# Tasks

## Task 1 — OTP API

- Files: `src/otp.ts`, `src/otp.test.ts`
- Consumes: `SmsClient`
- Produces: `POST /api/otp`
- REQ-001
- Depends on: none
- RED: `npm test -- otp.test.ts` fails on missing handler
- GREEN: same command passes
- Gate: test runner exit 0
