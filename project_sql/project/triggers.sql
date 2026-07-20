DELIMITER $$

-- Trigger 1: Reduce stock when order_item is inserted for a completed order
CREATE TRIGGER trg_reduce_stock_on_order
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    DECLARE v_status VARCHAR(20);
    SELECT status INTO v_status
    FROM orders WHERE order_id = NEW.order_id;

    IF v_status = 'completed' THEN
        UPDATE products
        SET stock = stock - NEW.quantity
        WHERE product_id = NEW.product_id;
    END IF;
END$$

-- Trigger 2: Restore stock when order is cancelled
CREATE TRIGGER trg_restore_stock_on_cancel
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
    IF OLD.status = 'completed' AND NEW.status = 'cancelled' THEN
        UPDATE products p
        JOIN order_items oi ON p.product_id = oi.product_id
        SET p.stock = p.stock + oi.quantity
        WHERE oi.order_id = NEW.order_id;
    END IF;
END$$

DELIMITER ;

