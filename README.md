# host-yarn-bridge

Allowlisted host-local bridge for RND#11 YaRN degradation curve.

- `POST /v1/run` — fixed body only (operation/host/seat/artifact_root/request_timeout_seconds)
- `GET /healthz` — liveness
- Rejects `command`/`image`/`task`
- One-run flock; redacts secrets in logs
- Writes `STEP4-CURVE.md` + `STEP4-CURVE-METRICS.json` under the allowlisted artifact root

## Run

```bash
HOST_YARN_PORT=8099 python -m host_yarn_bridge.app
```

Worker reaches this via `HOST_LOCAL_YARN_BRIDGE_URL=http://192.168.50.187:8099`.
