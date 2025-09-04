#!/usr/bin/env python3
"""
Demonstrate the 5-stage ETL process for JobSpy v2 with working data
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def demonstrate_etl_stages():
    """Demonstrate the 5-stage ETL process with sample data"""
    print("=" * 60)
    print("JobSpy v2 - 5-Stage ETL Process Demonstration")
    print("=" * 60)
    
    # Create test output directory
    test_output_dir = Path("test_output_demo")
    test_output_dir.mkdir(exist_ok=True)
    
    # Stage 1: Raw Data Extraction
    print("\n📊 Stage 1: Raw Data Extraction")
    print("   Extracting raw job data from Seek...")
    
    # Sample raw data (simulating what would be extracted from Seek)
    raw_jobs = [
        {
            "title": "Senior Software Engineer",
            "company": "TechCorp",
            "location": "Sydney, NSW",
            "salary": "$120,000 - $150,000",
            "description": "We are looking for a Senior Software Engineer to join our team...",
            "url": "https://www.seek.com.au/job/12345",
            "posted_date": "2025-09-01",
            "job_type": "Full Time"
        },
        {
            "title": "Frontend Developer",
            "company": "WebSolutions",
            "location": "Melbourne, VIC",
            "salary": "$90,000 - $110,000",
            "description": "Join our frontend team to build amazing web applications...",
            "url": "https://www.seek.com.au/job/67890",
            "posted_date": "2025-09-02",
            "job_type": "Full Time"
        }
    ]
    
    # Save raw data
    raw_data_file = test_output_dir / "raw_jobs.json"
    with open(raw_data_file, 'w', encoding='utf-8') as f:
        json.dump(raw_jobs, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Extracted {len(raw_jobs)} jobs")
    print(f"   📁 Raw data saved to: {raw_data_file}")
    
    # Stage 2: AI Processing
    print("\n🤖 Stage 2: AI Processing")
    print("   Processing jobs with AI to extract structured information...")
    
    # Sample AI processed data (simulating what AI would extract)
    ai_processed_jobs = []
    for job in raw_jobs:
        processed_job = job.copy()
        processed_job.update({
            "skills": ["Python", "JavaScript", "React", "AWS"],
            "experience_years": "5+",
            "education_required": "Bachelor's degree in Computer Science",
            "ai_confidence_score": 0.95,
            "ai_processing_timestamp": datetime.now().isoformat()
        })
        ai_processed_jobs.append(processed_job)
    
    # Save AI processed data
    ai_data_file = test_output_dir / "ai_processed_jobs.json"
    with open(ai_data_file, 'w', encoding='utf-8') as f:
        json.dump(ai_processed_jobs, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ AI processed {len(ai_processed_jobs)} jobs")
    print(f"   📁 AI data saved to: {ai_data_file}")
    
    # Stage 3: Data Cleaning
    print("\n🧹 Stage 3: Data Cleaning")
    print("   Cleaning and standardizing job data...")
    
    # Sample cleaned data (simulating what cleaning would do)
    cleaned_jobs = []
    for job in ai_processed_jobs:
        cleaned_job = job.copy()
        # Standardize location
        if "Sydney" in job["location"]:
            cleaned_job["location_standardized"] = "Sydney, Australia"
        elif "Melbourne" in job["location"]:
            cleaned_job["location_standardized"] = "Melbourne, Australia"
        
        # Parse salary
        salary_text = job["salary"]
        if "-" in salary_text:
            parts = salary_text.replace("$", "").replace(",", "").split(" - ")
            try:
                cleaned_job["salary_min"] = int(parts[0])
                cleaned_job["salary_max"] = int(parts[1])
            except:
                cleaned_job["salary_min"] = 0
                cleaned_job["salary_max"] = 0
        
        # Add cleaning metadata
        cleaned_job["cleaning_timestamp"] = datetime.now().isoformat()
        cleaned_job["data_quality_score"] = 0.98
        
        cleaned_jobs.append(cleaned_job)
    
    # Save cleaned data
    cleaned_data_file = test_output_dir / "cleaned_jobs.json"
    with open(cleaned_data_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_jobs, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Cleaned {len(cleaned_jobs)} jobs")
    print(f"   📁 Cleaned data saved to: {cleaned_data_file}")
    
    # Stage 4: Database Loading
    print("\n💾 Stage 4: Database Loading")
    print("   Loading jobs into database...")
    
    # Simulate database loading
    db_records_loaded = len(cleaned_jobs)
    print(f"   ✅ Loaded {db_records_loaded} records into database")
    
    # Stage 5: CSV Export
    print("\n📤 Stage 5: CSV Export")
    print("   Exporting jobs to CSV format...")
    
    # Create CSV export
    csv_file = test_output_dir / "jobs_export.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("title,company,location,salary_min,salary_max,posted_date,job_type,skills\n")
        
        # Write data
        for job in cleaned_jobs:
            skills = ";".join(job.get("skills", []))
            f.write(f"{job['title']},{job['company']},{job.get('location_standardized', job['location'])},{job.get('salary_min', 0)},{job.get('salary_max', 0)},{job['posted_date']},{job['job_type']},\"{skills}\"\n")
    
    print(f"   ✅ Exported {len(cleaned_jobs)} jobs to CSV")
    print(f"   📁 CSV export saved to: {csv_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ETL Process Summary")
    print("=" * 60)
    print(f"Total Jobs Processed: {len(raw_jobs)}")
    print(f"Stage 1 (Raw Data): ✅ Completed")
    print(f"Stage 2 (AI Processing): ✅ Completed")
    print(f"Stage 3 (Data Cleaning): ✅ Completed")
    print(f"Stage 4 (Database Load): ✅ Completed ({db_records_loaded} records)")
    print(f"Stage 5 (CSV Export): ✅ Completed")
    print(f"\n📁 All output files saved to: {test_output_dir}")
    
    # Show directory structure
    print(f"\n📂 Directory Structure:")
    print(f"   {test_output_dir}/")
    print(f"   ├── raw_jobs.json")
    print(f"   ├── ai_processed_jobs.json")
    print(f"   ├── cleaned_jobs.json")
    print(f"   └── jobs_export.csv")
    
    return True

def show_sample_data():
    """Show sample data from each stage"""
    print("\n" + "=" * 60)
    print("📋 Sample Data from Each Stage")
    print("=" * 60)
    
    test_output_dir = Path("test_output_demo")
    
    # Show raw data sample
    raw_file = test_output_dir / "raw_jobs.json"
    if raw_file.exists():
        with open(raw_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        print("\n📄 Stage 1 - Raw Data Sample:")
        print(json.dumps(raw_data[0], indent=2, ensure_ascii=False))
    
    # Show AI processed data sample
    ai_file = test_output_dir / "ai_processed_jobs.json"
    if ai_file.exists():
        with open(ai_file, 'r', encoding='utf-8') as f:
            ai_data = json.load(f)
        print("\n🤖 Stage 2 - AI Processed Sample:")
        print(json.dumps(ai_data[0], indent=2, ensure_ascii=False))
    
    # Show cleaned data sample
    cleaned_file = test_output_dir / "cleaned_jobs.json"
    if cleaned_file.exists():
        with open(cleaned_file, 'r', encoding='utf-8') as f:
            cleaned_data = json.load(f)
        print("\n🧹 Stage 3 - Cleaned Data Sample:")
        print(json.dumps(cleaned_data[0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    success = demonstrate_etl_stages()
    if success:
        show_sample_data()
        print("\n🎉 ETL demonstration completed successfully!")
    else:
        print("\n❌ ETL demonstration failed!")
        sys.exit(1)