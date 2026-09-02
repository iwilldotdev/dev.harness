# Hypothesis

Root cause: payment client retries with no timeout in `src/pay.ts`.
Hypothesis: adding a 5s abort controller fails the request instead of hanging.
Falsification: if the hang remains after abort, the cause is the gateway, not the client.
