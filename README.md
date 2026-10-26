<!--
Copyright IBM Corp. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
-->

# Secure a Course Agent with MCP tool integration

| ⚠️ General availability ⚠️ |
| :--- |
| This demonstration uses generally available IBM Verify Agent Identity capabilities. Availability may vary by data center and tenant rollout. Confirm that the required capabilities are enabled in your tenant before starting |

This tutorial demonstrates how IBM Agent Identity in IBM Verify secures a conversational agent that calls MCP course tools on behalf of a signed-in user.

## Before you begin

Read the IBM Agent Identity concepts articles and ensure you have a basic understanding of agent registration, runtime credentials and delegated access.

## Guides

| Guide | Purpose |
|---|---|
| [Setup](docs/setup.md) | **Start here.** Complete the first-time configuration and start the sample. |
| [Architecture](docs/architecture.md) | Understand the components and request flow. |
| [cURL walkthrough](docs/curl-walkthrough.md) | Run the API steps using cURL. Follow Setup for the required console configuration. |
| [Postman and Insomnia](docs/setup-and-api-walkthrough.md) | Alternative ways to run the API steps. |
| [API request reference](docs/collection-coverage.md) | Find each request and its expected response. |
| [Runtime and troubleshooting](docs/runtime-and-troubleshooting.md) | Test the sample and resolve errors. |
| [Audit activity](docs/audit.md) | Trace course listing and enrollment. |

**For first-time setup, begin with Setup. Use cURL for API operations, or choose Postman or Insomnia. Complete the shared console configuration once.**

## Run the demonstration

1. Complete setup Steps 1–3 to register the agent, associate its runtime OAuth application and activate it.
2. Complete Steps 4–6 to configure user sign-in, delegation and the Token Exchange application.
3. Configure `.env` in Step 7, then install and start the sample in Step 8.
4. Open `http://localhost:8000` and sign in.
5. Ask “Show me the available courses”, “Enroll me in Advanced Security Operations”, and “Show my enrolled courses”.
6. Review the operation results and [audit activity](docs/audit.md).

Use the [direct cURL walkthrough](docs/curl-walkthrough.md) for API operations. Postman and Insomnia provide alternative ways to send the same requests. The setup guide identifies the shared console configuration.
