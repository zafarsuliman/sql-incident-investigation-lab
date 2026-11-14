-- Run only in a disposable SQL Server database using two sessions.
-- Session A: BEGIN TRAN; UPDATE inventory SET reserved=reserved WHERE product_id=1; WAITFOR DELAY '00:00:05'; UPDATE inventory SET reserved=reserved WHERE product_id=2;
-- Session B: BEGIN TRAN; UPDATE inventory SET reserved=reserved WHERE product_id=2; WAITFOR DELAY '00:00:05'; UPDATE inventory SET reserved=reserved WHERE product_id=1;
-- Prevention: acquire locks in ascending product_id order and retry error 1205 with bounded backoff.

