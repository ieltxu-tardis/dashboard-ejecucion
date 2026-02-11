# NTRVSTA Streamer Debug

Goal: stabilize lip-sync (no idle mouth motion, no stutter/freezes) and identify root cause.

Status (2026-01-31)
- Added GPU live-ingest replay test: `infra/avatar/tests/gpu/test_streamsdk_live_replay.py`.
- Test passes on dump `sess_4baef8891e6b4fb0_1769800995964` after matching 512x512 frames.
- Offline replay test already passes; remaining failures are likely session-specific in live ingestion/pacing.

Key paths
- `infra/avatar/webrtc/streamer/conversational/livekit_agent.py`
- `infra/avatar/webrtc/streamer/sdk_ingest_runner.py`
- `infra/avatar/tests/gpu/test_streamsdk_live_replay.py`
- `docs/STREAMER_DEBUG_LOG.md`

Next steps
- Run live-ingest replay test against a failing session dump to see if it reproduces.
- If it fails, use response_end timing and lipsync budget logs to pinpoint the stall stage.
- If it passes, inspect runtime config and pacing differences vs live sessions.
