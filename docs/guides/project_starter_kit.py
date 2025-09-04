#!/usr/bin/env python3
"""
JobSpy Modernization Project Starter Kit
Automated setup script for the new tech stack architecture
"""

import os
import subprocess
import sys
from pathlib import Path
import json

class JobSpyModernizer:
    def __init__(self, project_root: str = "JobSpy-v2"):
        self.project_root = Path(project_root)
        self.current_dir = Path.cwd()
        
    def setup_project_structure(self):
        """Create the complete project directory structure"""
        print("Creating project structure...")
        
        directories = [
            "backend/app/api/v1",
            "backend/app/core",
            "backend/app/models",
            "backend/app/services",
            "backend/app/legacy",
            "backend/tests/unit",
            "backend/tests/integration",
            "backend/scripts",
            
            "frontend/src/components",
            "frontend/src/pages", 
            "frontend/src/services",
            "frontend/src/stores",
            "frontend/src/types",
            "frontend/src/utils",
            "frontend/public",
            "frontend/tests",
            
            "shared/types",
            "shared/utils",
            "shared/configs",
            
            "docker/dev",
            "docker/prod",
            
            "docs/api",
            "docs/frontend",
            "docs/deployment",
            
            "scripts/migration",
            "scripts/deployment",
            "scripts/monitoring",
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created: {directory}")
    
    def create_backend_foundation(self):
        """Set up FastAPI backend foundation"""
        print("Setting up FastAPI backend...")
        
        # Main FastAPI application
        main_py = '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import jobs, ai, users
from app.core.config import settings

app = FastAPI(
    title="JobSpy API v2",
    description="Modern AI-enhanced job search platform",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

@app.get("/")
async def root():
    return {"message": "JobSpy API v2 - Ready for AI-enhanced job searching!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
'''
        
        # Configuration
        config_py = '''
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost/jobspy"
    redis_url: str = "redis://localhost:6379"
    
    # AI Services
    openai_api_key: Optional[str] = None
    google_vision_api_key: Optional[str] = None
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Settings
    max_requests_per_minute: int = 100
    max_ai_requests_per_day: int = 1000
    
    class Config:
        env_file = ".env"

settings = Settings()
'''
        
        # Jobs router
        jobs_router = '''
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.services.job_search import JobSearchService
from app.models.job import JobSearchRequest, JobSearchResponse

router = APIRouter()

@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(
    request: JobSearchRequest,
    job_service: JobSearchService = Depends()
):
    """Enhanced job search with AI vision capabilities"""
    try:
        result = await job_service.search_with_ai_enhancement(
            query=request.query,
            location=request.location,
            results_wanted=request.results_wanted,
            use_ai_vision=request.use_ai_vision
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sites")
async def get_supported_sites():
    """Get list of supported job sites"""
    return {
        "sites": [
            {"name": "indeed", "region": "global", "ai_enhanced": True},
            {"name": "linkedin", "region": "global", "ai_enhanced": True},
            {"name": "glassdoor", "region": "global", "ai_enhanced": True},
        ]
    }
'''
        
        # AI router
        ai_router = '''
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ai_vision import AIVisionService
from app.core.config import settings

router = APIRouter()

@router.post("/analyze-page")
async def analyze_job_page(
    file: UploadFile = File(...),
    ai_service: AIVisionService = Depends()
):
    """Analyze job page screenshot with AI vision"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        image_data = await file.read()
        result = await ai_service.analyze_job_page(image_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.get("/usage")
async def get_ai_usage():
    """Get AI service usage statistics"""
    # TODO: Implement usage tracking
    return {"daily_usage": 0, "limit": settings.max_ai_requests_per_day}
'''
        
        # Write files
        files = {
            "backend/app/main.py": main_py,
            "backend/app/core/config.py": config_py,
            "backend/app/api/v1/jobs.py": jobs_router,
            "backend/app/api/v1/ai.py": ai_router,
            "backend/app/api/__init__.py": "",
            "backend/app/api/v1/__init__.py": "",
            "backend/app/core/__init__.py": "",
            "backend/app/models/__init__.py": "",
            "backend/app/services/__init__.py": "",
        }
        
        for file_path, content in files.items():
            full_path = self.project_root / file_path
            full_path.write_text(content.strip())
            print(f"  ✅ Created: {file_path}")
    
    def create_frontend_foundation(self):
        """Set up React TypeScript frontend"""
        print("Setting up React frontend...")
        
        # Package.json
        package_json = {
            "name": "jobspy-frontend",
            "private": True,
            "version": "2.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview",
                "test": "vitest"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "@tanstack/react-query": "^4.32.0",
                "zustand": "^4.4.0",
                "axios": "^1.5.0",
                "react-router-dom": "^6.15.0",
                "tailwindcss": "^3.3.0",
                "@headlessui/react": "^1.7.0",
                "framer-motion": "^10.16.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.15",
                "@types/react-dom": "^18.2.7",
                "@vitejs/plugin-react": "^4.0.3",
                "typescript": "^5.0.2",
                "vite": "^4.4.5",
                "vitest": "^0.34.0"
            }
        }
        
        # Main App component
        app_tsx = '''
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SearchPage } from './pages/SearchPage';
import { ResultsPage } from './pages/ResultsPage';
import './App.css';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <header className="bg-white shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <h1 className="text-2xl font-bold text-gray-900">
                JobSpy v2 - AI-Enhanced Job Search
              </h1>
            </div>
          </header>
          
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <Routes>
              <Route path="/" element={<SearchPage />} />
              <Route path="/results" element={<ResultsPage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
'''
        
        # Search page
        search_page = '''
import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { searchJobs } from '../services/api';

export const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [useAI, setUseAI] = useState(true);
  
  const searchMutation = useMutation({
    mutationFn: searchJobs,
    onSuccess: (data) => {
      console.log('Search results:', data);
    },
  });
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    searchMutation.mutate({
      query,
      location,
      results_wanted: 20,
      use_ai_vision: useAI
    });
  };
  
  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white p-8 rounded-lg shadow-lg">
        <h2 className="text-xl font-semibold mb-6">Search for Jobs</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Job Title or Keywords
            </label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="e.g. Software Engineer, Data Scientist"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Location (Optional)
            </label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="e.g. New York, London, Remote"
            />
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              id="useAI"
              checked={useAI}
              onChange={(e) => setUseAI(e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="useAI" className="text-sm text-gray-700">
              Enable AI-Enhanced Scraping (Beta)
            </label>
          </div>
          
          <button
            type="submit"
            disabled={searchMutation.isLoading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {searchMutation.isLoading ? 'Searching...' : 'Search Jobs'}
          </button>
        </form>
        
        {searchMutation.error && (
          <div className="mt-4 p-4 bg-red-50 rounded-md">
            <p className="text-red-800">
              Error: {(searchMutation.error as Error).message}
            </p>
          </div>
        )}
        
        {searchMutation.data && (
          <div className="mt-6">
            <h3 className="font-semibold mb-2">Search Results</h3>
            <p>Found {searchMutation.data.total_jobs} jobs</p>
            {/* TODO: Display job results */}
          </div>
        )}
      </div>
    </div>
  );
};
'''
        
        # API service
        api_service = '''
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

export interface JobSearchRequest {
  query: string;
  location?: string;
  results_wanted?: number;
  use_ai_vision?: boolean;
}

export interface JobListing {
  title: string;
  company: string;
  location: string;
  salary?: string;
  description: string;
  job_url: string;
  site: string;
}

export interface JobSearchResponse {
  jobs: JobListing[];
  total_jobs: number;
  successful_sites: string[];
  confidence_score: number;
  ai_enhanced: boolean;
}

export const searchJobs = async (request: JobSearchRequest): Promise<JobSearchResponse> => {
  const response = await api.post('/jobs/search', request);
  return response.data;
};

export const getSupportedSites = async () => {
  const response = await api.get('/jobs/sites');
  return response.data;
};
'''
        
        # Write frontend files
        frontend_files = {
            "frontend/package.json": json.dumps(package_json, indent=2),
            "frontend/src/App.tsx": app_tsx,
            "frontend/src/pages/SearchPage.tsx": search_page,
            "frontend/src/pages/ResultsPage.tsx": "export const ResultsPage = () => <div>Results Page - Coming Soon</div>;",
            "frontend/src/services/api.ts": api_service,
            "frontend/src/main.tsx": '''
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
''',
            "frontend/src/index.css": "@tailwind base;\n@tailwind components;\n@tailwind utilities;",
        }
        
        for file_path, content in frontend_files.items():
            full_path = self.project_root / file_path
            full_path.write_text(content.strip())
            print(f"  ✅ Created: {file_path}")
    
    def create_docker_setup(self):
        """Create Docker development environment"""
        print("Setting up Docker environment...")
        
        docker_compose = '''
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql://jobspy:password@postgres:5432/jobspy
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: jobspy
      POSTGRES_PASSWORD: password
      POSTGRES_DB: jobspy
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
'''
        
        backend_dockerfile = '''
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright
RUN playwright install chromium
RUN playwright install-deps

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        
        frontend_dockerfile = '''
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
'''
        
        docker_files = {
            "docker-compose.yml": docker_compose,
            "backend/Dockerfile": backend_dockerfile,
            "frontend/Dockerfile": frontend_dockerfile,
            ".env.example": '''
# Database
DATABASE_URL=postgresql://jobspy:password@localhost:5432/jobspy
REDIS_URL=redis://localhost:6379

# AI Services
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_VISION_API_KEY=your_google_vision_api_key_here

# Security
SECRET_KEY=your_secret_key_here
''',
        }
        
        for file_path, content in docker_files.items():
            full_path = self.project_root / file_path
            full_path.write_text(content.strip())
            print(f"  ✅ Created: {file_path}")
    
    def create_migration_script(self):
        """Create script to migrate existing JobSpy data"""
        print("Creating migration utilities...")
        
        migration_script = '''
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
'''
        
        wrapper_code = '''
import asyncio
from typing import Dict, List, Any
import sys
from pathlib import Path

# Import original JobSpy
original_path = Path(__file__).parent.parent / "legacy"
sys.path.insert(0, str(original_path))

from jobseeker import scrape_jobs
from jobseeker.smart_router import smart_router

class LegacyJobSearchWrapper:
    """Async wrapper for original JobSpy functionality"""
    
    async def search_jobs_async(self, query: str, location: str = "", results_wanted: int = 20) -> Dict[str, Any]:
        """Async wrapper for original job search"""
        loop = asyncio.get_event_loop()
        
        # Run original synchronous function in thread pool
        result = await loop.run_in_executor(
            None,
            lambda: smart_router(query, location, results_wanted)
        )
        
        return {
            "jobs": result.combined_jobs_data.to_dict('records') if result.combined_jobs_data is not None else [],
            "total_jobs": result.total_jobs,
            "successful_agents": [agent.value for agent in result.successful_agents],
            "confidence_score": result.confidence_score,
            "processing_time": getattr(result, 'processing_time', 0)
        }
    
    async def scrape_specific_site(self, site: str, query: str, location: str, results: int) -> List[Dict]:
        """Async wrapper for site-specific scraping"""
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            None,
            lambda: scrape_jobs(site, query, location, results)
        )
        
        return result.to_dict('records') if hasattr(result, 'to_dict') else []
'''
        
        migration_files = {
            "scripts/migration/migrate_legacy.py": migration_script,
            "backend/app/legacy/wrapper.py": wrapper_code,
        }
        
        for file_path, content in migration_files.items():
            full_path = self.project_root / file_path
            full_path.write_text(content.strip())
            print(f"  Created: {file_path}")
    
    def generate_readme(self):
        """Generate comprehensive README for the new project"""
        readme_content = """# JobSpy v2 - AI-Enhanced Job Search Platform

## Modern Architecture

This is the modernized version of JobSpy, featuring:

- FastAPI Backend: High-performance async API
- React + TypeScript Frontend: Modern, responsive UI  
- AI Vision Integration: OpenAI GPT-4V for intelligent scraping
- Microservices Architecture: Scalable and maintainable
- Docker Support: Easy development and deployment

## Project Structure

    JobSpy-v2/
    |-- backend/           # FastAPI backend application
    |-- frontend/          # React TypeScript frontend
    |-- shared/            # Shared types and utilities
    |-- docker/            # Docker configurations
    |-- scripts/           # Utility scripts
    |-- docs/              # Documentation

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- OpenAI API Key (for AI features)

### Quick Start

1. Clone and setup:
   git clone <repository>
   cd JobSpy-v2
   cp .env.example .env

2. Start with Docker:
   docker-compose up -d

3. Access applications:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Configuration

Create .env file with:

    DATABASE_URL=postgresql://jobspy:password@localhost:5432/jobspy
    REDIS_URL=redis://localhost:6379
    OPENAI_API_KEY=your_openai_api_key_here
    SECRET_KEY=your_secret_key_here

## Testing

    # Backend tests
    cd backend
    pytest
    
    # Frontend tests
    cd frontend
    npm test

## Key Features

- AI-Enhanced Scraping with GPT-4 Vision
- Real-time search results
- Progressive Web App support
- Responsive design
- Advanced filtering
- Async processing
- Redis caching
- Database indexing

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

MIT License - see LICENSE file

## Migration from v1

If migrating from original JobSpy:

1. Run migration script: python scripts/migration/migrate_legacy.py
2. Copy any custom configurations
3. Test functionality with new API endpoints
4. Update any integrations
"""
        
        (self.project_root / "README.md").write_text(readme_content.strip())
        print("  Created: README.md")
    
    def run_setup(self):
        """Execute the complete setup process"""
        print("Starting JobSpy v2 Modernization Setup...\n")
        
        try:
            # Create project in parent directory of current JobSpy
            setup_path = self.current_dir / self.project_root
            self.project_root = setup_path
            
            self.setup_project_structure()
            print()
            
            self.create_backend_foundation()
            print()
            
            self.create_frontend_foundation()
            print()
            
            self.create_docker_setup()
            print()
            
            self.create_migration_script()
            print()
            
            self.generate_readme()
            print()
            
            print("Setup Complete!")
            print(f"Project created at: {self.project_root}")
            print("\nNext Steps:")
            print("1. cd JobSpy-v2")
            print("2. Copy .env.example to .env and configure API keys")
            print("3. Run: docker-compose up -d")
            print("4. Visit: http://localhost:3000")
            print("\nReady to start development!")
            
        except Exception as e:
            print(f"Setup failed: {e}")
            return False
        
        return True

if __name__ == "__main__":
    modernizer = JobSpyModernizer()
    success = modernizer.run_setup()
    sys.exit(0 if success else 1)
