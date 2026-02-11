
## 2026-02-06 03:11 UTC - Low queue burst catch-up fix
- Issue targeted: video starts late then accelerates/catches up (micro-freeze effect) while audio remains fluid.
- Root cause confirmed: in `sdk_ingest_runner.py`, low queue branch (`queue_depth <= min_depth`) disabled pacing sleep (`next_chunk_time = now`), causing burst chunk emission.
- TDD:
  - Added failing test `infra/avatar/tests/local/test_sdk_pacing_guard.py::test_low_queue_depth_does_not_disable_chunk_pacing`.
  - Before fix: min inter-chunk interval ~0.1ms (fails `>=20ms` assertion).
  - After fix: test passes.
- Code change:
  - `infra/avatar/webrtc/streamer/sdk_ingest_runner.py`
  - Replaced low-queue fast-loop with normal paced scheduling (`_pace_chunk(t_start)`).
- Verification run:
  - `pytest -q infra/avatar/tests/local/test_sdk_pacing_guard.py -k low_queue_depth_does_not_disable_chunk_pacing`
  - `pytest -q infra/avatar/tests/local/test_sdk_pacing_guard.py -k "zero_frame_runs_are_paced or livekit_input_pace_keeps_output_pacing"`
- Deploy:
  - Redeployed streamer using `./skills/redeploy-streamer/scripts/redeploy_streamer.sh`.
  - Remote code verified includes comment: `Queue is low: keep cadence to avoid bursty video catch-up`.
  - Service active timestamp: `Fri 2026-02-06 03:09:13 UTC`.
- Observed runtime note:
  - Streamer logs still show repeated `Metrics payload too large (...)` warnings for long-lived session `sess_91496bbf46844e2f`.
