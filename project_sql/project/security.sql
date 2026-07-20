-- Create the marketing_analyst role
CREATE ROLE 'marketing_analyst';

-- Grant SELECT only on permitted objects
GRANT SELECT ON ecommerce_db.vw_high_value_customers TO 'marketing_analyst';
GRANT SELECT ON ecommerce_db.daily_sales_summary      TO 'marketing_analyst';
GRANT SELECT ON ecommerce_db.orders                   TO 'marketing_analyst';
GRANT SELECT ON ecommerce_db.customers                TO 'marketing_analyst';

-- Explicitly deny sensitive tables (MySQL denies by default; document explicitly)
-- No GRANT on: payments, order_items, products, suppliers, reviews

-- Create analyst user
CREATE USER 'analyst_user'@'localhost' IDENTIFIED BY 'SecurePass!2024';
GRANT 'marketing_analyst' TO 'analyst_user'@'localhost';
SET DEFAULT ROLE 'marketing_analyst' TO 'analyst_user'@'localhost';

-- Test: analyst_user CANNOT run this:
-- SELECT * FROM payments;       -- ERROR 1142: SELECT command denied
-- SELECT * FROM order_items;    -- ERROR 1142: SELECT command denied

-- Test: analyst_user CAN run this:
-- SELECT * FROM vw_high_value_customers;
-- SELECT * FROM orders LIMIT 10;





