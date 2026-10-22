<!--
Copyright IBM Corp. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
-->

# Audit course listing and enrollment

[Setup](setup.md) · [Runtime demonstration](runtime-and-troubleshooting.md)

## What the audit shows

IBM Verify token events record which agent authenticated and which user, tool and permissions were included when delegated access was issued. Use these records alongside the MCP operation result to trace a request.

The examples below are based on four events captured for course listing and enrollment. All four record `result=success` and `action=issued`. Identity values in the downloadable examples use placeholders; tenant details, IP addresses, geolocation, user IDs and token hashes are omitted. Event IDs, times and transaction links are retained for comparison.

## Find the events

1. Open **Reporting & diagnostics → Reports** in the Verify administration console.
2. Choose the time window of your demonstration and locate **Token** events. Depending on the tenant view, also inspect application/client authentication or AI activity reports.
3. Filter or search for **UC2 Course MCP Conversational Agent** to find agent authentication.
4. Search for **UC2 Course MCP Agent Token Exchange** to find delegated-token issuance.
5. Open the event details or export JSON. Inspect the fields below; use the sample's response and MCP logs to confirm the tool result.

Report labels may vary by tenant. The field names below are taken from the supplied event exports.

## Example sequence

Times are on **22 October 2026, Asia/Singapore (UTC+08:00)**.

| Event ID prefix | Time | Operation | Course | Scope | Result |
|---|---|---|---|---|---|
| `12aa8218…` | 22:44:09.414 | `Agent authentication` | `—` | `agent.run` | success |
| `dd2dc3e0…` | 22:44:09.803 | `list_available_courses` | `ALL` | `mcp.tools.invoke course.read` | success |
| `5effb8b3…` | 22:45:56.846 | `list_available_courses` | `ALL` | `mcp.tools.invoke course.read` | success |
| `173c2cc4…` | 22:46:11.170 | `enroll_course` | `GOV-301` | `mcp.tools.invoke course.enroll` | success |

Two list events are present. They share the user session transaction but have different `actor_txn` and correlation IDs, so treat them as separate token-issuance events.

## Agent authentication

Open [actor-token.json](audit-examples/actor-token.json).

| Field | Example value / meaning |
|---|---|
| `grant_type` | `client_credentials` |
| `applicationname` | `UC2 Course MCP Conversational Agent` |
| `scope` | `agent.run` |
| `entity_type` | `agent` |
| `entity_id` | AgentID of the registered agent |
| `client_id` | OAuth client ID of its runtime application |
| `txn` | Transaction used to link this authentication to a later exchange |

This event establishes that the runtime application authenticated as the registered agent. It does not by itself establish that a course tool ran.

## List available courses

Open [list-courses.json](audit-examples/list-courses.json) and the second [list-courses-repeat.json](audit-examples/list-courses-repeat.json).

| Field | Observed value |
|---|---|
| `grant_type` | `urn:ietf:params:oauth:grant-type:token-exchange` |
| `applicationname` | `UC2 Course MCP Agent Token Exchange` |
| `username` | The signed-in user (`demo-user` in the sanitized example) |
| `actor_entity_type` | `agent` |
| `actor_entity_id` | Registered AgentID |
| `scope` | `mcp.tools.invoke course.read` |
| `auth_details[0].courseId` | `ALL` |
| `auth_details[0].operationDetails.action` | `list_available_courses` |
| `auth_details[0].operationDetails.toolName` | `list_available_courses` |
| `auth_details[0].operationDetails.targetSystem` | `course-mcp-server` |

The event contains both `requested_auth_details` and `auth_details`. Their parsed contents match for these captured requests: the requested list operation appears in the issued authorization context.

## Enroll in a course

Open [enroll-course.json](audit-examples/enroll-course.json).

| Field | Observed value |
|---|---|
| `applicationname` | `UC2 Course MCP Agent Token Exchange` |
| `username` | The same signed-in user |
| `actor_entity_id` | The same registered AgentID |
| `scope` | `mcp.tools.invoke course.enroll` |
| `auth_details[0].courseId` | `GOV-301` |
| `auth_details[0].operationDetails.action` | `enroll_course` |
| `auth_details[0].operationDetails.toolName` | `enroll_course` |
| `auth_details[0].operationDetails.affectedPerson` | The intended user |

The enrollment event identifies a specific course and carries enrollment permission. Compare this with the list event's `ALL` course selection and read permission. Requested and issued authorization details also match in this enrollment example.

## Link authentication to delegated activity

The first list event provides a direct transaction link to the supplied agent-authentication event:

```text
List event data.actor_txn:
f871fa67-90b6-4aae-bdd2-4387c4c3b3f6

Agent authentication data.txn:
f871fa67-90b6-4aae-bdd2-4387c4c3b3f6
```

| Field | How to use it |
|---|---|
| `actor_txn` | Find the agent-authentication event whose `txn` matches it |
| `subject_txn` | Find the associated subject-token transaction when its event is available |
| `actor_entity_id` / `entity_id` | Identify the registered agent across the supplied events |
| `username` | Identify the human in the exchange event |
| `correlationid` | Investigate that event's request; each supplied event has a different value |
| `auth_details` | Inspect the authorized tool, course and target system |

All three exchange events have `subject_txn=23e0f2be-ba9d-47f4-9974-50f8b5ec6e2a`. This groups them under the same subject transaction, not a single tool invocation. The matching subject-authentication event is not included in these four exports. The additional actor-authentication events referenced by the repeated list and enrollment events are also outside this set.

## Read the authorization details

In these exports, `actor`, `requested_auth_details` and `auth_details` are JSON stored as strings. For example:

```bash
jq '._source.data | {
  applicationname, username, scope, actor_entity_id,
  actor: (.actor | fromjson),
  requested: (.requested_auth_details | fromjson),
  authorized: (.auth_details | fromjson)
}' docs/audit-examples/enroll-course.json
```

## Confirm the business result

Token events establish successful issuance of delegated authority. Confirm successful listing or enrollment using the returned application result, MCP validation diagnostics and the enrolled-course query. The token events alone do not prove that enrollment completed.
