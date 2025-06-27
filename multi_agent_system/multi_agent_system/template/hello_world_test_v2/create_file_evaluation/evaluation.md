# Phase create_file: Create a simple hello world text file - Evaluation

## Evaluation Task
Assess whether Phase create_file was completed successfully by examining evidence.

## Files to Check
Examine these files in ./evidence/:
- `hello.txt` - Primary deliverable (hello world file)
- `create_file_summary.txt` - Implementation summary  
- `create_file_verification.txt` - Verification proof

## Pass Requirements (ALL must be met)
1. **File Created**: `hello.txt` exists and is readable
2. **Correct Content**: File contains exactly "Hello World!" text
3. **Summary Provided**: Summary accurately describes file creation
4. **Verification Complete**: Verification proves file works correctly
5. **All Evidence Present**: All required evidence files exist

## Fail Conditions (ANY causes failure)
- `hello.txt` file missing or empty
- File contains wrong text (not "Hello World!")
- Summary file missing or inaccurate
- Verification file missing or incomplete
- Any required evidence files missing

## Evaluation Process
1. Check each required evidence file exists
2. Verify content quality and completeness
3. Assess implementation against requirements
4. Validate verification claims
5. Score objectively based only on evidence

## Output Format
Provide result in exactly this format:

```
RESULT: PASS
SCORE: [0-100]
ISSUES: [list any issues found, or "None"]
SUMMARY: [brief description of what was accomplished]
```

OR

```
RESULT: FAIL  
SCORE: [0-100]
ISSUES: [list specific failures]
SUMMARY: [brief description of what was attempted]
```

## Scoring Guidelines
- **90-100**: Excellent, exceeds requirements
- **70-89**: Good, meets all requirements (minimum for PASS)
- **50-69**: Acceptable, minor issues (FAIL)
- **30-49**: Poor, major issues (FAIL)
- **0-29**: Failed, requirements not met (FAIL)

## Isolation Requirements
- Base assessment ONLY on evidence provided
- Do NOT access implementation directories
- Do NOT reference implementation process
- Evaluate objectively and independently
