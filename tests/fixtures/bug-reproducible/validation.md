# validation

PASS
RED on pre-fix `abcdef0`: `npm test -- pay.timeout.test.ts` failed.
GREEN on HEAD `1234567`: same command passed.
Evidence: src/pay.ts:18
Diff range: abcdef0...1234567
Cause addressed, not only the spinner symptom.

## Completeness

| Item | Status | Evidence | Correction |
| --- | --- | --- | --- |
| timeout symptom | done | src/pay.ts:18 | none |
| cause | done | src/pay.ts:18 | none |
