-- Slow-moving products: < 5 units sold in last 6 months
WITH sales_6m AS (
    SELECT
        oi.product_id,
        SUM(oi.quantity)   AS total_units_sold,
        MAX(o.order_date)  AS last_sale_date
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_date >= DATE_SUB('2025-03-31', INTERVAL 6 MONTH)
    GROUP BY oi.product_id
)
SELECT
    p.product_name,
    COALESCE(s.total_units_sold, 0)  AS total_units_sold,
    s.last_sale_date,
    p.stock                          AS current_stock
FROM products p
LEFT JOIN sales_6m s ON p.product_id = s.product_id
WHERE COALESCE(s.total_units_sold, 0) < 5
ORDER BY total_units_sold ASC, p.stock DESC;


