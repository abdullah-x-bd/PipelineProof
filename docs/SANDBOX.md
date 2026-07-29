# Sandbox

## Development mode

`local` mode runs each command in a separate process group with:

- Wall timeout
- CPU limit
- Address-space limit
- File-size limit
- File-descriptor limit
- Process limit
- Output limit
- Restricted environment variables

It does not isolate the host filesystem or network.

## Scored mode

Build the task image:

```bash
docker build -f docker/task.Dockerfile -t pipelineproof-task:0.3.0 .
```

Run verification with `--mode docker`.

Docker mode declares:

- Network disabled
- Read-only root filesystem
- Read-only candidate mount
- Writable scratch mount only
- Unprivileged user
- All Linux capabilities dropped
- `no-new-privileges`
- CPU, memory, process, wall-time, and output limits

The worker image contains NumPy, Pytest, and the execution worker. It does not install the `pipelineproof` package, so candidate code cannot import verifier modules through the normal Python path.
