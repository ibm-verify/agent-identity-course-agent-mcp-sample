<!--
Copyright IBM Corp. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
-->

# Run, verify and troubleshoot UC2

[README](../README.md) · [Setup](setup.md) · [API clients](setup-and-api-walkthrough.md)

## Before the demo

Complete setup Steps 1–8. Set `AGENT_ID` to the ID shown in the agent details. Restart the application and sign in again after configuration changes.

```bash
curl --show-error --fail http://localhost:8000/health
curl --show-error --fail http://localhost:8000/mcp/tools
python tools/diagnose_runtime.py
```

Tool discovery should include `list_available_courses`, `list_enrolled_courses`, `enroll_course` and `delete_course_history`. The last is an intentional missing-scope demonstration. The app starts the STDIO MCP subprocess; do not start a separate server for the default path.

## Demo and evidence

| Test | Prompt / action | Expected result and reason |
|---|---|---|
| Read catalog | “Show me the available courses.” | Returns courses after delegation and MCP validation; requires read scope |
| Enroll self | “Enroll me in Advanced Security Operations.” | Enrolls the signed-in user for the approved course; requires enroll scope |
| Read enrollments | “Show my enrolled courses.” | Shows that user's enrollment result, including local persisted writes |
| Cross-user | Ask for an existing different user's enrollments | Denied by the sample's self-service boundary; directory lookup alone does not grant authority |
| Delete scope | Use runtime collection requests 07 then 08 | Missing `course.delete` is denied at the resource when Token Exchange issued the test token |
| Suspend / restore | Setup request 07, read status, then fresh operation; restore with 06 | Record the fresh-request denial stage; after ACTIVE and fresh tokens, repeat the success |

Use an actual course returned by the catalog. Diagnose lookup errors separately from authorization denial. Local enrollment writes persist in SQLite across MCP subprocesses; static example fixtures are separate demo data.

## Debug by the first failed stage

| Symptom | Likely area | Fast check / recovery |
|---|---|---|
| `dquote>` | Shell quoting | Ctrl+C; close the Authorization-header quote |
| HTTP 301 | Tenant URL / redirect | Use `https://` tenant origin; do not treat redirect as creation success |
| Admin token length 0 | Failed request or export | Reacquire admin token with exact HTTP 200 before extracting it |
| HTTP 401 at token endpoint | Client authentication | Verify correct administrative/actor/Token Exchange client ID and secret for that request |
| Generic HTML 400 / Authorization Error | Front-end authorization or request handling | Check nonempty bearer token and HTTPS; inspect response body, not headers alone |
| PATCH HTTP 403, `CSIAK4300E` | Administrative entitlement | Add `manageAppAccessAdmin` to the API client, obtain fresh admin token, retry |
| PATCH HTTP 204, empty body | Expected association success | Verify association in console; do not parse empty body as JSON |
| `CSIAQ5201E` | Verify delegation | Compare actor `sub` with subject `may_act.sub`; check Actor Criteria, default validation and permitted subject applications |
| `Invalid actor. Expected ...` | Local resource check | Set `.env` `AGENT_ID`; confirm new gateway code and process; compare delegated `act.sub` |
| `AGENT_ID is not configured` | Local `.env` | Fill registry ID; shell exports can override `.env`; restart |
| `invalid_authorization_details` | ADT schema / attached type | Compare actual RAR with exact packaged schema, including MCP fields |
| Audience / scope denial | Token Exchange mapping or resource configuration | Inspect delegated `aud`, scope and approved operation; do not broaden scopes to bypass the check |
| Tool/action/course mismatch | Token reused for another operation | Obtain new delegated authority for the exact tool and course |
| Introspection 401/403 | Introspection client permission | Use a client authorized to inspect that token; do not infer token contents from failure |
| Old error after editing | Running old checkout/process | Stop uvicorn, start `python -m uvicorn` in this project, sign in again |

Run `python tools/diagnose_runtime.py` to print non-secret effective configuration and selected actor-introspection fields. It uses your existing `.env`, requests a fresh actor token and introspects with Token Exchange credentials. If that client lacks introspection permission, use the API collection with authorized resource credentials. Share selected claims and error codes; do not share tokens, secrets or cookies.

For a remaining delegation error, also provide: Actor Criteria expression, Skip default actor validation state, permitted subject application list, and subject may_act mapping. The script's fresh token is not evidence of the browser session's older subject token.

## Review audit activity

Follow [Audit course listing and enrollment](audit.md) to identify the agent, user, requested tool and granted permissions in Verify token events.

## Working boundaries

The normal path is local STDIO with `MCP_FORWARD_TO_COURSE_API=false`. Delegated output must be JWT for local signature/JWKS validation; opaque human access tokens are supported as Token Exchange inputs. Offline JWT validation does not automatically revoke every previously issued token on suspension.

Keep `ALLOW_LOCAL_UNSIGNED_JWT=false`. The optional LLM classifies intent but does not grant authority. For a first run use `USE_LLM=false`; enable Gemini after the Verify/MCP path succeeds. Existing working LLM settings can be retained.
