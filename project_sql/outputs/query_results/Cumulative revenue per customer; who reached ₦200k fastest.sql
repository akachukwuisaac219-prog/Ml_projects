-- Cumulative revenue per customer; who reached ₦200k fastest?
WITH cumulative AS (
    SELECT
        c.customer_id,
        c.full_name,
        o.order_date,
        o.total_amount,
        SUM(o.total_amount) OVER (
            PARTITION BY c.customer_id
            ORDER BY o.order_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_revenue,
        ROW_NUMBER() OVER (
            PARTITION BY c.customer_id ORDER BY o.order_date
        ) AS order_seq
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.status = 'completed'
),
first_200k AS (
    SELECT customer_id, full_name, order_date AS reached_200k_on
    FROM (
        SELECT *,
            LAG(cumulative_revenue) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_cum
        FROM cumulative
    ) t
    WHERE cumulative_revenue >= 200000
      AND (prev_cum IS NULL OR prev_cum < 200000)
)
SELECT
    full_name,
    reached_200k_on,
    DATEDIFF(reached_200k_on,
        (SELECT MIN(join_date) FROM customers c2
         WHERE c2.customer_id = f.customer_id)) AS days_to_reach
FROM first_200k f
ORDER BY reached_200k_on ASC
LIMIT 10;

