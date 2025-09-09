# BigQuery Conversational Analytics Authentication Scope Error

(Issue)[https://github.com/googleapis/genai-toolbox/issues/1378]

## Problem

The `bigquery-conversational-analytics` tool fails with `ACCESS_TOKEN_SCOPE_INSUFFICIENT` error in Cloud Run environments, while all other BigQuery tools work fine.

## Error Details

```json
{
  "error": {
    "code": 403,
    "message": "Request had insufficient authentication scopes.",
    "status": "PERMISSION_DENIED",
    "details": [{
      "@type": "type.googleapis.com/google.rpc.ErrorInfo",
      "reason": "ACCESS_TOKEN_SCOPE_INSUFFICIENT",
      "domain": "googleapis.com",
      "metadata": {
        "method": "google.cloud.geminidataanalytics.v1alpha.DataChatService.Chat",
        "service": "geminidataanalytics.googleapis.com"
      }
    }]
  }
}
```

## Environment

- **✅ Working**: Local development → MCP Toolbox
- **❌ Failing**: Cloud Run → MCP Toolbox
- **✅ Working**: All other BigQuery tools in both environments
- **❌ Failing**: Only `bigquery-conversational-analytics` tool

## Root Cause

The conversational analytics tool uses `TokenSource` with limited BigQuery scope (`bigqueryapi.Scope`), but the Gemini Data Analytics API requires broader `cloud-platform` scope.

**Key difference from working tools:**
- Other BigQuery tools use `ClientCreator` pattern for flexible scope handling
- Conversational analytics tool makes direct HTTP calls to `geminidataanalytics.googleapis.com` with insufficient scopes

## Reproduction

Use this test script to reproduce the error:

```python
#!/usr/bin/env python3
import os
import json
import requests
import google.auth
from google.auth.transport.requests import Request

def test_conversational_analytics():
    # Get cloud-platform scoped token
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    request = Request()
    credentials.refresh(request)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {credentials.token}"
    }

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "bigquery-conversational-analytics",
            "arguments": {
                "user_query_with_context": "What is the structure of this table?",
                "table_references": json.dumps([{
                    "projectId": "your-project",
                    "datasetId": "samples",
                    "tableId": "shakespeare"
                }])
            }
        }
    }

    response = requests.post("YOUR_TOOLBOX_URL/mcp", headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    print(response.text)

if __name__ == "__main__":
    test_conversational_analytics()
```

## Proposed Solution

Make the conversational analytics tool consistent with other BigQuery tools by adding `ClientCreator` support:

1. **Add `ClientCreator` field** to Tool struct
2. **Update `compatibleSource` interface** to include `BigQueryClientCreator()` method
3. **Initialize `ClientCreator`** in the tool setup
4. **Enable proper OAuth scope handling** for Cloud Run environments

## Current Workaround

Set `useClientOAuth: true` in configuration:

```yaml
sources:
  bq_source:
    kind: bigquery
    project: ${BIGQUERY_PROJECT}
    useClientOAuth: true
```

However, this requires changes to existing deployments.

## Files Affected

- `internal/tools/bigquery/bigqueryconversationalanalytics/bigqueryconversationalanalytics.go`

## Impact

This issue prevents the conversational analytics tool from working in production Cloud Run environments where other BigQuery tools work perfectly. The tool is the only BigQuery tool that exhibits this authentication scope limitation.
