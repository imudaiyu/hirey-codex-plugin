---
name: hi-repair
description: Run HiRey's root-cause-first bug repair workflow with Product Signals, case-scoped Repair Grants, exclusive leases, evidence, and reviewable pull requests. Use when somebody reports a bug, Product Signals staff need to admit or assign a Problem Case, a local Codex or Claude Code worker should process an assigned repair, Walter wants a PR-ready repair without automatic deployment, or the original reporter needs to verify whether a released fix solved the symptom.
---

# Hi Repair

Turn a report into a bounded investigation and a reviewable PR without giving the reporter repository access or letting an autonomous worker claim deployment authority.

## Choose the lane

- Reporter: use `product_signals` to `submit`, later `get`, and only call `verify_repair` after `repair.status=live_please_verify`.
- Product Signals staff: triage evidence, create a separate Problem Case, and create/revoke case-scoped grants.
- Repair worker: operate only through an active grant and lease; stop at a PR or an explicit blocked result.
- Walter/release operator: review, merge, manually deploy, attach release truth, and ask the original reporter to retry. These actions are not delegated to the worker.

If the `product_signals` or `repair_cases` tools are missing or return authentication errors, use `hi-onboard`. Never ask for or share Walter's OpenAI/ChatGPT token. A local Codex scheduled task uses the signed-in Codex plan for model work; the Hi bearer only authorizes HiRey data.

## Intake and admission

1. Preserve observed facts with `product_signals(action="submit")`. Split independent symptoms and use a stable idempotency key.
2. Staff reads `product_signals(action="list", scope="company", statuses=["needs_triage"])` and makes explicit one-field decisions through `repair_cases(action="triage_signal")`.
3. Do not send external text straight into a code repository. First define an observable `failure_contract` and create a Problem Case with `repair_cases(action="create_problem_case")`.
4. Keep source signals immutable. Put hypotheses, causal claims, and engineering evidence on the Problem Case.
5. Risk classes other than `normal` are human-controlled. Do not place identity/consent, PII/security, notification/outbox, schema migration, cross-repository contract, or deployment-mechanism cases into the autonomous lane.

## Grant access

Use `repair_cases(action="create_grant")` with:

- `read_pack` always;
- only the additional capabilities required: `claim`, `investigate`, `link_evidence`, `submit_pr`;
- an exact lowercase GitHub `owner/name` repository allowlist;
- a short expiry when appropriate.

For another person, deliver the one-time `claim_code` privately; they redeem it while signed into their own Hi identity. The code is shown once and is not a reusable credential. For Walter's scheduled local worker, use `bind_to_self=true`. Revoke the grant immediately when access is no longer needed.

## Process one repair

A scheduled or interactive run handles at most one case:

1. Call `repair_cases(action="list_grants", scope="mine")`, then `get_pack` for one active grant. A Walter/staff worker may also inspect `repair_cases(action="inbox")` and create a self-bound grant for one already-admitted normal case.
2. Confirm `risk_class=normal`, the repository is allowed, and the pack contains a concrete failure contract. Otherwise stop and report what staff must decide.
3. Call `claim` with the exact repository and `agent_kind=codex|claude_code`. Keep the returned lease token private and call `heartbeat` during longer work.
4. In the repository, read its instructions, check open PR/work ownership, and create an isolated branch/worktree from the canonical remote base. Do not work in a stale parking tree.
5. Reproduce before changing code. Record bounded reproduction/runtime evidence with `add_evidence`; never upload raw secrets, contact data, or provider payloads.
6. Establish all three causal fields before claiming a verified root cause:
   - `first_bad_state`: the earliest state that becomes wrong;
   - `violated_invariant`: the rule that should still hold there;
   - `causal_chain`: concrete steps from that state to the reported symptom.
7. Call `update_analysis` using the latest revision. A plausible explanation is a hypothesis; use `root_cause_status=verified` only with reproducible evidence.
8. Implement the smallest durable correction and a regression guard. Run the repository's required checks and attach code/test/regression references with `add_evidence`.
9. Push a correctly prefixed branch and open a reviewable PR. Call `submit_pr` with the exact GitHub PR URL, branch, and concise root-cause summary.
10. Stop. A PR or green CI is not deployed. Do not merge, dispatch deployment, add `deploy_receipt`/`production_verification`, or mark the case resolved.

If the lease conflicts, refresh the grant list instead of working concurrently. If the evidence is insufficient, the repository is out of scope, or risk becomes non-normal, call `release` with a precise `blocked_reason`.

### Staff scheduled admission

If no assigned/admitted case is eligible, Walter's staff worker may inspect at most one `needs_triage` Product Signal. Admit it only when it is a concrete bug with an observable expected/actual contract, enough bounded evidence to identify the repository, no unresolved duplicate, and no high-risk class. Make one audited status decision (`accepted`), create the separate Problem Case, then create a self-bound grant. Never invent P0-P3. If expected behavior, duplication, repository, or risk is unclear, leave the signal in triage and report the single decision Walter must make.

## Release and reporter confirmation

Walter reviews the causal claim, regression guard, diff, and checks. Deployment follows the repository's own release discipline. Only after a real deploy receipt and production verification may the release side mark the case monitoring/resolved.

When `product_signals(action="get")` shows `repair.status=live_please_verify`, ask the original reporter to retry the original symptom:

- `works_now` records reporter confirmation;
- `still_broken` reopens investigation without rewriting the original report.

Reporter confirmation is valuable evidence but never replaces production verification. Report status truthfully as `PR open`, `merged, unreleased`, or `deployed and verified`.

## Scheduled task prompt

Use this task prompt on Walter's Mac:

> Use $hi-repair to inspect my assigned Repair Grants and process at most one eligible normal-risk case. If none is assigned, inspect the staff repair inbox; if still empty, admit at most one concrete, non-duplicate, normal-risk needs-triage bug whose expected behavior and repository are clear, then create a self-bound grant. Work in an isolated worktree, prove the root cause, add a regression guard, and stop after opening and recording a reviewable PR. Never invent priority, merge, or deploy. If nothing is eligible, report that briefly; if blocked or high risk, record the exact reason for Walter.

The Mac must be on and Codex must be running for local scheduled tasks. Prefer an isolated worktree and narrow workspace-write permissions.
