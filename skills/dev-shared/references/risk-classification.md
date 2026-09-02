# Complexity vs risk

**Complexity** (small / medium / large) reduces or increases planning.

**Risk** (normal / high) is **never** reduced by a small diff. High-risk includes: auth, authorization, money, personal data, migration, concurrency, public contract, security.

| | Feature | Bug |
| --- | --- | --- |
| small + normal | Compact spec; F-A may authorize skipping design/tasks | All B gates; no spec/design/tasks |
| large or high-risk | Design, tasks, and negative tests are required | Wider triage; rigor increases, patch scope does not |
| production / incident | n/a | Explicit mitigation; postmortem only if the user confirms |

A Jira ticket is a signal, not absolute truth. Ticket type “Bug” plus a request for new behavior → Gate 0.
