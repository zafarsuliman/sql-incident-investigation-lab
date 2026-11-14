# Verification

Verified locally on 14 November 2026.

| Check | Command | Result |
| --- | --- | --- |
| Incident tests | `.clean-venv\Scripts\python.exe -m pytest -q` | PASS - 5 tests in 1.33 seconds |
| Static analysis | `.clean-venv\Scripts\python.exe -m ruff check .` | PASS |
| SQL Server transactional scripts | `sqlcmd` setup and verification recorded in the portfolio report | PASS in the recorded SQL Server Express run |
| Docker SQL Server | Compose profile | NOT VERIFIED |
| Two-session deadlock capture | Manual concurrent reproduction | NOT VERIFIED |

The SQLite app and SQL Server scripts cover different review paths. Do not interpret the SQLite test result as proof that the Docker SQL Server or deadlock path ran.
