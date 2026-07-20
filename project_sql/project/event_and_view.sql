-- Create the summary table first
CREATE TABLE IF NOT EXISTS daily_sales_summary (
    summary_id   INT PRIMARY KEY AUTO_INCREMENT,
    summary_date DATE NOT NULL UNIQUE,
    total_revenue    DECIMAL(14,2),
    total_orders     INT,
    avg_order_value  DECIMAL(10,2),
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Daily event at 11:59 PM
SET GLOBAL event_scheduler = ON;

CREATE EVENT evt_daily_sales_summary
ON SCHEDULE EVERY 1 DAY
STARTS (CURRENT_DATE + INTERVAL 1 DAY - INTERVAL 1 MINUTE)
DO
  INSERT INTO daily_sales_summary
      (summary_date, total_revenue, total_orders, avg_order_value)
  SELECT
      CURDATE(),
      COALESCE(SUM(total_amount), 0),
      COUNT(*),
      COALESCE(AVG(total_amount), 0)
  FROM orders
  WHERE DATE(order_date) = CURDATE()
    AND status = 'completed'
  ON DUPLICATE KEY UPDATE
      total_revenue   = VALUES(total_revenue),
      total_orders    = VALUES(total_orders),
      avg_order_value = VALUES(avg_order_value);

-- High-value customers view
CREATE OR REPLACE VIEW vw_high_value_customers AS
SELECT
    c.customer_id,
    c.full_name,
    c.email,
    c.city,
    c.join_date,
    c.total_spent,
    COUNT(o.order_id)          AS total_orders,
    AVG(o.total_amount)        AS avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.total_spent > 150000
GROUP BY c.customer_id, c.full_name, c.email, c.city, c.join_date, c.total_spent;
