# Security policy

## Supported release

The actively maintained research-artifact line is `0.4.x`.

## Security boundary

PipelineProof executes candidate code. Docker mode reduces the candidate execution surface through network isolation, read-only mounts, an unprivileged user, dropped capabilities, resource limits, and `no-new-privileges`, but it is not presented as a formally verified sandbox or an absolute hostile-code security boundary.

Local mode is for development and debugging only. Do not use local mode to execute untrusted third-party submissions.

See `docs/THREAT_MODEL.md` for the benchmark trust model and residual risks.

## Reporting a vulnerability

Do not publish working sandbox escapes, credential-exposure paths, or other sensitive exploit details in a public issue.

Use GitHub's private vulnerability-reporting or Security Advisory interface for this repository when available. If that interface is unavailable, open a public issue containing only a request for a private security contact and no exploit details.

Useful reports include:

- affected PipelineProof version or commit;
- execution mode;
- operating system and Docker version when relevant;
- minimal reproduction conditions;
- expected and observed security boundary;
- whether network, filesystem, process, or verifier isolation is affected.

## Benchmark attacks versus security vulnerabilities

A candidate that fools a benchmark detector is not automatically a sandbox vulnerability. Report verifier-gaming cases through ordinary benchmark issues unless they cross the execution/security boundary.

Conversely, a sandbox escape or exposure of held-back verifier material should be treated as a security issue even if it does not increase benchmark reward.
