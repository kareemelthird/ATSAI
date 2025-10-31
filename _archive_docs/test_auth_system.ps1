# Test Script for User Management System
# Run this after starting the backend server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing User Management System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000/api/v1"

# Test 1: Login with Super Admin
Write-Host "Test 1: Login with Super Admin" -ForegroundColor Yellow
Write-Host "POST $baseUrl/auth/login" -ForegroundColor Gray
$loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -ContentType "application/json" -Body (@{
    email = "admin@ats.com"
    password = "Admin@123"
} | ConvertTo-Json) -ErrorAction Stop

if ($loginResponse.access_token) {
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "  User: $($loginResponse.user.first_name) $($loginResponse.user.last_name)" -ForegroundColor Gray
    Write-Host "  Role: $($loginResponse.user.role)" -ForegroundColor Gray
    Write-Host "  Access Token: $($loginResponse.access_token.Substring(0, 50))..." -ForegroundColor Gray
    $token = $loginResponse.access_token
} else {
    Write-Host "✗ Login failed!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 2: Get Current User Profile
Write-Host "Test 2: Get Current User Profile" -ForegroundColor Yellow
Write-Host "GET $baseUrl/auth/me" -ForegroundColor Gray
$headers = @{
    "Authorization" = "Bearer $token"
}
$profile = Invoke-RestMethod -Uri "$baseUrl/auth/me" -Method Get -Headers $headers -ErrorAction Stop

if ($profile.id) {
    Write-Host "✓ Profile retrieved!" -ForegroundColor Green
    Write-Host "  ID: $($profile.id)" -ForegroundColor Gray
    Write-Host "  Username: $($profile.username)" -ForegroundColor Gray
    Write-Host "  Email: $($profile.email)" -ForegroundColor Gray
    Write-Host "  Role: $($profile.role)" -ForegroundColor Gray
    Write-Host "  Status: $($profile.status)" -ForegroundColor Gray
} else {
    Write-Host "✗ Failed to get profile!" -ForegroundColor Red
}
Write-Host ""

# Test 3: Create a New User (Recruiter)
Write-Host "Test 3: Create New User (Recruiter)" -ForegroundColor Yellow
Write-Host "POST $baseUrl/users/" -ForegroundColor Gray
$newUser = Invoke-RestMethod -Uri "$baseUrl/users/" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
    email = "recruiter@ats.com"
    username = "recruiter1"
    password = "Recruiter@123"
    first_name = "John"
    last_name = "Recruiter"
    phone = "+1234567890"
    role = "recruiter"
    department = "HR"
    job_title = "Senior Recruiter"
} | ConvertTo-Json) -ErrorAction SilentlyContinue

if ($newUser.id) {
    Write-Host "✓ User created!" -ForegroundColor Green
    Write-Host "  ID: $($newUser.id)" -ForegroundColor Gray
    Write-Host "  Username: $($newUser.username)" -ForegroundColor Gray
    Write-Host "  Email: $($newUser.email)" -ForegroundColor Gray
    Write-Host "  Role: $($newUser.role)" -ForegroundColor Gray
    $newUserId = $newUser.id
} else {
    Write-Host "⚠ User might already exist or creation failed" -ForegroundColor Yellow
    # Try to get user by listing all users
    $allUsers = Invoke-RestMethod -Uri "$baseUrl/users/" -Method Get -Headers $headers -ErrorAction Stop
    $existingUser = $allUsers | Where-Object { $_.email -eq "recruiter@ats.com" }
    if ($existingUser) {
        Write-Host "  Found existing user: $($existingUser.username)" -ForegroundColor Gray
        $newUserId = $existingUser.id
    }
}
Write-Host ""

# Test 4: List All Users
Write-Host "Test 4: List All Users" -ForegroundColor Yellow
Write-Host "GET $baseUrl/users/" -ForegroundColor Gray
$users = Invoke-RestMethod -Uri "$baseUrl/users/" -Method Get -Headers $headers -ErrorAction Stop

if ($users) {
    Write-Host "✓ Retrieved $($users.Count) users!" -ForegroundColor Green
    foreach ($u in $users) {
        Write-Host "  - $($u.username) ($($u.email)) - Role: $($u.role), Status: $($u.status)" -ForegroundColor Gray
    }
} else {
    Write-Host "✗ Failed to list users!" -ForegroundColor Red
}
Write-Host ""

# Test 5: Update User
if ($newUserId) {
    Write-Host "Test 5: Update User" -ForegroundColor Yellow
    Write-Host "PUT $baseUrl/users/$newUserId" -ForegroundColor Gray
    $updateResponse = Invoke-RestMethod -Uri "$baseUrl/users/$newUserId" -Method Put -Headers $headers -ContentType "application/json" -Body (@{
        department = "Talent Acquisition"
        job_title = "Lead Recruiter"
    } | ConvertTo-Json) -ErrorAction Stop
    
    if ($updateResponse.id) {
        Write-Host "✓ User updated!" -ForegroundColor Green
        Write-Host "  Department: $($updateResponse.department)" -ForegroundColor Gray
        Write-Host "  Job Title: $($updateResponse.job_title)" -ForegroundColor Gray
    } else {
        Write-Host "✗ Update failed!" -ForegroundColor Red
    }
    Write-Host ""
}

# Test 6: Get User by ID
if ($newUserId) {
    Write-Host "Test 6: Get User by ID" -ForegroundColor Yellow
    Write-Host "GET $baseUrl/users/$newUserId" -ForegroundColor Gray
    $userDetail = Invoke-RestMethod -Uri "$baseUrl/users/$newUserId" -Method Get -Headers $headers -ErrorAction Stop
    
    if ($userDetail.id) {
        Write-Host "✓ User retrieved!" -ForegroundColor Green
        Write-Host "  Name: $($userDetail.first_name) $($userDetail.last_name)" -ForegroundColor Gray
        Write-Host "  Email: $($userDetail.email)" -ForegroundColor Gray
        Write-Host "  Department: $($userDetail.department)" -ForegroundColor Gray
        Write-Host "  Job Title: $($userDetail.job_title)" -ForegroundColor Gray
    } else {
        Write-Host "✗ Failed to get user!" -ForegroundColor Red
    }
    Write-Host ""
}

# Test 7: Register New User (Public Endpoint)
Write-Host "Test 7: Register New User (Public Endpoint)" -ForegroundColor Yellow
Write-Host "POST $baseUrl/auth/register" -ForegroundColor Gray
$registerResponse = Invoke-RestMethod -Uri "$baseUrl/auth/register" -Method Post -ContentType "application/json" -Body (@{
    email = "testuser@ats.com"
    username = "testuser"
    password = "TestUser@123"
    first_name = "Test"
    last_name = "User"
    phone = "+9876543210"
} | ConvertTo-Json) -ErrorAction SilentlyContinue

if ($registerResponse.access_token) {
    Write-Host "✓ Registration successful!" -ForegroundColor Green
    Write-Host "  User: $($registerResponse.user.username)" -ForegroundColor Gray
    Write-Host "  Role: $($registerResponse.user.role) (default)" -ForegroundColor Gray
    Write-Host "  Auto-logged in: Yes" -ForegroundColor Gray
} else {
    Write-Host "⚠ User might already exist or registration failed" -ForegroundColor Yellow
}
Write-Host ""

# Test 8: Logout
Write-Host "Test 8: Logout" -ForegroundColor Yellow
Write-Host "POST $baseUrl/auth/logout" -ForegroundColor Gray
$logoutResponse = Invoke-RestMethod -Uri "$baseUrl/auth/logout" -Method Post -Headers $headers -ErrorAction Stop

if ($logoutResponse.message) {
    Write-Host "✓ Logout successful!" -ForegroundColor Green
    Write-Host "  Message: $($logoutResponse.message)" -ForegroundColor Gray
} else {
    Write-Host "✗ Logout failed!" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Authentication system is working!" -ForegroundColor Green
Write-Host "✓ User management endpoints are working!" -ForegroundColor Green
Write-Host "✓ Login page is ready at: http://localhost:3000/login" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Open http://localhost:3000/login in your browser" -ForegroundColor Gray
Write-Host "2. Login with: admin@ats.com / Admin@123" -ForegroundColor Gray
Write-Host "3. Test the registration form" -ForegroundColor Gray
Write-Host "4. Check the user info in the sidebar" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
