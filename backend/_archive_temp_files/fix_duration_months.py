#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from sqlalchemy import create_engine, text
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Database connection
DATABASE_URL = "postgresql+psycopg://k3admin:KH%40123456@localhost:5432/ats_db"

def calculate_duration_months(start_date, end_date, is_current):
    """Calculate duration in months between two dates"""
    if not start_date:
        return 0
    
    # If no end date and is_current is True, use current date
    if not end_date and is_current:
        end_date = datetime.now().date()
    elif not end_date:
        return 0
    
    # Ensure dates are date objects
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Calculate difference in months
    diff = relativedelta(end_date, start_date)
    total_months = diff.years * 12 + diff.months
    
    # Add 1 month if there are any days (partial month counts as full month)
    if diff.days > 0:
        total_months += 1
    
    return max(total_months, 0)

def fix_duration_months():
    """Fix missing duration_months in work experience records"""
    try:
        engine = create_engine(DATABASE_URL)
        
        # Get all work experience records with missing duration_months
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    we.id,
                    we.candidate_id,
                    c.first_name,
                    c.last_name,
                    we.company_name,
                    we.job_title,
                    we.start_date,
                    we.end_date,
                    we.is_current,
                    we.duration_months
                FROM work_experience we
                JOIN candidates c ON we.candidate_id = c.id
                WHERE we.duration_months IS NULL 
                   OR we.duration_months = 0
                ORDER BY c.first_name, we.start_date
            """))
            
            records = result.fetchall()
            
            print("=== Fixing Duration Months ===")
            updated_count = 0
            
            for record in records:
                calculated_months = calculate_duration_months(
                    record.start_date, 
                    record.end_date, 
                    record.is_current
                )
                
                print(f"{record.first_name} {record.last_name} - {record.company_name}")
                print(f"  {record.job_title}")
                print(f"  Period: {record.start_date} to {record.end_date}")
                print(f"  Current: {record.is_current}")
                print(f"  Old duration: {record.duration_months}")
                print(f"  New duration: {calculated_months} months")
                
                if calculated_months > 0:
                    # Update the duration_months
                    with engine.begin() as trans:
                        trans.execute(text("""
                            UPDATE work_experience 
                            SET duration_months = :duration
                            WHERE id = :record_id
                        """), {
                            "duration": calculated_months,
                            "record_id": record.id
                        })
                    print(f"  ✅ Updated")
                    updated_count += 1
                else:
                    print(f"  ⚠️  Skipped (no valid dates)")
                print()
            
            print(f"Updated {updated_count} work experience records")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_duration_months()