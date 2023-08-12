DELIMITER //
CREATE PROCEDURE ComputeAverageWeightedScoreForUsers()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE user_id INT;
    DECLARE total_score DECIMAL(10, 4);
    DECLARE total_weight DECIMAL(10, 4);
    DECLARE average_weighted_score DECIMAL(10, 4);

    -- Declare cursor for looping through users
    DECLARE users_cursor CURSOR FOR
        SELECT id FROM users;
        
    -- Declare continue handler for cursor
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Loop through users
    OPEN users_cursor;
    users_loop: LOOP
        FETCH users_cursor INTO user_id;
        IF done THEN
            LEAVE users_loop;
        END IF;

        -- Initialize variables
        SET total_score = 0;
        SET total_weight = 0;

        -- Calculate the total weighted score and total weight for the current user
        SELECT SUM(corrections.score * projects.weight), IFNULL(SUM(projects.weight), 0)
        INTO total_score, total_weight
        FROM corrections
        LEFT JOIN projects ON corrections.project_id = projects.id
        WHERE corrections.user_id = user_id;

        -- Calculate the average weighted score for the current user
        IF total_weight > 0 THEN
            SET average_weighted_score = total_score / total_weight;
        ELSE
            SET average_weighted_score = 0;
        END IF;

        -- Update the average weighted score in the users table
        UPDATE users SET average_score = average_weighted_score WHERE id = user_id;
    END LOOP;
    CLOSE users_cursor;
END;
//
DELIMITER ;
