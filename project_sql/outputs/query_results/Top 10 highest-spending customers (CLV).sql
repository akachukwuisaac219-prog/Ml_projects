-- Top 10 highest-spending customers (CLV)
SELECT
    c.full_name,
    c.city,
    c.total_spent,
    COUNT(o.order_id)          AS total_orders,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.full_name, c.city, c.total_spent
ORDER BY c.total_spent DESC
LIMIT 10;
