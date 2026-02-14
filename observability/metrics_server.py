#!/usr/bin/env python3
from __future__ import annotations

import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from memory_service.db import PostgresExec

HOST = os.getenv("METRICS_HOST", "127.0.0.1")
PORT = int(os.getenv("METRICS_PORT", "9464"))


def _line(name: str, value: float, labels: dict[str, str] | None = None) -> str:
    if labels:
        l = ",".join(f'{k}="{v}"' for k, v in labels.items())
        return f"{name}{{{l}}} {value}"
    return f"{name} {value}"


def render_metrics() -> str:
    db = PostgresExec(repo_root=str(Path(__file__).resolve().parents[1]))

    lines = []
    lines.append("# HELP openclaw_requests_total Synthetic request counter by component/route/status class")
    lines.append("# TYPE openclaw_requests_total counter")
    for row in db.fetchall_json("""
        SELECT component, COALESCE(route,'internal') as route,
               COALESCE(outcome,'2xx') as status_class,
               COUNT(*)::float AS c
        FROM observability_events
        WHERE event_type IN ('request','semantic_search','job_process')
        GROUP BY component, route, status_class
    """):
        lines.append(_line("openclaw_requests_total", row["c"], {"component": row["component"], "route": row["route"], "status_class": row["status_class"]}))

    lines.append("# HELP openclaw_request_latency_seconds Request latency")
    lines.append("# TYPE openclaw_request_latency_seconds gauge")
    for row in db.fetchall_json("""
        SELECT component, COALESCE(route,'internal') as route,
               COALESCE(AVG(latency_ms),0)::float/1000.0 AS sec
        FROM observability_events
        WHERE latency_ms IS NOT NULL
        GROUP BY component, route
    """):
        lines.append(_line("openclaw_request_latency_seconds", row["sec"], {"component": row["component"], "route": row["route"]}))

    lines.append("# HELP openclaw_errors_total Errors by component and error code")
    lines.append("# TYPE openclaw_errors_total counter")
    for row in db.fetchall_json("""
        SELECT component, COALESCE(error_code,'unknown') AS error_code, COUNT(*)::float AS c
        FROM observability_events
        WHERE outcome='error'
        GROUP BY component, error_code
    """):
        lines.append(_line("openclaw_errors_total", row["c"], {"component": row["component"], "error_code": row["error_code"]}))

    lines.append("# HELP openclaw_policy_denied_total Policy denies by reason")
    lines.append("# TYPE openclaw_policy_denied_total counter")
    for row in db.fetchall_json("""
        SELECT COALESCE(error_code,'unknown') AS reason, COUNT(*)::float AS c
        FROM observability_events
        WHERE event_type='policy_denied'
        GROUP BY reason
    """):
        lines.append(_line("openclaw_policy_denied_total", row["c"], {"reason": row["reason"]}))

    lines.append("# HELP openclaw_jobs_enqueued_total Jobs enqueued")
    lines.append("# TYPE openclaw_jobs_enqueued_total counter")
    for row in db.fetchall_json("SELECT type AS job_type, COUNT(*)::float AS c FROM jobs GROUP BY type"):
        lines.append(_line("openclaw_jobs_enqueued_total", row["c"], {"job_type": row["job_type"]}))

    lines.append("# HELP openclaw_jobs_processed_total Jobs processed by outcome")
    lines.append("# TYPE openclaw_jobs_processed_total counter")
    for row in db.fetchall_json("SELECT job_type, status AS outcome, COUNT(*)::float AS c FROM job_runs GROUP BY job_type,status"):
        lines.append(_line("openclaw_jobs_processed_total", row["c"], {"job_type": row["job_type"], "outcome": row["outcome"]}))

    lines.append("# HELP openclaw_job_duration_seconds Average job duration")
    lines.append("# TYPE openclaw_job_duration_seconds gauge")
    for row in db.fetchall_json("""
        SELECT job_type,
               COALESCE(AVG(EXTRACT(EPOCH FROM (ended_at-started_at))),0)::float AS sec
        FROM job_runs
        GROUP BY job_type
    """):
        lines.append(_line("openclaw_job_duration_seconds", row["sec"], {"job_type": row["job_type"]}))

    depth = db.fetchone_value("SELECT COUNT(*)::text FROM jobs WHERE status='queued'") or "0"
    lines.append("# HELP openclaw_queue_depth Current queued jobs")
    lines.append("# TYPE openclaw_queue_depth gauge")
    lines.append(_line("openclaw_queue_depth", float(depth)))

    lines.append("# HELP openclaw_job_lag_seconds Oldest queued lag by job_type")
    lines.append("# TYPE openclaw_job_lag_seconds gauge")
    for row in db.fetchall_json("""
        SELECT type AS job_type,
               COALESCE(MAX(EXTRACT(EPOCH FROM (NOW()-scheduled_at))),0)::float AS lag
        FROM jobs WHERE status='queued' GROUP BY type
    """):
        lines.append(_line("openclaw_job_lag_seconds", row["lag"], {"job_type": row["job_type"]}))

    lines.append("# HELP openclaw_embeddings_generated_total Generated embeddings rows")
    lines.append("# TYPE openclaw_embeddings_generated_total counter")
    for row in db.fetchall_json("SELECT model, COUNT(*)::float AS c FROM embeddings GROUP BY model"):
        lines.append(_line("openclaw_embeddings_generated_total", row["c"], {"model": row["model"]}))

    lines.append("# HELP openclaw_semantic_search_queries_total Semantic search queries")
    lines.append("# TYPE openclaw_semantic_search_queries_total counter")
    q = db.fetchone_value("SELECT COUNT(*)::text FROM observability_events WHERE event_type='semantic_search'") or "0"
    lines.append(_line("openclaw_semantic_search_queries_total", float(q)))

    lines.append("# HELP openclaw_semantic_search_hits_total Semantic search hits")
    lines.append("# TYPE openclaw_semantic_search_hits_total counter")
    h = db.fetchone_value("SELECT COALESCE(SUM(value_num),0)::text FROM observability_events WHERE event_type='semantic_search'") or "0"
    lines.append(_line("openclaw_semantic_search_hits_total", float(h)))

    return "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/metrics":
            self.send_response(404)
            self.end_headers()
            return
        body = render_metrics().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), Handler)
    print(f"metrics_server listening on http://{HOST}:{PORT}/metrics", flush=True)
    server.serve_forever()
