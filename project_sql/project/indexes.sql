-- Composite index on orders: covers JOIN key + filter + sort
CREATE INDEX idx_orders_date_amount
    ON orders (order_date, total_amount DESC, customer_id);

-- Index on customers.customer_id (already PK, no extra index needed)
-- But add covering index for the join + common report fields:
CREATE INDEX idx_customers_id_city_spent
    ON customers (customer_id, city, total_spent);

-- Composite index on order_items for order-level aggregations:
CREATE INDEX idx_order_items_order_product
    ON order_items (order_id, product_id, quantity, item_price);

-- EXPLAIN output after indexing:
EXPLAIN SELECT o.*, c.*
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= DATE_SUB(CURRENT_DATE, INTERVAL 90 DAY)
ORDER BY o.total_amount DESC;

-- Expected EXPLAIN improvement:
-- type: range (uses idx_orders_date_amount) instead of ALL
-- key: idx_orders_date_amount
-- Extra: Using index condition; Using filesort reduced/eliminated
-- rows examined: dramatically reduced from full table scan


