# 🚀 Deployment Checklist

## Pre-Deployment

- [ ] Read `IMPLEMENTATION_COMPLETE.md`
- [ ] Review `FIXES_AND_IMPROVEMENTS.md`
- [ ] Check `QUICK_REFERENCE.md` for configuration
- [ ] Review code changes in modified files
- [ ] Verify all tests pass

## Code Deployment

- [ ] Deploy updated `backend/app/config.py`
- [ ] Deploy updated `backend/app/routers/query.py`
- [ ] Deploy updated `backend/app/services/rag_service.py`
- [ ] Deploy updated `backend/app/services/cache_service.py`
- [ ] Deploy updated `backend/scraper/cleaner.py`
- [ ] Deploy updated `backend/setup/simplify_laws.py`
- [ ] Deploy NEW `backend/app/services/validation_service.py`

## Configuration

- [ ] Verify `SIMILARITY_THRESHOLD = 0.70` (not 0.50)
- [ ] Verify `MIN_RESULT_CONFIDENCE = 0.60` exists
- [ ] Verify `MIN_SECTION_TEXT_LENGTH = 100` exists
- [ ] Verify `MIN_SIMPLIFIED_TEXT_LENGTH = 50` exists
- [ ] Update `.env` file if using environment variables

## Database Preparation

- [ ] Backup current database
- [ ] No schema changes needed (backward compatible)
- [ ] Optional: Run cache clear for fresh start

## Data Quality Validation

- [ ] Run: `python -m setup.simplify_laws`
- [ ] Monitor: Check logs for validation failures
- [ ] Verify: At least 95% of sections pass validation
- [ ] If issues: Check logs and adjust thresholds if needed

## Testing

### Functional Tests

- [ ] **Test 1 - Normal Query**: Execute a typical legal query
  - ✓ Should return relevant laws
  - ✓ Should include disclaimer in response
  - ✓ Should show real confidence scores
- [ ] **Test 2 - Fallback Mode**: Disable embeddings temporarily
  - ✓ Should use keyword search
  - ✓ Should show "⚠️ FALLBACK MODE:" warning
  - ✓ Should show confidence as 0.50
- [ ] **Test 3 - Low Confidence**: Query with vague terms
  - ✓ Should return fewer results (threshold 0.70)
  - ✓ Should log low confidence warnings
- [ ] **Test 4 - Null Simplified Text**: Update law to set simplified_en = NULL
  - ✓ Should fallback to original text
  - ✓ Should log fallback warning
- [ ] **Test 5 - Cache Invalidation**: Make query → update law → make same query
  - ✓ Should return fresh result (not cached)
- [ ] **Test 6 - Error Recovery**: Stop LLM API temporarily
  - ✓ Should degrade gracefully
  - ✓ Should show degraded mode warning
  - ✓ Should still return vector search results

### Data Quality Tests

- [ ] **Test 7 - Validation**: Run simplify script on test data
  - ✓ Should reject sections < 100 chars
  - ✓ Should reject invalid severity
  - ✓ Should reject hallucinations
- [ ] **Test 8 - Logging**: Check application logs
  - ✓ Should see warning for missing severity
  - ✓ Should see error for failed validation
  - ✓ Should see info for successful operations

### Performance Tests

- [ ] **Test 9 - Response Time**: Should be < 1 second (with cache)
- [ ] **Test 10 - Cache Hit Rate**: Should see > 50% cache hits after warmup

## Monitoring

- [ ] Set up log monitoring for:
  - [ ] "Severity missing"
  - [ ] "Validation failed"
  - [ ] "Fallback mode"
  - [ ] "Cache invalidated"
  - [ ] Error messages

- [ ] Set up metrics:
  - [ ] Vector search success rate
  - [ ] Fallback rate
  - [ ] Cache hit rate
  - [ ] Validation failure rate

- [ ] Create alerts for:
  - [ ] Fallback rate > 10%
  - [ ] Validation failures > 5%
  - [ ] Response time > 2 seconds
  - [ ] Error rate > 1%

## Documentation

- [ ] Add link to `FIXES_AND_IMPROVEMENTS.md` in main README
- [ ] Update API documentation with new response fields
- [ ] Document new config settings in `.env.example`
- [ ] Update frontend to display disclaimers prominently

## Frontend Updates

- [ ] Display disclaimer banner in results page
- [ ] Show fallback mode indicator
- [ ] Display actual confidence scores
- [ ] Update language for legal safety

## Post-Deployment

### Day 1

- [ ] Monitor logs for errors
- [ ] Check validation failure rate
- [ ] Verify users getting better results
- [ ] Monitor performance metrics

### Day 7

- [ ] Review log patterns
- [ ] Adjust thresholds if needed
- [ ] Update documentation based on learnings
- [ ] Celebrate improved quality! 🎉

## Rollback Plan

If issues occur:

1. Stop application
2. Revert to previous `backend/app/` code
3. Keep `validation_service.py` (non-critical)
4. Revert config to `SIMILARITY_THRESHOLD = 0.50`
5. Clear Redis cache
6. Restart application

---

## Configuration Comparison

### Before

```python
SIMILARITY_THRESHOLD: float = 0.50
CACHE_TTL_SECONDS: int = 86400
# No validation settings
# No confidence thresholds
```

### After

```python
SIMILARITY_THRESHOLD: float = 0.70          # ← CHANGED
CACHE_TTL_SECONDS: int = 86400
MIN_RESULT_CONFIDENCE: float = 0.60         # ← NEW
MIN_SECTION_TEXT_LENGTH: int = 100          # ← NEW
MIN_SIMPLIFIED_TEXT_LENGTH: int = 50        # ← NEW
```

---

## Files Summary

| File                       | Type     | Status    |
| -------------------------- | -------- | --------- |
| config.py                  | Modified | Ready     |
| query.py                   | Modified | Ready     |
| rag_service.py             | Modified | Ready     |
| cache_service.py           | Modified | Ready     |
| cleaner.py                 | Modified | Ready     |
| simplify_laws.py           | Modified | Ready     |
| validation_service.py      | New      | Ready     |
| FIXES_AND_IMPROVEMENTS.md  | Docs     | Ready     |
| QUICK_REFERENCE.md         | Docs     | Ready     |
| IMPLEMENTATION_COMPLETE.md | Docs     | Ready     |
| DEPLOYMENT_CHECKLIST.md    | Docs     | This file |

---

## Success Criteria

✅ Deployment is successful if:

- [ ] No errors in application logs
- [ ] At least 90% of queries return within 1 second
- [ ] Less than 5% validation failures
- [ ] All tests pass
- [ ] Users see disclaimers in results
- [ ] Confidence scores are realistic (0.6-0.95, not 0.5-0.66)
- [ ] Cache invalidation working (old results cleared)
- [ ] Error messages are clear and helpful

---

## Quick Commands

```bash
# Deployment
git pull origin main
docker-compose up -d

# Validation
python -m setup.simplify_laws

# Testing
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"issue": "someone stole my phone", "language": "en"}'

# Monitoring
tail -f backend/logs/lexindia.log | grep -E "FAILED|DEGRADED|Validation"

# Cache clearing
redis-cli KEYS "lexindia:*" | xargs redis-cli DEL

# Database backup
pg_dump lexindia > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## Support Resources

- Technical details: `FIXES_AND_IMPROVEMENTS.md`
- Quick reference: `QUICK_REFERENCE.md`
- Status: `IMPLEMENTATION_COMPLETE.md`
- Configuration: `backend/app/config.py`
- Validation: `backend/app/services/validation_service.py`

---

## Sign-Off

- [ ] QA: Tested all scenarios
- [ ] DevOps: Reviewed deployment
- [ ] Product: Approved changes
- [ ] Security: Reviewed no breaking changes

Date Deployed: ******\_\_\_\_******
Deployed By: ******\_\_\_\_******

---

**All set? Let's deploy! 🚀**
