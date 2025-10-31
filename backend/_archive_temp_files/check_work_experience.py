#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from sqlalchemy import create_engine, text

# Database connection
DATABASE_URL = "postgresql+psycopg://k3admin:KH%40123456@localhost:5432/ats_db"

def check_work_experience_data():
    """Check work experience data for candidates with 0 years"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Get candidates with 0 years and their work experience
            result = conn.execute(text("""
                SELECT 
                    c.first_name, 
                    c.last_name, 
                    c.years_of_experience,
                    COUNT(we.id) as work_experience_count,
                    COALESCE(SUM(we.duration_months), 0) as total_months
                FROM candidates c
                LEFT JOIN work_experience we ON c.id = we.candidate_id
                WHERE c.years_of_experience = 0
                GROUP BY c.id, c.first_name, c.last_name, c.years_of_experience
                ORDER BY c.first_name
            """))
            
            candidates = result.fetchall()
            
            print("=== Candidates with 0 Years - Work Experience Analysis ===")
            for candidate in candidates:
                print(f"{candidate.first_name} {candidate.last_name}:")
                print(f"  Work Experience Records: {candidate.work_experience_count}")
                print(f"  Total Months: {candidate.total_months}")
                print()
                
            # Check specific work experience records for sample candidates
            print("=== Sample Work Experience Records ===")
            sample_result = conn.execute(text("""
                SELECT 
                    c.first_name, 
                    c.last_name,
                    we.company_name,
                    we.job_title,
                    we.start_date,
                    we.end_date,
                    we.duration_months,
                    we.is_current
                FROM candidates c
                JOIN work_experience we ON c.id = we.candidate_id
                WHERE c.years_of_experience = 0
                ORDER BY c.first_name, we.start_date
                LIMIT 20
            """))
            
            for record in sample_result:
                print(f"{record.first_name} {record.last_name} - {record.company_name}")
                print(f"  Title: {record.job_title}")
                print(f"  Period: {record.start_date} to {record.end_date}")
                print(f"  Duration: {record.duration_months} months")
                print(f"  Current: {record.is_current}")
                print()
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_work_experience_data()