-- Customer retention: 2024 joiners active in 2025
WITH joiners_2024 AS (
    SELECT customer_id FROM customers WHERE YEAR(join_date) = 2024
),
active_in_2025 AS (
    SELECT DISTINCT o.customer_id
    FROM orders o
    JOIN joiners_2024 j ON o.customer_id = j.customer_id
    WHERE YEAR(o.order_date) = 2025
)
SELECT
    COUNT(j.customer_id)                                AS total_2024_joiners,
    COUNT(a.customer_id)                                AS active_in_2025,
    ROUND(COUNT(a.customer_id) / COUNT(j.customer_id) * 100, 2) AS retention_pct
FROM joiners_2024 j
LEFT JOIN active_in_2025 a ON j.customer_id = a.customer_id;

