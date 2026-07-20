WITH recent_sales AS (
    SELECT
        oi.product_id,
        SUM(oi.quantity) AS units_sold_60d
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_date >= DATE_SUB('2025-03-31', INTERVAL 60 DAY)
      AND o.status = 'completed'
    GROUP BY oi.product_id
    HAVING SUM(oi.quantity) > 5
)
SELECT
    p.product_id,
    p.product_name,
    rs.units_sold_60d                                AS units_sold,
    p.stock                                          AS current_stock,
    ROUND(p.stock / (rs.units_sold_60d / 60.0), 1)  AS days_of_stock_left
FROM products p
JOIN recent_sales rs ON p.product_id = rs.product_id
WHERE p.stock < 50
ORDER BY days_of_stock_left ASC;