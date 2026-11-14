SET NOCOUNT ON;
SET XACT_ABORT ON;
USE CareerPortfolioSqlLab;
GO
BEGIN TRANSACTION;
INSERT dbo.Payments(order_id,external_ref,amount,paid_at)
VALUES (1,'PAY-001',150.00,SYSUTCDATETIME());

IF (SELECT COUNT(*) FROM dbo.Payments WHERE external_ref='PAY-001') <> 2
    THROW 51000, 'Duplicate payment reproduction failed', 1;

;WITH duplicates AS (
    SELECT id, ROW_NUMBER() OVER (PARTITION BY external_ref ORDER BY id) AS row_number
    FROM dbo.Payments
)
DELETE FROM duplicates WHERE row_number > 1;

IF (SELECT COUNT(*) FROM dbo.Payments WHERE external_ref='PAY-001') <> 1
    THROW 51001, 'Duplicate payment correction failed', 1;

UPDATE dbo.Orders SET total=999 WHERE id=1;
IF NOT EXISTS (
    SELECT 1 FROM dbo.Orders o
    CROSS APPLY (SELECT SUM(quantity*unit_price) calculated FROM dbo.OrderItems WHERE order_id=o.id) x
    WHERE o.id=1 AND o.total<>x.calculated
)
    THROW 51002, 'Order-total investigation failed', 1;

UPDATE o SET total=x.calculated
FROM dbo.Orders o
CROSS APPLY (SELECT SUM(quantity*unit_price) calculated FROM dbo.OrderItems WHERE order_id=o.id) x
WHERE o.id=1;

IF EXISTS (
    SELECT 1 FROM dbo.Orders o
    CROSS APPLY (SELECT SUM(quantity*unit_price) calculated FROM dbo.OrderItems WHERE order_id=o.id) x
    WHERE o.id=1 AND o.total<>x.calculated
)
    THROW 51003, 'Order-total correction failed', 1;

ROLLBACK TRANSACTION;

IF (SELECT COUNT(*) FROM dbo.Payments WHERE external_ref='PAY-001') <> 1
    THROW 51004, 'Transaction rollback failed', 1;

PRINT 'SQLLAB_INTEGRATION_PASS';
GO

