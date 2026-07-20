-- AOV by payment method + % of total revenue
SELECT
    pm.payment_method,
    ROUND(AVG(pm.amount), 2)                           AS avg_order_value,
    ROUND(SUM(pm.amount), 2)                           AS total_revenue,
    ROUND(
        SUM(pm.amount) / SUM(SUM(pm.amount)) OVER () * 100,
    2)                                                 AS revenue_pct
FROM payments pm
WHERE pm.status = 'success'
GROUP BY pm.payment_method
ORDER BY total_revenue DESC;
