-- Revenue by product category with ranking
SELECT
    cat.category_name,
    ROUND(SUM(oi.quantity * oi.item_price), 2)            AS total_revenue,
    ROUND(
        SUM(oi.quantity * oi.item_price)
        / SUM(SUM(oi.quantity * oi.item_price)) OVER () * 100,
    2)                                                     AS revenue_pct,
    RANK() OVER (ORDER BY SUM(oi.quantity * oi.item_price) DESC) AS revenue_rank
FROM order_items oi
JOIN products p    ON oi.product_id  = p.product_id
JOIN categories cat ON p.category_id = cat.category_id
JOIN orders o      ON oi.order_id    = o.order_id
WHERE o.status = 'completed'
GROUP BY cat.category_id, cat.category_name
ORDER BY revenue_rank;
