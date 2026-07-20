-- Monthly Revenue Trend 2024–2025 with MoM growth %
WITH monthly AS (
    SELECT
        DATE_FORMAT(order_date, '%Y-%m')   AS month,
        SUM(total_amount)                  AS total_revenue,
        COUNT(*)                           AS total_orders
    FROM orders
    WHERE YEAR(order_date) IN (2024, 2025)
      AND status = 'completed'
    GROUP BY DATE_FORMAT(order_date, '%Y-%m')
)
SELECT
    month,
    total_revenue,
    total_orders, CONCAT(
    ROUND(
        (total_revenue - LAG(total_revenue) OVER (ORDER BY month))
        / NULLIF(LAG(total_revenue) OVER (ORDER BY month), 0) * 100,
    2), '%') AS mom_growth_pct
FROM monthly
ORDER BY month;
