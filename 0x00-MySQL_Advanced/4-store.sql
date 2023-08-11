-- SQL script that creates a trigger that decreases the quantity of an item after adding a new order
DELIMITER //

CREATE TRIGGER after_order_insert
AFTER INSERT ON orders
FOR EACH ROW
BEGIN
    DECLARE quantity_ordered INT;

    -- Get the quantity_ordered from the inserted order
    SET quantity_ordered = NEW.number;

    -- Decrease the quantity of the item in the items table
    UPDATE items
    SET quantity = quantity - quantity_ordered
    WHERE name = NEW.item_name;
END;
//

DELIMITER ;

