-- PRODUCTION FIX: Update candidates with temp emails using their CV text
-- Run this on your Vercel/Supabase PostgreSQL database

-- Step 1: Check how many candidates have temp emails
SELECT 
    'Before Fix' as status,
    COUNT(*) as temp_email_count
FROM candidates 
WHERE email LIKE 'temp_%@temp.com';

-- Step 2: Show candidates with temp emails that have CV text
SELECT 
    c.id,
    c.first_name,
    c.last_name,
    c.email,
    CASE 
        WHEN r.extracted_text IS NULL THEN 'No CV text'
        WHEN LENGTH(r.extracted_text) < 50 THEN 'CV text too short'
        ELSE 'Has CV text'
    END as cv_status,
    CASE 
        WHEN r.extracted_text ~ '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' 
        THEN 'Email found in CV'
        ELSE 'No email in CV'
    END as email_status
FROM candidates c
LEFT JOIN resumes r ON c.id = r.candidate_id
WHERE c.email LIKE 'temp_%@temp.com'
ORDER BY c.created_at DESC;

-- Step 3: Extract and show what emails would be found
SELECT 
    c.id,
    c.first_name,
    c.last_name,
    c.email as current_temp_email,
    SUBSTRING(
        r.extracted_text FROM '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    ) as extracted_email
FROM candidates c
JOIN resumes r ON c.id = r.candidate_id
WHERE c.email LIKE 'temp_%@temp.com' 
    AND r.extracted_text IS NOT NULL
    AND r.extracted_text ~ '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
ORDER BY c.created_at DESC;

-- Step 4: ACTUAL UPDATE (uncomment and run this after reviewing results above)
/*
UPDATE candidates 
SET 
    email = (
        SELECT SUBSTRING(r.extracted_text FROM '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        FROM resumes r 
        WHERE r.candidate_id = candidates.id
        AND r.extracted_text ~ '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        LIMIT 1
    ),
    updated_at = NOW()
WHERE email LIKE 'temp_%@temp.com' 
    AND EXISTS (
        SELECT 1 FROM resumes r 
        WHERE r.candidate_id = candidates.id
        AND r.extracted_text ~ '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    )
    -- Safety check: don't update if extracted email already exists for another candidate
    AND NOT EXISTS (
        SELECT 1 FROM candidates c2 
        WHERE c2.email = (
            SELECT SUBSTRING(r.extracted_text FROM '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
            FROM resumes r 
            WHERE r.candidate_id = candidates.id
            LIMIT 1
        )
        AND c2.id != candidates.id
    );
*/

-- Step 5: Check results after update
SELECT 
    'After Fix' as status,
    COUNT(*) as remaining_temp_emails
FROM candidates 
WHERE email LIKE 'temp_%@temp.com';

-- Step 6: Show recently updated candidates
SELECT 
    id,
    first_name,
    last_name,
    email,
    'Fixed email' as status,
    updated_at
FROM candidates 
WHERE updated_at > NOW() - INTERVAL '5 minutes'
    AND email NOT LIKE 'temp_%@temp.com'
ORDER BY updated_at DESC;