#!/usr/bin/env python3
"""
Migration script to transfer existing JobSpy functionality to v2 architecture
"""

import sys
import os
from pathlib import Path

# Add original JobSpy to path
original_jobspy_path = Path(__file__).parent.parent.parent / "JobSpy"
sys.path.insert(0, str(original_jobspy_path))

try:
    from jobseeker import scrape_jobs
    from jobseeker.smart_router import smart_router
    print("Successfully imported original JobSpy modules")
except ImportError as e:
    print(f"Failed to import JobSpy modules: {e}")
    print("Make sure the original JobSpy project is available")

class JobSpyMigrator:
    def __init__(self):
        self.original_path = original_jobspy_path
        
    def test_original_functionality(self):
        """Test that original JobSpy still works"""
        try:
            # Test basic scraping
            result = scrape_jobs("indeed", "software engineer", "New York", 5)
            print(f"Original scraping works: {len(result)} jobs found")
            return True
        except Exception as e:
            print(f"Original scraping failed: {e}")
            return False