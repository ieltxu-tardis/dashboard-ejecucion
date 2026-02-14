#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from memory_service.db import PostgresExec
from .config import load_config
from .approvals import ApprovalService


def build_service() -> ApprovalService:
    repo_root = str(Path(__file__).resolve().parents[1])
    return ApprovalService(PostgresExec(repo_root=repo_root), load_config())


def main() -> int:
    parser = argparse.ArgumentParser(prog="approvals")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list")
    p_list.add_argument("--status", default="pending", choices=["pending", "approved", "denied", "expired", "canceled", "all"])
    p_list.add_argument("--limit", type=int, default=50)

    p_show = sub.add_parser("show")
    p_show.add_argument("approval_id")

    p_approve = sub.add_parser("approve")
    p_approve.add_argument("approval_id")
    p_approve.add_argument("--reason", required=True)
    p_approve.add_argument("--by", dest="decided_by", default=load_config().approvals_admin_actor)

    p_deny = sub.add_parser("deny")
    p_deny.add_argument("approval_id")
    p_deny.add_argument("--reason", required=True)
    p_deny.add_argument("--by", dest="decided_by", default=load_config().approvals_admin_actor)

    p_exp = sub.add_parser("expire")

    args = parser.parse_args()
    svc = build_service()

    if args.cmd == "list":
        print(json.dumps(svc.list(status=args.status, limit=args.limit), ensure_ascii=False))
        return 0
    if args.cmd == "show":
        print(json.dumps(svc.show(args.approval_id), ensure_ascii=False))
        return 0
    if args.cmd == "approve":
        print(json.dumps(svc.decide(approval_id=args.approval_id, decision="approved", decided_by=args.decided_by, reason=args.reason), ensure_ascii=False))
        return 0
    if args.cmd == "deny":
        print(json.dumps(svc.decide(approval_id=args.approval_id, decision="denied", decided_by=args.decided_by, reason=args.reason), ensure_ascii=False))
        return 0
    if args.cmd == "expire":
        print(json.dumps({"expired": svc.expire_pending()}, ensure_ascii=False))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
