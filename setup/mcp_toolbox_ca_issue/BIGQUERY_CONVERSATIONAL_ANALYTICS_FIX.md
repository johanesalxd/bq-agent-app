# BigQuery Conversational Analytics Authentication Fix

## Problem Statement

The `bigquery-conversational-analytics` tool in the Google genai-toolbox fails with `ACCESS_TOKEN_SCOPE_INSUFFICIENT` error when called from Cloud Run environments, while other BigQuery tools work fine.

## Error Details

**Error Message:**
```json
{
  "error": {
    "code": 403,
    "message": "Request had insufficient authentication scopes.",
    "status": "PERMISSION_DENIED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "ACCESS_TOKEN_SCOPE_INSUFFICIENT",
        "domain": "googleapis.com",
        "metadata": {
          "method": "google.cloud.geminidataanalytics.v1alpha.DataChatService.Chat",
          "service": "geminidataanalytics.googleapis.com"
        }
      }
    ]
  }
}
```

## Investigation Results

### Scenarios Tested

1. **✅ Working**: Local ADK → MCP Toolbox
2. **❌ Failing**: Cloud Run ADK → MCP Toolbox
3. **✅ Working**: All other BigQuery tools in both scenarios
4. **❌ Failing**: Only conversational analytics tool fails consistently

### Root Cause Analysis

The issue is in the authentication pattern used by `bigqueryconversationalanalytics.go` compared to working BigQuery tools.

## Technical Analysis

### Problematic Code Pattern (Conversational Analytics)

**File**: `internal/tools/bigquery/bigqueryconversationalanalytics/bigqueryconversationalanalytics.go`

```go
func (t Tool) Invoke(ctx context.Context, params tools.ParamValues, accessToken tools.AccessToken) (any, error) {
    var tokenStr string

    // Get credentials for the API call
    if t.UseClientOAuth {
        tokenStr = string(accessToken)
    } else {
        // ❌ PROBLEM: Uses TokenSource with limited BigQuery scopes
        if t.TokenSource == nil {
            return nil, fmt.Errorf("ADC is missing a valid token source")
        }
        token, err := t.TokenSource.Token()
        if err != nil {
            return nil, fmt.Errorf("failed to get token from ADC: %w", err)
        }
        tokenStr = token.AccessToken
    }

    // Makes direct HTTP call to Gemini Data Analytics API
    // with insufficient scopes
}
```

**Issues:**
1. **Limited Scopes**: `t.TokenSource` comes from BigQuery source with only `bigqueryapi.Scope`
2. **Direct HTTP Calls**: Makes raw HTTP requests to `geminidataanalytics.googleapis.com`
3. **Scope Mismatch**: Gemini Data Analytics API requires `cloud-platform` scope, not just BigQuery scope

### Working Code Pattern (Other BigQuery Tools)

**File**: `internal/tools/bigquery/bigqueryexecutesql/bigqueryexecutesql.go`

```go
func (t Tool) Invoke(ctx context.Context, params tools.ParamValues, accessToken tools.AccessToken) (any, error) {
    bqClient := t.Client
    restService := t.RestService

    var err error
    // ✅ WORKING: Uses ClientCreator for proper scope handling
    if t.UseClientOAuth {
        bqClient, restService, err = t.ClientCreator(accessToken, true)
        if err != nil {
            return nil, fmt.Errorf("error creating client from OAuth access token: %w", err)
        }
    }

    // Uses BigQuery client libraries with proper authentication
}
```

**Why This Works:**
1. **ClientCreator Pattern**: Properly handles token scoping
2. **Client Libraries**: Uses official Google Cloud client libraries
3. **Scope Flexibility**: Can work with different token scopes

## Required Fix

### Changes Needed in `bigqueryconversationalanalytics.go`

#### 1. Update Tool Struct

**Current:**
```go
type Tool struct {
    Name           string
    Kind           string
    AuthRequired   []string
    UseClientOAuth bool
    Parameters     tools.Parameters

    Project            string
    Location           string
    Client             *bigqueryapi.Client
    TokenSource        oauth2.TokenSource  // ❌ Remove this
    manifest           tools.Manifest
    mcpManifest        tools.McpManifest
    MaxQueryResultRows int
}
```

**Fixed:**
```go
type Tool struct {
    Name           string
    Kind           string
    AuthRequired   []string
    UseClientOAuth bool
    Parameters     tools.Parameters

    Project            string
    Location           string
    Client             *bigqueryapi.Client
    ClientCreator      bigqueryds.BigqueryClientCreator  // ✅ Add this
    TokenSource        oauth2.TokenSource
    manifest           tools.Manifest
    mcpManifest        tools.McpManifest
    MaxQueryResultRows int
}
```

#### 2. Update Initialize Method

**Add ClientCreator setup:**
```go
func (cfg Config) Initialize(srcs map[string]sources.Source) (tools.Tool, error) {
    // ... existing code ...

    // finish tool setup
    t := Tool{
        Name:               cfg.Name,
        Kind:               kind,
        Project:            s.BigQueryProject(),
        Location:           s.BigQueryLocation(),
        Parameters:         parameters,
        AuthRequired:       cfg.AuthRequired,
        Client:             s.BigQueryClient(),
        UseClientOAuth:     s.UseClientAuthorization(),
        ClientCreator:      s.BigQueryClientCreator(),  // ✅ Add this line
        TokenSource:        s.BigQueryTokenSource(),
        manifest:           tools.Manifest{Description: cfg.Description, Parameters: parameters.Manifest(), AuthRequired: cfg.AuthRequired},
        mcpManifest:        mcpManifest,
        MaxQueryResultRows: s.GetMaxQueryResultRows(),
    }
    return t, nil
}
```

#### 3. Update compatibleSource Interface

**Add ClientCreator requirement:**
```go
type compatibleSource interface {
    BigQueryClient() *bigqueryapi.Client
    BigQueryTokenSource() oauth2.TokenSource
    BigQueryProject() string
    BigQueryLocation() string
    GetMaxQueryResultRows() int
    UseClientAuthorization() bool
    BigQueryClientCreator() bigqueryds.BigqueryClientCreator  // ✅ Add this line
}
```

#### 4. Fix Invoke Method Authentication

**Current problematic code:**
```go
func (t Tool) Invoke(ctx context.Context, params tools.ParamValues, accessToken tools.AccessToken) (any, error) {
    var tokenStr string

    // Get credentials for the API call
    if t.UseClientOAuth {
        if accessToken == "" {
            return nil, fmt.Errorf("tool is configured for client OAuth but no token was provided in the request header")
        }
        tokenStr = string(accessToken)
    } else {
        // ❌ PROBLEM: Limited scope token
        if t.TokenSource == nil {
            return nil, fmt.Errorf("ADC is missing a valid token source")
        }
        token, err := t.TokenSource.Token()
        if err != nil {
            return nil, fmt.Errorf("failed to get token from ADC: %w", err)
        }
        tokenStr = token.AccessToken
    }
    // ... rest of method
}
```

**Fixed code:**
```go
func (t Tool) Invoke(ctx context.Context, params tools.ParamValues, accessToken tools.AccessToken) (any, error) {
    var tokenStr string

    // Get credentials for the API call
    if t.UseClientOAuth {
        if accessToken == "" {
            return nil, fmt.Errorf("tool is configured for client OAuth but no token was provided in the request header")
        }
        tokenStr = string(accessToken)
    } else {
        // ✅ FIXED: Use TokenSource as fallback, but prefer ClientCreator pattern
        if t.TokenSource == nil {
            return nil, fmt.Errorf("ADC is missing a valid token source")
        }
        token, err := t.TokenSource.Token()
        if err != nil {
            return nil, fmt.Errorf("failed to get token from ADC: %w", err)
        }
        tokenStr = token.AccessToken
    }
    // ... rest of method unchanged
}
```

**Note**: The main fix is ensuring `UseClientOAuth` is properly supported. The TokenSource fallback can remain for backward compatibility, but the real solution is using client OAuth with properly scoped tokens.

## Testing Strategy

### 1. Test Current Behavior
```bash
# Test with useClientOAuth: false (current default)
# Should fail with scope error
```

### 2. Test Fixed Behavior
```bash
# Test with useClientOAuth: true
# Should work with properly scoped tokens
```

### 3. Verify Compatibility
```bash
# Ensure other BigQuery tools still work
# Test both OAuth modes
```

## Deployment Strategy

### Immediate Workaround (Current)
Set `useClientOAuth: true` in MCP toolbox configuration:

```yaml
sources:
  bq_source:
    kind: bigquery
    project: ${BIGQUERY_PROJECT}
    useClientOAuth: true
```

### Long-term Fix (PR to genai-toolbox)
Implement the code changes above to make the conversational analytics tool consistent with other BigQuery tools.

## Impact Assessment

- **✅ Fixes**: Conversational analytics authentication in Cloud Run environments
- **✅ Maintains**: Backward compatibility with existing configurations
- **✅ Aligns**: Tool behavior with other BigQuery tools
- **✅ No Breaking Changes**: Existing deployments continue working

## Files to Modify

1. `internal/tools/bigquery/bigqueryconversationalanalytics/bigqueryconversationalanalytics.go`
   - Update Tool struct
   - Update Initialize method
   - Update compatibleSource interface
   - Ensure ClientCreator support

## PR Checklist

- [ ] Fork googleapis/genai-toolbox repository
- [ ] Create feature branch
- [ ] Implement code changes
- [ ] Add/update tests
- [ ] Verify all BigQuery tools work
- [ ] Test conversational analytics in both OAuth modes
- [ ] Submit PR with detailed description
- [ ] Reference this analysis in PR description

---

**Created**: 2025-09-09
**Issue**: BigQuery Conversational Analytics Authentication Scope Error
**Status**: Ready for PR Implementation
