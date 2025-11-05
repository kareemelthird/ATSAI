    -- SPECIFIC FIX for candidate be949f9c-9052-4091-a8b9-2f309f9fefb5
-- This candidate should have email kareemelthird@gmail.com instead of temp email

-- First, check the candidate's current info and their resume text
SELECT 
    c.id,
    c.first_name,
    c.last_name,
    c.email,
    r.original_filename,
    LEFT(r.extracted_text, 300) as cv_preview
FROM candidates c
LEFT JOIN resumes r ON c.id = r.candidate_id
WHERE c.id = 'be949f9c-9052-4091-a8b9-2f309f9fefb5';

-- Check if kareemelthird@gmail.com is already used by another candidate
SELECT 
    id,
    first_name,
    last_name,
    email,
    created_at
FROM candidates 
WHERE email = 'kareemelthird@gmail.com';

-- Extract email pattern from the resume text to verify
SELECT 
    c.id,
    c.first_name,
    c.last_name,
    c.email as current_email,
    SUBSTRING(r.extracted_text FROM '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}') as extracted_email_from_cv
FROM candidates c
JOIN resumes r ON c.id = r.candidate_id
WHERE c.id = 'be949f9c-9052-4091-a8b9-2f309f9fefb5';

-- If the email is not used by another candidate, update it
-- UNCOMMENT THE LINES BELOW AFTER CHECKING THE RESULTS ABOVE:

/*
UPDATE candidates 
SET 
    email = 'kareemelthird@gmail.com',
    updated_at = NOW()
WHERE id = 'be949f9c-9052-4091-a8b9-2f309f9fefb5'
    AND email LIKE 'temp_%@temp.com'
    -- Safety check: only update if kareemelthird@gmail.com is not used by another candidate
    AND NOT EXISTS (
        SELECT 1 FROM candidates 
        WHERE email = 'kareemelthird@gmail.com' 
        AND id != 'be949f9c-9052-4091-a8b9-2f309f9fefb5'
    );
*/

    -- Verify the update
    SELECT 
        id,
        first_name,
        last_name,
        email,
        updated_at,
        'Email fixed!' as status
    FROM candidates 
    WHERE id = 'be949f9c-9052-4091-a8b9-2f309f9fefb5';