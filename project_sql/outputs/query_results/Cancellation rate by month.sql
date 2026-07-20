-- Cancellation rate by month
SELECT
    DATE_FORMAT(order_date, '%Y-%m')     AS month,
    COUNT(*)                             AS total_orders,
    SUM(status = 'cancelled')            AS cancelled_orders,
    ROUND(
        SUM(status = 'cancelled') / COUNT(*) * 100,
    2)                                   AS cancellation_pct
FROM orders
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY cancellation_pct DESC;

-- To find the single highest cancellation month:
-- Add: LIMIT 1  (already sorted DESC by cancellation_pct)
