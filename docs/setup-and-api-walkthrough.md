<!--
Copyright IBM Corp. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
-->

# Execute setup and diagnostics in Postman or Insomnia

[README](../README.md) · [Setup and explanations](setup.md) · [Collection coverage](collection-coverage.md)

Begin with [Setup](setup.md) for the complete first-time configuration. Use this guide when choosing Postman or Insomnia for the API steps.

## Choose one client and import the current files

| Client | Setup import | Runtime import |
|---|---|---|
| Postman | `api-clients/postman/uc2-ibm-verify-setup.postman_collection.json` | `api-clients/postman/uc2-runtime-diagnostics.postman_collection.json` |
| Insomnia | `api-clients/insomnia/uc2-ibm-verify-setup.insomnia.json` | `api-clients/insomnia/uc2-runtime-diagnostics.insomnia.json` |

Import the setup collection and the runtime collection for your chosen client. Do not run the entire collection: suspension and delete-scope denial are intentional negative tests, and ADT creation is optional when the type already exists.

Postman stores successful response values in **collection variables**. Remove conflicting environment variables with the same names. Insomnia uses the imported **Base Environment**: copy returned values there manually. Setup and runtime environments are independent; copy the required values into the runtime environment explicitly. Neither client populates the application's local `.env`. The local `STS_*` keys hold the Token Exchange application settings; keep these key names when copying values.

## Variable map

| Variable in either client | Source and purpose | Local `.env` equivalent |
|---|---|---|
| `tenant_url` | HTTPS tenant origin; no trailing slash | Tenant endpoint URLs |
| `admin_client_id`, `admin_client_secret` | Administrative API client with setup entitlements | Setup only |
| `admin_access_token` | Setup request 01 `access_token` | Setup only |
| `agent_id` | Setup request 02 registry `id` | `AGENT_ID` |
| `actor_client_id`, `actor_client_secret` | Setup request 03 OAuth credentials | `ACTOR_CLIENT_ID`, `ACTOR_CLIENT_SECRET` |
| `actor_application_id` | Runtime application's management ID from console | Setup only |
| `actor_access_token` | Setup request 08 `access_token` | Transient runtime input |
| `resource_client_id`, `resource_client_secret` | Client authorized to introspect the selected token | Diagnostics only |
| `subject_access_token` | Human access token obtained with Authorization Code + PKCE | Transient runtime input |
| `subject_resource_client_id`, `subject_resource_client_secret` | Client permitted to introspect the human token | Diagnostics only |
| `sts_client_id`, `sts_client_secret` | Token Exchange application credentials | `STS_CLIENT_ID`, `STS_CLIENT_SECRET` |
| `delegated_access_token` | Runtime request 05 or 07 `access_token` | Transient tool-call authority |
| `logged_in_subject` | Actual human username/email/sub used by the sample | Request context |
| `tool_name`, `course_id` | Intended operation; use `ALL` for listing | Request context |

Find `agent_id` in the agent details and `actor_application_id` in the application details or management URL. The setup guide shows where to obtain each value.

## Setup sequence and expected outputs

Complete [setup Step 1](setup.md#step-1--prepare-administrative-access), including `manageAppAccessAdmin`, before running request 01.

| Order | Request | Purpose | Check / save |
|---|---|---|---|
| 1 | 01 Get Admin Access Token | Authorize setup calls | HTTP 200; save `access_token` as `admin_access_token` |
| 2 | 02 Onboard Agent | Create the governed record | HTTP 201; save `id` as `agent_id` |
| 3 | 03 DCR Create UC2 Actor Client | Create runtime credentials | HTTP 201; save `client_id` and `client_secret` |
| 4 | 04 Get Agent Details | Read only this agent | HTTP 200; returned `id=agent_id` |
| 5 | 05 Associate Actor Application with Agent | Link credentials to agent identity | Set `actor_application_id` first; HTTP 204, no body |
| 6 | 06 Activate Agent, then 04 again | Establish lifecycle readiness | ACTIVE and association verified in console |
| 7 | 08 Get Actor Token | Obtain fresh runtime identity | HTTP 200; save `access_token` as `actor_access_token` |
| 8 | 10 Introspect Actor Token | Prove registry identity is in token | `active=true`, `sub=agent_id`, `client_id=actor_client_id` |

For request 10, supply introspection-authorized `resource_client_id`/secret. Your Token Exchange client can be used if your tenant permits it; a client credential pair is not automatically entitled to introspect every token. A 401/403 here is an introspection-access problem, not proof of an actor-sub mismatch.

Request 05 replaces application tags with the supplied array. Preserve any additional tags for an existing customized application. If it returns 403, add **Manage application lifecycle** to the administrative API client, obtain a fresh admin token and retry. An empty 204 response is expected and must not be parsed as JSON.

**Stop before runtime if request 10 does not show the registry AgentID in `sub`.** Review application association, purpose tag, ACTIVE status and token freshness.

## Shared console configuration

Follow setup Steps 4–6 in both client workflows:

1. Create/configure the human OIDC application: Authorization Code + PKCE, browser callback and test-user entitlements.
2. Under the human application's **Endpoint configuration → Introspect**, configure target attribute `may_act` with a custom rule whose resulting JSON is:

   ```json
   {"sub": "<registry-agent-id>"}
   ```

   Replace the placeholder with the AgentID returned by request 02 or shown in the agent details.
3. Register the ADT with request 09 only when absent. If UC1 already uses the same type, inspect/merge the MCP schema through the console instead of duplicating or breaking it.
4. Configure the Token Exchange application, JWT output, audience `course-mcp-server`, permitted scopes, ADT, consent mapping and test-user entitlements.
5. Keep **Skip default actor validation unchecked** for the supplied `may_act` path. If your tenant instead uses Actor Criteria, configure an explicit rule for the intended delegation and select the skip option only when deliberately replacing default validation. Do not enable unconditional delegation to bypass an error.

Also select **All users are entitled to this application** in the Token Exchange application's **Entitlements** tab. Then edit the agent's **Agent tasks**, select **Act on behalf of a user**, associate **UC2 Course MCP Agent Token Exchange**, and save. These console steps apply to both API clients.

## Obtain the actual human access token for manual testing

The browser sample obtains the subject token through sign-in. For separate API-client tests, use your client's **OAuth 2.0 Authorization Code + PKCE** helper:

1. Set authorize URL `<tenant>/oauth2/authorize`, token URL `<tenant>/oauth2/token`, human application's client ID/secret, scopes `openid profile email`, PKCE S256 and a fresh state.
2. Read the helper's callback URL in your installed client and add that exact URL to the human application before authorizing. Keep `http://localhost:8000/callback` registered for browser use.
3. Authenticate the intended human and obtain an **access token**. Do not substitute the ID token.
4. Copy that access token to runtime `subject_access_token`. Populate `logged_in_subject` using the same actual human identity used by the app.

After changing delegation configuration, obtain fresh tokens and sign in again. A separate API-client token does not prove which older token is held by an already running browser session.

## Runtime sequence

Set runtime `agent_id`, `actor_client_id`, fresh `actor_access_token`, human `subject_access_token`, `sts_client_id`, `sts_client_secret`, `tenant_url` and `logged_in_subject`.

1. Run **01 Application Health** and **02 MCP tools/list through client**. Expect four tools; discovery grants no execution rights.
2. Run **06 Introspect Subject Token and may_act** with the subject introspection credentials. Expect `active=true` and `may_act.sub=agent_id` for this guide's delegation path.
3. Set `tool_name=list_available_courses` and `course_id=ALL`. Run **05 Token Exchange for Selected MCP Tool**. Expect HTTP 200. Postman saves the returned token; in Insomnia copy `access_token` to `delegated_access_token`.
4. Run **04 Introspect Delegated Token as MCP Resource** using authorized resource credentials. Expect `active=true`, `act.sub=agent_id`, the MCP audience, `mcp.tools.invoke course.read` and matching authorization details.
5. Run **03 MCP tools/call through client**. Expect the approved operation to succeed.
6. Repeat with `tool_name=enroll_course` and an actual `course_id`, such as `SEC-301`, obtaining a new delegated token for the changed operation. Then use `list_enrolled_courses` with `ALL` and a fresh read token.

The supplied mapping derives delegated scopes from the requested operation. The request payload uses `actor_client_id` for `creator`.

## Optional negative tests and recovery

- **Missing delete authority:** run runtime 07, then 08 using its new token. Expected resource denial is HTTP 403, `denied_stage=scope`, missing `course.delete`. The supplied mapping does not grant that scope. If Token Exchange denies issuance instead, record that earlier stage and do not claim a resource-scope test passed.
- **Cross-user request:** use the browser test in the runtime guide. Named-user lookup requires `readUsers`; lookup success does not grant cross-user access.
- **Suspension:** run setup 07 only after a working ACTIVE test, then setup 04 and a fresh runtime token request. Record the stage Verify denies. Reactivate with setup 06, verify with 04 and obtain fresh tokens. Previously issued JWTs may still pass offline validation until expiry.

## API request reference

Open a request's description for its purpose and expected result. The [API request reference](collection-coverage.md) lists every operation. Postman checks responses in the Tests tab; in Insomnia compare the response to the expected fields in the table.
