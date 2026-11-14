# Architecture

```mermaid
flowchart LR
  U[Support analyst] --> S[Streamlit dashboard]
  S --> I[Incident service]
  I --> D[(Disposable SQLite demo)]
  I -. optional exercises .-> M[(SQL Server 2022)]
  T[pytest] --> I
```

The incident catalogue is immutable metadata; reproductions mutate only a disposable database. Database reset is intentionally cheap. SQLite makes the portfolio immediately inspectable, while SQL Server assets demonstrate platform-specific investigation without claiming local verification.

