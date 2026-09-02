# Spec — login OTP

WHAT: When a signed-in user opens checkout, the system shall send a one-time password.
WHY: Reduce fraud on payment.
WHO: Checkout shopper.

## REQ-001

When the user submits a valid phone, then the system sends an OTP SMS.
Origin: Jira SHOP-12 description / Gate F-A.
Expected outcome: SMS delivered; test asserts `/api/otp` 202.

## REQ-002

When the OTP is wrong three times, then checkout locks for 15 minutes.
Origin: Jira SHOP-12 AC.
Expected outcome: 429 with retry-after.

## Out of scope

Password reset. Admin impersonation.

## Risk

normal — no authz model change; payment already gated.
