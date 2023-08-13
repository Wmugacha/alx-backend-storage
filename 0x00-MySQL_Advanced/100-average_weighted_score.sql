-- Create the stored procedure
DELIMITER //
CREATE PROCEDURE ComputeAverageWeightedScoreForUser(IN user_id INT)
BEGIN
    DECLARE total_score DECIMAL(10, 2);
    DECLARE total_weight DECIMAL(10, 2);
    DECLARE average_weighted_score DECIMAL(10, 2);

    -- Initialize variables
    SET total_score = 0;
    SET total_weight = 0;

    -- Calculate the total weighted score and total weight
    SELECT SUM(score * weight), SUM(weight) INTO total_score, total_weight
    FROM corrections
    JOIN projects ON corrections.project_id = projects.id
    WHERE corrections.user_id = user_id;

    -- Calculate the average weighted score
    IF total_weight > 0 THEN
        SET average_weighted_score = total_score / total_weight;
    ELSE
        SET average_weighted_score = 0;
    END IF;

    -- Update the average weighted score in the users table
    UPDATE users SET average_score = average_weighted_score WHERE id = user_id;

END;
//
DELIMITER ;
