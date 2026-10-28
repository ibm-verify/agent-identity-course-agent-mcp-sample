<!--
Copyright IBM Corp. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
-->

# API request reference

[Setup](setup.md) · [Postman and Insomnia walkthrough](setup-and-api-walkthrough.md)

The same numbered requests are available in Postman and Insomnia. Each request description explains its purpose and expected response. Postman saves selected response values automatically; copy them into the Base Environment in Insomnia.

| Collection | Request | Expected check |
|---|---|---|
| Setup | 01 - Get Admin Access Token | HTTP 200; copy access_token to admin_access_token. If 401, check this client ID/secret. After entitlement changes obtain a fresh token. |
| Setup | 02 - Onboard Agent | HTTP 201; copy id to agent_id. Expected name: UC2 Course MCP Conversational Agent. Reuse an existing record instead of creating duplicates. |
| Setup | 03 - DCR - Create UC2 Actor Client | HTTP 201; copy client_id and client_secret to actor_client_id and actor_client_secret. This client_id is not the AgentID. |
| Setup | 04 - Get Agent Details | HTTP 200; id must equal agent_id. Repeat after activation/suspension. Verify application association in the console. |
| Setup | 05 - Associate Actor Application with Agent | HTTP 204 with no body. actor_application_id is the application management ID. Requires manageAppAccessAdmin. Replaces tags: preserve other tags on customized applications. Verify association in Identity & authentication. |
| Setup | 06 - Activate Agent | HTTP 200; rerun 04 and confirm ACTIVE and association. Obtain a fresh actor token. Preserve customized metadata when adapting lifecycle PUT. |
| Setup | 07 - Suspend Agent | HTTP 200; rerun 04. Record the actual denial stage in a new token request. Reactivate with 06. Previously issued JWTs may remain usable until expiry. |
| Setup | 08 - Get Actor Token | HTTP 200; copy access_token to actor_access_token; run 10. actor sub must be the registry agent_id, not actor_client_id. |
| Setup | 09 - Register MCP ADT | HTTP 201. If type exists, inspect/update via console; do not duplicate it; keep the separate UC1 type unchanged. See payloads/mcp_tool_action_adt_schema.json. |
| Setup | 10 - Introspect Actor Token | HTTP 200; active=true, sub=agent_id, client_id=actor_client_id. Use a client authorized to introspect this token (resource_client_id/secret; your Token Exchange client may be permitted). Configure subject may_act.sub=agent_id, keep human sub unchanged. |
| Runtime | 01 - Application Health | HTTP 200. If unavailable check localhost:8000 and the uvicorn terminal. |
| Runtime | 02 - MCP tools/list through client | HTTP 200; four tools including the intentional delete negative-test tool. Discovery grants no authority. |
| Runtime | 03 - MCP tools/call through client | HTTP 200 for an allowed matching request; verify business result. Use the token from 05 for the same tool/course/subject. |
| Runtime | 04 - Introspect Delegated Token as MCP Resource | HTTP 200; active=true; act.sub=agent_id; audience contains course-mcp-server; check scope and authorization_details. |
| Runtime | 05 - Token Exchange for Selected MCP Tool | HTTP 200; copy access_token to delegated_access_token. Match tool_name, course_id and logged_in_subject. RAR creator must equal agent_id. |
| Runtime | 06 - Introspect Subject Token and may_act | HTTP 200; active=true; may_act.sub=agent_id for the supplied may_act route. The human own sub stays the human identity. If using Actor Criteria instead, inspect that explicit rule and Skip default actor validation. |
| Runtime | 07 - Token Exchange for Delete - No Delete Scope | HTTP 200 only if policy permits issuance; expected scope excludes course.delete. Copy returned access_token, then run 08. A policy denial at Token Exchange is a different observed stage. |
| Runtime | 08 - Invoke Delete - Expect Scope Denial | HTTP 403 with denied_stage=scope and reason mentioning course.delete. No data should be deleted with the supplied mapping. |

## Console configuration

Configure human sign-in, delegation, user entitlements and the Token Exchange consent mapping in the console as described in the setup guide. Under the agent's **Agent tasks**, associate the Token Exchange application with **Act on behalf of a user**.

For Token Exchange requests, use the credentials saved as `STS_CLIENT_ID` and `STS_CLIENT_SECRET` in the application's `.env`.
