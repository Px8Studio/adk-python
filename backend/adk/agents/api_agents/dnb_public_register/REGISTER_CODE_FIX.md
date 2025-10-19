# Fix: Invalid Register Code Error Handling

## Problem

The DNB Public Register API was rejecting requests with error:
```
HTTP 400: {"errorMessage":"The register code 'AFM' is not valid."}
```

This occurred because:
1. The LLM assumed 'AFM' was a valid register code
2. The agent didn't validate register codes before making API calls
3. No guidance existed for discovering valid register codes

## Root Cause

- **The OpenAPI spec doesn't enumerate valid register codes** - it only uses examples like `WFTAF`
- **The agent instructions didn't mention the discovery tool** `dnb_public_register_api_publicregister_registers`
- **Error messages weren't enhanced** to guide the LLM toward the solution

## Solution

### 1. Enhanced Agent Instructions

Added critical guidance in `dnb_public_register_agent`:
```python
CRITICAL - DISCOVERING VALID REGISTER CODES:
Before searching publications or entities, you MUST first discover valid register codes:
1. Call dnb_public_register_api_publicregister_registers to get the list of available registers
2. This returns register codes like 'WFTAF', 'WFT', etc. with their names and types
3. Use the EXACT register code from this list in subsequent API calls
4. Common mistake: Do NOT assume 'AFM' is a valid register code - always check first!
```

### 2. Improved Error Handling

Enhanced the `_PublicationsSearchAdapter` to detect invalid register code errors and provide actionable feedback:
```python
# Check for invalid register code error
if "register code" in error_msg.lower() and "not valid" in error_msg.lower():
    register_code = args.get("RegisterCode", "UNKNOWN")
    enhanced_msg = (
        f"Invalid register code '{register_code}'. "
        f"Use dnb_public_register_api_publicregister_registers tool to get valid register codes. "
        f"Original error: {error_msg}"
    )
    raise ValueError(enhanced_msg) from exc
```

### 3. Updated Coordinator Instructions

Added awareness in `dnb_coordinator_agent`:
```python
3. **Public Register API** (dnb_public_register_agent):
   - License searches, registration data, regulatory info
   - IMPORTANT: This agent will automatically discover valid register codes
   - Common registers: WFTAF (financial services), Wft (various financial categories)
   - Do NOT assume register codes like 'AFM' - let the specialist discover valid codes
```

## Testing

### Test Case 1: User asks for AFM register
**Before:**
```
Error: The register code 'AFM' is not valid
```

**After (Expected Flow):**
1. Agent calls `dnb_public_register_api_publicregister_registers`
2. Agent discovers valid codes (WFTAF, WFT, etc.)
3. Agent uses correct code or asks user to clarify which register they meant
4. Successful API call

### Test Case 2: Direct invalid register code
**Before:**
```
Exception: error while invoking tool: unexpected status code: 400
```

**After (Expected):**
```
ValueError: Invalid register code 'AFM'. Use dnb_public_register_api_publicregister_registers tool to get valid register codes. Original error: {"errorMessage":"The register code 'AFM' is not valid."}
```

## Available Tools

The agent now has clear instructions to use:

1. **`dnb_public_register_api_publicregister_registers`**
   - Returns list of all valid registers with codes, names, and types
   - Should be called FIRST when register codes are unknown

2. **`dnb_public_register_api_publicregister_publications_search`**
   - Requires valid `RegisterCode` (capital R)
   - Other params: `OrganizationName`, `ActArticleName`, `languageCode`, `page`, `pageSize`

## Common Valid Register Codes

Based on DNB documentation and examples:
- `WFTAF` - Financial services under Wft (Wet op het financieel toezicht)
- `WFT` - Various financial supervision categories
- Others can be discovered via the registers endpoint

## Related Issues

This fix is **NOT** related to the HTTP query parameter bug documented in `issue.md`. That bug involves optional query parameters with `nil` values being sent as empty strings (e.g., `?page=&pageSize=`). This is a separate issue about **data validation** where an invalid enum value is being used.

## Files Changed

1. `backend/adk/agents/api_agents/dnb_public_register/agent.py`
   - Enhanced agent instructions with register code discovery workflow
   - Improved error handling in `_PublicationsSearchAdapter`

2. `backend/adk/agents/api_coordinators/dnb_coordinator/agent.py`
   - Updated instructions to warn about register code assumptions

## Verification

To verify the fix works:

1. Restart ADK web server (file watcher should auto-reload)
2. Ask: "Find financial institutions in the AFM register"
3. Observe agent:
   - Calls `dnb_public_register_api_publicregister_registers` first
   - Uses valid register code from response
   - Completes search successfully
