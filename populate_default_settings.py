#!/usr/bin/env python3

import requests
import json

def populate_default_settings():
    """Populate the database with default settings like we did locally"""
    
    print("🔧 Populating default settings...")
    print("-" * 60)
    
    # Login first
    auth_data = {"email": "admin@ats.com", "password": "admin123"}
    
    auth_response = requests.post(
        "https://atsai-jade.vercel.app/api/v1/auth/login",
        json=auth_data,
        headers={"Content-Type": "application/json"}
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.text}")
        return
        
    token = auth_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Default settings that should exist (based on local setup)
    default_settings = [
        # AI Configuration
        {
            "category": "ai_provider",
            "key": "AI_PROVIDER", 
            "value": "openrouter",
            "label": "AI Provider",
            "description": "Primary AI service provider",
            "data_type": "string"
        },
        {
            "category": "ai_provider",
            "key": "OPENROUTER_API_KEY",
            "value": "",
            "label": "OpenRouter API Key", 
            "description": "API key for OpenRouter service",
            "data_type": "string",
            "is_encrypted": True
        },
        {
            "category": "ai_provider", 
            "key": "GROQ_API_KEY",
            "value": "",
            "label": "Groq API Key",
            "description": "API key for Groq service",
            "data_type": "string",
            "is_encrypted": True
        },
        {
            "category": "ai_provider",
            "key": "AI_MODEL",
            "value": "anthropic/claude-3.5-sonnet",
            "label": "Default AI Model",
            "description": "Default model to use for AI operations",
            "data_type": "string"
        },
        
        # Database
        {
            "category": "database",
            "key": "DATABASE_URL",
            "value": "",
            "label": "Database Connection URL",
            "description": "PostgreSQL connection string",
            "data_type": "string",
            "is_encrypted": True,
            "requires_restart": True
        },
        
        # Application Settings
        {
            "category": "application",
            "key": "APP_NAME",
            "value": "ATS AI",
            "label": "Application Name", 
            "description": "Name of the application",
            "data_type": "string"
        },
        {
            "category": "application",
            "key": "APP_VERSION",
            "value": "1.0.0",
            "label": "Application Version",
            "description": "Current version of the application", 
            "data_type": "string"
        },
        {
            "category": "application",
            "key": "UPLOAD_LIMIT_MB",
            "value": "10",
            "label": "Upload Limit (MB)",
            "description": "Maximum file upload size in megabytes",
            "data_type": "integer"
        },
        
        # Security
        {
            "category": "security",
            "key": "JWT_SECRET_KEY",
            "value": "",
            "label": "JWT Secret Key",
            "description": "Secret key for JWT token signing",
            "data_type": "string",
            "is_encrypted": True,
            "requires_restart": True
        },
        {
            "category": "security", 
            "key": "SESSION_TIMEOUT_MINUTES",
            "value": "1440",
            "label": "Session Timeout (Minutes)",
            "description": "User session timeout in minutes",
            "data_type": "integer"
        },
        
        # Server Configuration
        {
            "category": "server",
            "key": "SERVER_HOST",
            "value": "0.0.0.0",
            "label": "Server Host",
            "description": "Server bind address",
            "data_type": "string"
        },
        {
            "category": "server",
            "key": "SERVER_PORT", 
            "value": "8000",
            "label": "Server Port",
            "description": "Server port number",
            "data_type": "integer"
        },
        
        # AI Instructions (the missing ones for chat)
        {
            "category": "ai_provider",
            "key": "RESUME_ANALYSIS_INSTRUCTIONS",
            "value": "Analyze the resume comprehensively, extracting key information about skills, experience, education, and qualifications. Provide structured insights about the candidate's strengths and potential fit for various roles.",
            "label": "Resume Analysis Instructions",
            "description": "Instructions for AI resume analysis",
            "data_type": "text"
        },
        {
            "category": "ai_provider", 
            "key": "CHAT_SYSTEM_INSTRUCTIONS",
            "value": "You are an AI assistant for an Applicant Tracking System. Help users with recruitment tasks, candidate evaluation, resume analysis, and HR-related questions. Be professional, helpful, and accurate.",
            "label": "Chat System Instructions",
            "description": "System instructions for AI chat interactions",
            "data_type": "text"
        }
    ]
    
    print(f"🔧 Creating {len(default_settings)} default settings...")
    
    for setting in default_settings:
        print(f"\n   Creating: {setting['key']}")
        try:
            response = requests.post(
                "https://atsai-jade.vercel.app/api/v1/settings/",
                json=setting,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                print(f"   ✅ Created successfully")
            elif response.status_code == 409:
                print(f"   ⚠️  Already exists")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n🔧 Default settings population complete!")
    print("🔧 You can now refresh the Settings page to see the populated values.")

if __name__ == "__main__":
    populate_default_settings()