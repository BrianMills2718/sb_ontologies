# Phase fix_blueprint_generation: Fix blueprint generation to create all required endpoints properly

## Task Description
Fix blueprint generation to create all required endpoints properly

## Problem Context
Current production validation shows **50% functional failure**:
- `/customers` endpoint returns 404 (should return customer data)
- `/analytics/dashboard` endpoint returns 404 (should return dashboard)
- `/database/health` endpoint returns 404 (should return health status)
- `/database/stats` endpoint returns 404 (should return stats)
- Only `/health` endpoint works (200 response)

**Root Cause**: Blueprint generation is not creating all required endpoints properly.

## Requirements
1. Analyze blueprint_language/ files to find why endpoints are missing/broken
2. Fix the blueprint generation code to create ALL required endpoints
3. Ensure generated systems have working /customers, /analytics/dashboard, /database/* routes
4. Test that a newly generated system has all endpoints working (not 404)
5. Verify the fixes work by running production_validation_functional.py

## Success Criteria
- Generated systems have /customers endpoint working (200, not 404)
- Generated systems have /analytics/dashboard endpoint working (200, not 404)
- Generated systems have /database/health and /database/stats working (200, not 404)
- Production validation functional test shows improved success rate
- Code changes are tested and verified to work

## Evidence Requirements
Create these files in ../shared/evidence/:
- `blueprint_fixes.txt` - Specific code changes made to blueprint generation
- `endpoint_verification.txt` - Test results showing endpoints now work
- `production_validation_results.txt` - New production validation results
- `fix_blueprint_generation_summary.txt` - Summary of what was accomplished

## Implementation Notes
- Work completely independently
- Focus only on this specific phase
- Base work only on these instructions
- Create comprehensive evidence for evaluation

## Completion Checklist
- [ ] All requirements implemented
- [ ] Implementation verified to work
- [ ] Evidence files created
- [ ] Summary documentation complete
