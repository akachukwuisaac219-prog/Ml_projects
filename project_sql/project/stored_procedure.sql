DELIMITER $$

CREATE PROCEDURE sp_cancel_order(IN p_order_id INT, OUT p_message VARCHAR(255))
BEGIN
    DECLARE v_status VARCHAR(20);
    DECLARE v_done BOOLEAN DEFAULT FALSE;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_message = 'ERROR: Order cancellation failed. Transaction rolled back.';
    END;

    -- Validate order exists
    SELECT status INTO v_status 
    FROM orders 
    WHERE order_id = p_order_id;

    IF v_status IS NULL THEN
        SET p_message = 'ERROR: Order not found.';
        SET v_done = TRUE;
    END IF;

    IF v_status = 'cancelled' AND v_done = FALSE THEN
        SET p_message = 'INFO: Order is already cancelled.';
        SET v_done = TRUE;
    END IF;

    IF v_done = FALSE THEN
        START TRANSACTION;

        -- Step 1: Change order status to cancelled
        UPDATE orders 
        SET status = 'cancelled' 
        WHERE order_id = p_order_id;

        -- Step 2: Restore stock for all items in the order
        UPDATE products p
        JOIN order_items oi ON p.product_id = oi.product_id
        SET p.stock = p.stock + oi.quantity
        WHERE oi.order_id = p_order_id;

        -- Step 3: Mark payment as failed if previously successful
        UPDATE payments
        SET status = 'failed'
        WHERE order_id = p_order_id 
          AND status = 'success';

        COMMIT;
        SET p_message = CONCAT('SUCCESS: Order #', p_order_id, 
                               ' has been cancelled and stock restored.');
    END IF;

END$$

DELIMITER ;


-- Usage:
CALL sp_cancel_order(7, @msg);
SELECT @msg;


