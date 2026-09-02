# Integration heuristics (Step 2, dimension c)

Read only at Step 2. A finding without `path:line` (or an identified CI job) does not enter the report.

This dimension covers **contracts, breaking changes, and side effects visible in the diff** — not style, not “ugly code”, not generic architecture.

## What counts as risk

Treat as a risk candidate if the diff (MCP in MR mode, or `git diff <merge-base>...<HEAD>` in branch mode) touches:

- Public signature: HTTP handler, RPC, event, job, CLI flag, package export.
- Schema: OpenAPI/Swagger, GraphQL SDL, JSON Schema, protobuf, exported types (`types`, `api`, `dto`, `client`).
- Persistence: migration, seed, column rename/drop, incompatible serializer.
- Authz/authn: middleware, guard, policy, scope, role.
- Feature flag / env: default changes behavior for anyone who did not update.
- UI↔backend contract: payload, query param, status code, new required field.
- Callers outside the MR: `Grep` the working tree for a removed/renamed symbol. An unupdated caller is evidence.
- CI: job `failed` / `canceled` in `gitlab_get_pipeline_jobs`. Name + status is enough; **do not** claim root cause without a log (there is no log tool).

## Breaking change (flag it)

- Remove or rename a field/endpoint/param without a version or feature flag.
- Tighten a type (optional → required, string → enum) without migrating callers.
- Change status-code / error semantics without updating the client.
- Irreversible migration or no mentioned rollback, if the diff shows only “up”.

Do not call breaking: an `internal`/`private` change with no external callers found; a refactor whose callers are in the same MR.

## Side effect

- Changed job/cron/worker: what runs in production besides the request path.
- Cache key / invalidation.
- Webhook / event publish.
- Config default.

Needs a one-sentence failure scenario (“if X in prod, then Y”). Without a scenario, do not list.

## What not to count (leave for `dev-mr-guided-review`)

- Naming, formatting, import-order nits.
- “I would have extracted a function”.
- A missing test **as a generic coverage nit**. It belongs here only if a **Jira criterion (a)** or a **broken contract (c)** has no assertion — and cite the criterion/contract.

## How to gather evidence (order)

1. MR diff (`includeDiffs` + local git if truncated) **or**, with no MR, `git diff <merge-base>...<HEAD>`.
2. `Grep` at the repo toplevel for removed/renamed symbols.
3. `gitlab_get_repository_file` on the source-branch `ref` for a neighboring contract **cited** in the diff and absent from the change set.
4. `gitlab_search` `scope: blobs` only if the diff shows rename/move and local Grep cannot find it.
5. CI: MR payload **or** `gitlab_list_pipelines` with `ref` = branch → `gitlab_get_pipeline` / `gitlab_get_pipeline_jobs` if there is a failure. No job log.

Do not run broad GitLab search (`gitlab_search` without a path/symbol). Do not infer “this probably breaks the mobile app” without a caller or contract in the repo/diff.
