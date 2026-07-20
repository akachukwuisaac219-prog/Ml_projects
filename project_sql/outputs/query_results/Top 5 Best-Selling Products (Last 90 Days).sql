-- Top 5 best-selling products in the last 90 days
SELECT
    p.product_name,
    SUM(oi.quantity)                       AS total_units_sold,
    SUM(oi.quantity * oi.item_price)       AS total_revenue,
    p.stock                                AS current_stock
FROM order_items oi
JOIN orders o      using (order_id)
JOIN products p    using (product_id)
WHERE o.order_date >= DATE_SUB('2025-03-31', INTERVAL 90 DAY)  -- I couldn't use CURRENT_DATE because with won't return any data
  AND o.status = 'completed'
GROUP BY p.product_id, p.product_name, p.stock
ORDER BY total_units_sold DESC
LIMIT 5;


SELECT MIN(order_date), MAX(order_date) FROM orders;
