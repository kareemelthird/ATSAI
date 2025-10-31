#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from sqlalchemy import create_engine, text
from datetime import datetime

# Database connection
DATABASE_URL = "postgresql+psycopg://k3admin:KH%40123456@localhost:5432/ats_db"

def calculate_total_years_of_experience_sql(candidate_id):
    """Calculate total years of experience using SQL"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Get total months from work experience
            result = conn.execute(text("""
                SELECT COALESCE(SUM(duration_months), 0) as total_months
                FROM work_experience 
                WHERE candidate_id = :candidate_id
            """), {"candidate_id": candidate_id})
            
            total_months = result.scalar() or 0
            return round(total_months / 12, 1)
    except Exception as e:
        print(f"Error calculating years for {candidate_id}: {e}")
        return 0

def update_years_for_all_candidates():
    """Update years of experience for all candidates"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Get all candidates
            result = conn.execute(text("""
                SELECT id, first_name, last_name, years_of_experience
                FROM candidates 
                ORDER BY first_name
            """))
            
            candidates = result.fetchall()
            
            print("=== Updating Years of Experience ===")
            updated_count = 0
            
            for candidate in candidates:
                candidate_id = candidate.id
                current_years = candidate.years_of_experience or 0
                calculated_years = calculate_total_years_of_experience_sql(candidate_id)
                
                print(f"{candidate.first_name} {candidate.last_name}:")
                print(f"  Current in DB: {current_years} years")
                print(f"  Calculated: {calculated_years} years")
                
                if current_years != calculated_years:
                    # Update the candidate
                    with engine.begin() as trans:
                        trans.execute(text("""
                            UPDATE candidates 
                            SET years_of_experience = :years,
                                updated_at = :updated_at
                            WHERE id = :candidate_id
                        """), {
                            "years": calculated_years,
                            "updated_at": datetime.utcnow(),
                            "candidate_id": candidate_id
                        })
                    print(f"  ✅ Updated to {calculated_years} years")
                    updated_count += 1
                else:
                    print(f"  ✅ Already correct")
                print()
            
            print(f"Updated {updated_count} candidates")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_years_for_all_candidates()