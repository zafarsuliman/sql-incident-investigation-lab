# Incident runbooks

Each scenario exposed in the dashboard contains: symptom, reproduction action, investigation SQL, root cause, corrective action where locally supported, prevention guidance, and an isolated reset path. Automated tests cover representative mutation, investigation, correction, quarantine, and reset flows. The deadlock is deliberately a two-session SQL Server exercise because SQLite uses a different locking model.

| Incident | Verification focus |
|---|---|
| Duplicate payments | Group by payment reference; retain canonical row |
| Inventory discrepancy | Reserved quantity must not exceed on-hand |
| Slow query | Compare query plan before/after email index |
| Missing index | Compare customer order lookup plan |
| Incorrect total | Reconcile header to line calculation |
| Deadlock | Capture SQL Server error 1205/deadlock graph |
| Failed import | Quarantine invalid row while retaining valid row |
| Duplicate customer | Normalize email and merge canonical identity |
| Invalid date | Reject impossible dates at input boundary |
| Failed update | Reconcile shipped orders to audit events |

