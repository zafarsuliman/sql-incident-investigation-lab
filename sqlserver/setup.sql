SET NOCOUNT ON;
IF DB_ID(N'CareerPortfolioSqlLab') IS NULL
BEGIN
    CREATE DATABASE CareerPortfolioSqlLab;
END;
GO
USE CareerPortfolioSqlLab;
GO
IF OBJECT_ID(N'dbo.Payments', N'U') IS NOT NULL DROP TABLE dbo.Payments;
IF OBJECT_ID(N'dbo.OrderItems', N'U') IS NOT NULL DROP TABLE dbo.OrderItems;
IF OBJECT_ID(N'dbo.Orders', N'U') IS NOT NULL DROP TABLE dbo.Orders;
IF OBJECT_ID(N'dbo.Inventory', N'U') IS NOT NULL DROP TABLE dbo.Inventory;
IF OBJECT_ID(N'dbo.Products', N'U') IS NOT NULL DROP TABLE dbo.Products;
IF OBJECT_ID(N'dbo.Customers', N'U') IS NOT NULL DROP TABLE dbo.Customers;
GO
CREATE TABLE dbo.Customers (
    id int IDENTITY PRIMARY KEY,
    name nvarchar(120) NOT NULL,
    email nvarchar(254) NOT NULL
);
CREATE TABLE dbo.Products (
    id int IDENTITY PRIMARY KEY,
    sku varchar(40) NOT NULL UNIQUE,
    name nvarchar(120) NOT NULL,
    price decimal(12,2) NOT NULL CHECK (price >= 0)
);
CREATE TABLE dbo.Inventory (
    product_id int PRIMARY KEY REFERENCES dbo.Products(id),
    on_hand int NOT NULL CHECK (on_hand >= 0),
    reserved int NOT NULL DEFAULT 0 CHECK (reserved >= 0)
);
CREATE TABLE dbo.Orders (
    id int IDENTITY PRIMARY KEY,
    customer_id int NOT NULL REFERENCES dbo.Customers(id),
    order_date date NOT NULL,
    status varchar(20) NOT NULL,
    total decimal(12,2) NOT NULL
);
CREATE INDEX IX_Orders_CustomerId ON dbo.Orders(customer_id);
CREATE TABLE dbo.OrderItems (
    id int IDENTITY PRIMARY KEY,
    order_id int NOT NULL REFERENCES dbo.Orders(id),
    product_id int NOT NULL REFERENCES dbo.Products(id),
    quantity int NOT NULL CHECK (quantity > 0),
    unit_price decimal(12,2) NOT NULL
);
CREATE TABLE dbo.Payments (
    id int IDENTITY PRIMARY KEY,
    order_id int NOT NULL REFERENCES dbo.Orders(id),
    external_ref varchar(80) NOT NULL,
    amount decimal(12,2) NOT NULL,
    paid_at datetime2 NOT NULL
);
GO
INSERT dbo.Customers(name,email) VALUES (N'Naledi Mokoena','naledi@example.test');
INSERT dbo.Products(sku,name,price) VALUES ('SKU-100',N'Safety Gloves',75.00);
INSERT dbo.Inventory(product_id,on_hand,reserved) VALUES (1,100,10);
INSERT dbo.Orders(customer_id,order_date,status,total) VALUES (1,'2026-10-01','paid',150.00);
INSERT dbo.OrderItems(order_id,product_id,quantity,unit_price) VALUES (1,1,2,75.00);
INSERT dbo.Payments(order_id,external_ref,amount,paid_at) VALUES (1,'PAY-001',150.00,SYSUTCDATETIME());
GO
PRINT 'SQLLAB_SETUP_PASS';

