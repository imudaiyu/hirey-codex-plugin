---
name: hi-repair
description: Use the existing Product Signal and Repair Case operations through workspace_workflows for a bounded bug report, diagnosis, repair run, reviewable pull request, release evidence, and reporter verification.
---

# Hi Repair

Use `workspace_workflows`; call `action: catalog` first and follow the live definitions for the
existing `product_signal.*` and `repair.*` operations.

- Reporter: `product_signal.submit`, then `product_signal.get`; use
  `product_signal.verify_repair` only after the release asks the reporter to verify.
- Authorized Product Signals staff: triage the signal and create a separate Problem Case with
  `repair.case.create`.
- Repair worker: use only a current `repair.grant.*` authority and an exclusive
  `repair.run.claim`; keep the lease with `repair.run.heartbeat`, attach bounded evidence, and end
  with `repair.run.finish`.
- Release operator: review and merge outside the repair worker, deploy explicitly, and advance the
  recorded release only with typed evidence through `repair.release.advance`.

Every write needs a stable `idempotency_key`. Operations marked for explicit confirmation need the
user's approval and the exact confirmation object. A repair worker does not gain merge, deploy, or
production authority from a Repair Grant.
