# Phase 3: Deployment

## Objective
Deploy the Flask API to Railway and the React frontend to GitHub Pages, ensuring proper configuration and communication between services.

## Deployment Architecture

```
GitHub Pages (Frontend)          Railway (Backend API)
┌─────────────────────────┐     ┌─────────────────────────┐
│   React Application     │────▶│    Flask API Server     │
│   Static Files          │     │    Background Workers   │
│   yourname.github.io    │     │    Redis (optional)     │
└─────────────────────────┘     └─────────────────────────┘
```

## Part A: Railway API Deployment

### 3.1 Pre-deployment Preparation

**Update requirements.txt with all dependencies:**
```txt
# Core JobSpy dependencies
jobspy>=1.0.0
Flask>=3.0.0
Flask-CORS>=4.0.0
gunicorn>=21.2.0
pydantic>=2.3.0
python-dotenv>=1.0.0

# Background task processing (optional)
celery>=5.3.0
redis>=4.6.0

# Additional API dependencies
requests>=2.31.0
beautifulsoup4>=4.12.2
pandas>=2.1.0
numpy==1.26.3
markdownify>=1.1.0
regex>=2024.4.28
```

**Update Procfile for API-only deployment:**
```
web: cd web_app && python3 -m gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -
```

**Create .railwayignore for optimized deployment:**
```
# Frontend development files (not needed for API)
jobspy-frontend/
*.md
docs/
examples/
tests/

# Development and build artifacts
__pycache__/
.pytest_cache/
*.pyc
*.pyo
.coverage
.vscode/
.idea/

# Large data files
data/
*.csv
*.json
*.xlsx

# OS files
.DS_Store
Thumbs.db

# Environment files (use Railway environment variables)
.env
.env.local
```

### 3.2 Railway Environment Variables

Set the following environment variables in Railway dashboard:

**Production Configuration:**
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key-here
FLASK_DEBUG=false

# CORS Configuration
FRONTEND_URL=https://yourusername.github.io

# API Configuration
API_VERSION=v1
RATE_LIMIT_PER_MINUTE=60

# Background Tasks (if using Celery)
CELERY_BROKER_URL=redis://redis:6379/0
REDIS_URL=redis://redis:6379/0

# Monitoring and Logging
LOG_LEVEL=INFO
```

**To set environment variables in Railway:**
1. Go to your Railway project dashboard
2. Click on "Variables" tab
3. Add each variable with name and value
4. Railway will automatically restart your service

### 3.3 Deploy API to Railway

**Option 1: Deploy from existing repository**
```bash
# Make sure your current code is committed
git add .
git commit -m "Prepare API for production deployment"
git push origin main

# Railway will automatically deploy from your GitHub repository
```

**Option 2: Deploy using Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to existing project
railway link

# Deploy
railway up
```

### 3.4 Test API Deployment

**Create a simple test script (test_api_deployment.py):**
```python
import requests
import json

# Replace with your actual Railway URL
API_BASE_URL = "https://web-production-f5cc.up.railway.app"

def test_api_endpoints():
    print("Testing Railway API deployment...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=10)
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test job search endpoint
    try:
        search_data = {
            "site_name": "indeed",
            "search_term": "python developer",
            "location": "taipei",
            "results_wanted": 5
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/search",
            json=search_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Search test: SUCCESS - Found {data.get('count', 0)} jobs")
        else:
            print(f"Search test: FAILED - {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Search test failed: {e}")

if __name__ == "__main__":
    test_api_endpoints()
```

## Part B: GitHub Pages Frontend Deployment

### 3.5 Prepare Frontend for Production

**Update environment configuration:**

**Create .env.production in frontend directory:**
```
VITE_API_URL=https://web-production-f5cc.up.railway.app
VITE_APP_TITLE=JobSpy - Job Search Tool
VITE_APP_VERSION=1.0.0
```

**Update vite.config.ts for GitHub Pages:**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/jobspy/', // Replace 'jobspy' with your repository name
  build: {
    outDir: 'dist',
    sourcemap: false, // Disable for production
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          utils: ['axios', '@tanstack/react-query', 'zustand']
        }
      }
    }
  },
  server: {
    port: 3000,
    open: true,
  },
})
```

### 3.6 Create GitHub Repository for Frontend

```bash
# Navigate to your frontend directory
cd jobspy-frontend

# Initialize git repository
git init

# Create .gitignore
echo "node_modules/
dist/
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.DS_Store
.vscode/
*.log" > .gitignore

# Add and commit files
git add .
git commit -m "Initial commit: JobSpy React frontend"

# Create GitHub repository (replace 'yourusername' with your GitHub username)
# Go to GitHub.com and create a new repository named 'jobspy'

# Add remote origin
git remote add origin https://github.com/yourusername/jobspy.git
git branch -M main
git push -u origin main
```

### 3.7 Set up GitHub Pages Deployment

**Method 1: GitHub Actions (Recommended)**

**Create .github/workflows/deploy.yml:**
```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
      
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Build
      run: npm run build
      env:
        VITE_API_URL: https://web-production-f5cc.up.railway.app
        
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      if: github.ref == 'refs/heads/main'
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./dist
```

**Method 2: Manual deployment with gh-pages**

```bash
# Install gh-pages package
npm install --save-dev gh-pages

# Add deployment script to package.json
{
  "scripts": {
    "deploy": "npm run build && gh-pages -d dist"
  }
}

# Deploy manually
npm run deploy
```

### 3.8 Configure GitHub Pages

1. Go to your GitHub repository settings
2. Scroll down to "Pages" section
3. Under "Source", select "Deploy from a branch"
4. Choose "gh-pages" branch and "/ (root)" folder
5. Click "Save"

Your site will be available at: `https://yourusername.github.io/jobspy/`

## Part C: Integration Testing

### 3.9 End-to-End Testing

**Create integration test script (test_integration.py):**
```python
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_full_integration():
    """Test complete workflow from frontend to backend"""
    
    # Configuration
    FRONTEND_URL = "https://yourusername.github.io/jobspy/"
    API_URL = "https://web-production-f5cc.up.railway.app"
    
    print("Starting integration tests...")
    
    # Test 1: API Health Check
    print("\n1. Testing API health...")
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=10)
        assert response.status_code == 200
        print("✓ API is healthy")
    except Exception as e:
        print(f"✗ API health check failed: {e}")
        return False
    
    # Test 2: Frontend Loads
    print("\n2. Testing frontend loading...")
    try:
        driver = webdriver.Chrome()  # Make sure ChromeDriver is installed
        driver.get(FRONTEND_URL)
        
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        print("✓ Frontend loads successfully")
        
        # Test 3: Form Submission
        print("\n3. Testing job search form...")
        
        # Fill in the form
        search_input = driver.find_element(By.ID, "search_term")
        search_input.send_keys("python developer")
        
        location_input = driver.find_element(By.ID, "location")
        location_input.send_keys("taipei")
        
        submit_button = driver.find_element(By.TYPE, "submit")
        submit_button.click()
        
        # Wait for results (up to 30 seconds)
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            print("✓ Job search completed successfully")
            
            # Check if results are displayed
            rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
            print(f"✓ Found {len(rows)} job results")
            
        except Exception as e:
            print(f"✗ Job search failed or took too long: {e}")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"✗ Frontend test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_full_integration()
    print(f"\nIntegration tests {'PASSED' if success else 'FAILED'}")
```

### 3.10 Performance Testing

**Create performance test script (test_performance.py):**
```python
import requests
import time
import statistics

def test_api_performance():
    """Test API response times"""
    
    API_URL = "https://web-production-f5cc.up.railway.app"
    
    # Test health endpoint performance
    print("Testing API performance...")
    
    health_times = []
    for i in range(5):
        start = time.time()
        response = requests.get(f"{API_URL}/api/health")
        end = time.time()
        
        if response.status_code == 200:
            health_times.append(end - start)
        time.sleep(1)
    
    if health_times:
        avg_health = statistics.mean(health_times)
        print(f"Health endpoint average: {avg_health:.2f}s")
    
    # Test search endpoint performance
    search_data = {
        "site_name": "indeed",
        "search_term": "developer",
        "location": "taipei",
        "results_wanted": 10
    }
    
    search_times = []
    for i in range(3):  # Fewer tests as this is slower
        start = time.time()
        response = requests.post(f"{API_URL}/api/search", json=search_data, timeout=30)
        end = time.time()
        
        if response.status_code == 200:
            search_times.append(end - start)
        time.sleep(5)  # Give server time to recover
    
    if search_times:
        avg_search = statistics.mean(search_times)
        print(f"Search endpoint average: {avg_search:.2f}s")
    
    return {
        'health_avg': statistics.mean(health_times) if health_times else None,
        'search_avg': statistics.mean(search_times) if search_times else None
    }

if __name__ == "__main__":
    results = test_api_performance()
    print(f"\nPerformance Results:")
    print(f"Health API: {results['health_avg']:.2f}s")
    print(f"Search API: {results['search_avg']:.2f}s")
```

## Part D: Monitoring and Maintenance

### 3.11 Set up Monitoring

**Create monitoring script for uptime checking:**
```python
import requests
import smtplib
from email.mime.text import MimeText
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_service_health():
    """Monitor both frontend and backend health"""
    
    services = {
        'API': 'https://web-production-f5cc.up.railway.app/api/health',
        'Frontend': 'https://yourusername.github.io/jobspy/'
    }
    
    results = {}
    
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=10)
            results[name] = {
                'status': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'healthy': response.status_code == 200
            }
            logger.info(f"{name}: {response.status_code} ({response.elapsed.total_seconds():.2f}s)")
            
        except Exception as e:
            results[name] = {
                'status': 'ERROR',
                'response_time': None,
                'healthy': False,
                'error': str(e)
            }
            logger.error(f"{name}: {e}")
    
    return results

# Run monitoring
if __name__ == "__main__":
    while True:
        results = check_service_health()
        
        # Check if any service is down
        for service, result in results.items():
            if not result['healthy']:
                logger.warning(f"Service {service} is down!")
        
        # Wait 5 minutes before next check
        time.sleep(300)
```

### 3.12 Create Deployment Checklist

**deployment_checklist.md:**
```markdown
# Deployment Checklist

## Pre-deployment
- [ ] All code committed and pushed to main branch
- [ ] Environment variables set in Railway dashboard
- [ ] Frontend environment variables configured
- [ ] API routes tested locally
- [ ] CORS configuration verified

## Railway API Deployment
- [ ] Railway project connected to GitHub repository
- [ ] Environment variables configured
- [ ] Procfile updated for API-only deployment
- [ ] .railwayignore configured to exclude frontend files
- [ ] Deployment successful (check Railway logs)
- [ ] Health endpoint accessible
- [ ] Search endpoint tested

## GitHub Pages Frontend Deployment
- [ ] GitHub repository created for frontend
- [ ] GitHub Actions workflow configured
- [ ] Base path set correctly in vite.config.ts
- [ ] Production environment variables set
- [ ] Build successful
- [ ] Site accessible at github.io URL
- [ ] API integration working

## Post-deployment Testing
- [ ] Frontend loads without errors
- [ ] Job search form submits successfully
- [ ] Results display correctly
- [ ] Export functionality works
- [ ] Mobile responsiveness verified
- [ ] Cross-browser compatibility checked

## Performance Verification
- [ ] Initial page load < 3 seconds
- [ ] API response times acceptable
- [ ] No cold start delays for UI interactions
- [ ] Error handling working properly

## Final Steps
- [ ] Update DNS/domain if using custom domain
- [ ] Set up monitoring/alerting
- [ ] Document API endpoints
- [ ] Create user documentation
- [ ] Archive old monolithic deployment (optional)
```

## Completion Checklist

- [ ] Railway API deployment successful
- [ ] Environment variables configured
- [ ] GitHub Pages frontend deployment successful
- [ ] CORS properly configured
- [ ] Integration testing completed
- [ ] Performance benchmarks recorded
- [ ] Monitoring setup configured
- [ ] Documentation updated

## Next Steps

After completing Phase 3, proceed to [Phase 4: Go Live](./phase4_go_live.md) for final optimizations and launch preparation.