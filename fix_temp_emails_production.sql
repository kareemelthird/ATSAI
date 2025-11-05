-- Fix existing candidates with temp emails by extracting real emails from their CV text
-- This script will update candidates who have temp emails but real emails in their uploaded CVs

-- First, let's see how many candidates have temp emails
SELECT 
    COUNT(*) as temp_email_candidates,
    COUNT(CASE WHEN original_resume_text IS NOT NULL THEN 1 END) as with_cv_text
FROM candidates 
WHERE email LIKE 'temp_%@temp.com';

-- Show some examples of candidates with temp emails and their CV text
SELECT 
    id,
    first_name,
    last_name,
    email,
    LEFT(original_resume_text, 200) as cv_preview
FROM candidates 
WHERE email LIKE 'temp_%@temp.com' 
    AND original_resume_text IS NOT NULL
LIMIT 5;

-- Update candidates by extracting emails from their CV text
-- This uses PostgreSQL's regex functions to find email patterns in the CV text

UPDATE candidates 
SET email = SUBSTRING(
    original_resume_text FROM '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
)
WHERE email LIKE 'temp_%@temp.com' 
    AND original_resume_text IS NOT NULL
    AND original_resume_text ~ '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    -- Only update if we can find a valid email pattern in the CV text
    AND SUBSTRING(original_resume_text FROM '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}') IS NOT NULL;

-- Show results after update
SELECT 
    'After Update' as status,
    COUNT(*) as remaining_temp_emails
FROM candidates 
WHERE email LIKE 'temp_%@temp.com';

-- Show the candidates that were successfully updated
SELECT 
    id,
    first_name,
    last_name,
    email,
    'Updated from CV' as status
FROM candidates 
WHERE updated_at > NOW() - INTERVAL '1 minute'
    AND email NOT LIKE 'temp_%@temp.com'
ORDER BY updated_at DESC
LIMIT 10;