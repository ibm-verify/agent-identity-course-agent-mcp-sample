<!--
Copyright IBM Corp. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
-->

# Run UC2 with cURL

[Setup](setup.md) · [Audit](audit.md) · [Postman and Insomnia](setup-and-api-walkthrough.md)

Start with [Setup](setup.md) for the complete first-time configuration. Use this walkthrough for the corresponding direct cURL commands. It does not require the setup helper. Complete the application, delegation and entitlement configuration described in the setup guide. Postman or Insomnia can be used for the equivalent requests.

Run commands from the project folder in one terminal. At each step, continue only after the expected HTTP status and required response fields are present.

## 1. Obtain an administrative token

```bash
export TENANT='https://<tenantname>'
export ADMIN_CLIENT_ID='PASTE_ADMIN_CLIENT_ID'
export ADMIN_CLIENT_SECRET='PASTE_ADMIN_CLIENT_SECRET'
mkdir -p .local
chmod 700 .local
umask 077

curl --silent --show-error --fail-with-body \
  -X POST "$TENANT/oauth2/token" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'grant_type=client_credentials' \
  --data-urlencode "client_id=$ADMIN_CLIENT_ID" \
  --data-urlencode "client_secret=$ADMIN_CLIENT_SECRET" \
  -o .local/admin-token.json -w 'HTTP %{http_code}\n'
```

Expected: **200**. Then capture the token:

```bash
export ADMIN_ACCESS_TOKEN="$(jq -er '.access_token | select(type == "string" and length > 0)' .local/admin-token.json)"
```

A redirect such as 301 is not success. Confirm the tenant URL starts with `https://`. Do not extract values from an unexpected response.

## 2. Create the agent and runtime OAuth application

```bash
curl --silent --show-error --fail-with-body \
  -X POST "$TENANT/v1.0/Agents" \
  -H "Authorization: Bearer $ADMIN_ACCESS_TOKEN" \
  -H 'Accept: application/scim+json' \
  -H 'Content-Type: application/scim+json' \
  --data-binary @curl/payloads/course-mcp-agent.json \
  -o .local/agent-created.json -w 'HTTP %{http_code}\n'
```

Expected: **201**. Capture the AgentID and check the name:

```bash
export AGENT_ID="$(jq -er '.id | select(type == "string" and length > 0)' .local/agent-created.json)"
jq '{id,displayName,status}' .local/agent-created.json

curl --silent --show-error --fail-with-body \
  -X POST "$TENANT/oauth2/register" \
  -H "Authorization: Bearer $ADMIN_ACCESS_TOKEN" \
  -H 'Content-Type: application/json' \
  --data-binary @curl/payloads/actor-client-dcr.json \
  -o .local/actor-created.json -w 'HTTP %{http_code}\n'
```

Expected: **201**. Capture the runtime credentials:

```bash
export ACTOR_CLIENT_ID="$(jq -er '.client_id | select(type == "string" and length > 0)' .local/actor-created.json)"
export ACTOR_CLIENT_SECRET="$(jq -er '.client_secret | select(type == "string" and length > 0)' .local/actor-created.json)"
```

## 3. Associate and activate

Find the runtime application's management ID using [setup Step 3](setup.md#find-the-application-id).

```bash
export ACTOR_APPLICATION_ID='PASTE_APPLICATION_MANAGEMENT_ID'
jq --arg agent_id "$AGENT_ID" \
  'map(if .path == "/providers/oidc/properties" then .value.entityId = $agent_id else . end)' \
  curl/payloads/actor-application-associate.json > .local/actor-associate.json

curl --silent --show-error --fail-with-body \
  -X PATCH "$TENANT/v1.0/applications/$ACTOR_APPLICATION_ID" \
  -H "Authorization: Bearer $ADMIN_ACCESS_TOKEN" \
  -H 'Content-Type: application/json-patch+json' \
  --data-binary @.local/actor-associate.json \
  -o .local/association-response.json -w 'HTTP %{http_code}\n'
```

Expected: **204**, with no body. The supplied payload replaces application tags; retain additional tags when adapting an existing application. This request requires **Manage application lifecycle** on the administrative API client.

```bash
curl --silent --show-error --fail-with-body \
  -X PUT "$TENANT/v1.0/Agents/$AGENT_ID" \
  -H "Authorization: Bearer $ADMIN_ACCESS_TOKEN" \
  -H 'Accept: application/scim+json' -H 'Content-Type: application/scim+json' \
  --data-binary @curl/payloads/course-mcp-agent-activate.json \
  -o .local/agent-activated.json -w 'HTTP %{http_code}\n'
```

Expected: **200**. Read the specific agent:

```bash
curl --silent --show-error --fail-with-body \
  "$TENANT/v1.0/Agents/$AGENT_ID" \
  -H "Authorization: Bearer $ADMIN_ACCESS_TOKEN" \
  -H 'Accept: application/scim+json' \
  -o .local/agent-current.json -w 'HTTP %{http_code}\n'
jq '{id,displayName,status,oauthClients}' .local/agent-current.json
```

Expected: **200**, ACTIVE and the runtime application association verified in the console.

## 4. Register the authorization detail type

For a new type:

```bash
curl --silent --show-error --fail-with-body \
  -X POST "$TENANT/v1.0/auth-detail-types" \
  -H "Authorization: Bearer $ADMIN_ACCESS_TOKEN" \
  -H 'Content-Type: application/json' \
  --data-binary @payloads/mcp_tool_action_adt_registration.json \
  -o .local/adt-created.json -w 'HTTP %{http_code}\n'
```

Expected: **201**. If the type already exists, inspect and update its schema in the console as described in setup Step 5.

## 5. Complete the shared console settings

Follow setup Steps 4–7 to configure user sign-in, the AgentID delegation mapping, Token Exchange JWT output, audience, scopes, consent mapping and application entitlements. Under **Agent tasks → Act on behalf of a user**, select the Token Exchange application. Populate the local `.env`.

These configuration steps use the Verify console in this tutorial. The cURL requests below test the resulting flow.

## 6. Obtain a fresh actor token

```bash
# Token Exchange application settings.
# Keep the STS_* variable names; the application reads these keys.
export STS_CLIENT_ID='PASTE_TOKEN_EXCHANGE_CLIENT_ID'
export STS_CLIENT_SECRET='PASTE_TOKEN_EXCHANGE_CLIENT_SECRET'

curl --silent --show-error --fail-with-body \
  -X POST "$TENANT/oauth2/token" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'grant_type=client_credentials' \
  --data-urlencode "client_id=$ACTOR_CLIENT_ID" \
  --data-urlencode "client_secret=$ACTOR_CLIENT_SECRET" \
  --data-urlencode 'scope=agent.run' \
  -o .local/actor-token.json -w 'HTTP %{http_code}\n'
```

Expected: **200**. Then:

```bash
export ACTOR_ACCESS_TOKEN="$(jq -er '.access_token | select(type == "string" and length > 0)' .local/actor-token.json)"
```

## 7. Exchange tokens for a selected tool

Obtain the human access token using **Authorization Code + PKCE**. You can use the Postman/Insomnia OAuth helper described in the [API walkthrough](setup-and-api-walkthrough.md#obtain-the-actual-human-access-token-for-manual-testing). Register its callback URL in the human sign-in application. Use its **access token**, then continue with cURL:

```bash
export SUBJECT_ACCESS_TOKEN='PASTE_HUMAN_ACCESS_TOKEN'
export LOGGED_IN_SUBJECT='PASTE_SIGNED_IN_USERNAME'
export TOOL_NAME='list_available_courses'
export COURSE_ID='ALL'

jq -n --arg creator "$AGENT_ID" --arg user "$LOGGED_IN_SUBJECT" \
  --arg tool "$TOOL_NAME" --arg course "$COURSE_ID" \
  '[{type:"urn:ibm:demo:verify:mcp_tool_action",courseId:$course,
    operationDetails:{creator:$creator,affectedPerson:$user,loggedInSubject:$user,
      action:$tool,targetSystem:"course-mcp-server",resource:"mcp-tool",
      toolName:$tool,downstreamSystem:"course-api"}}]' > .local/tool-rar.json

curl --silent --show-error --fail-with-body \
  -X POST "$TENANT/oauth2/token" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'grant_type=urn:ietf:params:oauth:grant-type:token-exchange' \
  --data-urlencode "client_id=$STS_CLIENT_ID" \
  --data-urlencode "client_secret=$STS_CLIENT_SECRET" \
  --data-urlencode "subject_token=$SUBJECT_ACCESS_TOKEN" \
  --data-urlencode 'subject_token_type=urn:ietf:params:oauth:token-type:access_token' \
  --data-urlencode "actor_token=$ACTOR_ACCESS_TOKEN" \
  --data-urlencode 'actor_token_type=urn:ietf:params:oauth:token-type:access_token' \
  --data-urlencode 'audience=course-mcp-server' \
  --data-urlencode authorization_details@.local/tool-rar.json \
  -o .local/delegated-token.json -w 'HTTP %{http_code}\n'
```

Expected: **200**. Capture the delegated token:

```bash
export DELEGATED_ACCESS_TOKEN="$(jq -er '.access_token | select(type == "string" and length > 0)' .local/delegated-token.json)"
```

## 8. Invoke the tool

Start the local application using setup Step 8 before calling:

```bash
jq -n --arg token "$DELEGATED_ACCESS_TOKEN" --arg user "$LOGGED_IN_SUBJECT" \
  --arg tool "$TOOL_NAME" --arg course "$COURSE_ID" \
  '{tool_name:$tool,course_id:$course,requested_subject:$user,
    logged_in_subject:$user,delegated_token:$token}' > .local/tool-invoke.json

curl --silent --show-error --fail-with-body \
  -X POST 'http://localhost:8000/mcp/invoke' \
  -H 'Content-Type: application/json' \
  --data-binary @.local/tool-invoke.json \
  -o .local/tool-result.json -w 'HTTP %{http_code}\n'
jq . .local/tool-result.json
```

Expected: **200** and the course list. To enroll, set `TOOL_NAME=enroll_course` and `COURSE_ID` to a course from the catalog, then repeat Steps 7–8 to obtain authority for that operation. To view enrollments, use `TOOL_NAME=list_enrolled_courses` and `COURSE_ID=ALL`, then repeat Steps 7–8.

Review [audit activity](audit.md) to compare the read and enrollment token events. Keep token response and invocation files under `.local/` private.
