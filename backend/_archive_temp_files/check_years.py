#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from sqlalchemy import create_engine, text

# Database connection
DATABASE_URL = "postgresql+psycopg://k3admin:KH%40123456@localhost:5432/ats_db"

try:
    engine = create_engine(DATABASE_URL)
    
    # Simple SQL query to check years of experience
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                first_name, 
                last_name, 
                years_of_experience,
                id
            FROM candidates 
            ORDER BY first_name
        """))
        
        print("=== Years of Experience in Database ===")
        for row in result:
            print(f"{row.first_name} {row.last_name}: {row.years_of_experience} years")
            
        print(f"\nTotal candidates: {result.rowcount}")
        
except Exception as e:
    print(f"Error: {e}")