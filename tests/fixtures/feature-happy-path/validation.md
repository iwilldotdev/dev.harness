# validation

Verdict: PASS

| REQ | Outcome | Test | Evidence |
| --- | --- | --- | --- |
| REQ-001 | OTP SMS sent | `npm test -- otp.test.ts` | src/otp.ts:12 |
| REQ-002 | lock after 3 failures | `npm test -- otp.lock.test.ts` | src/otp.ts:40 |

Diff range: `abcdef0...1234567`

## Completeness

| Item | Status | Evidence | Correction |
| --- | --- | --- | --- |
| REQ-001 | done | src/otp.ts:12 | none |
| REQ-002 | done | src/otp.ts:40 | none |
