# Phase 1: API Preparation

## Objective
Convert the existing Flask web application into a RESTful API that can serve the React frontend.

## Tasks Overview

### 1. API Route Conversion
Transform existing Flask routes from rendering templates to returning JSON responses.

### 2. CORS Configuration
Enable Cross-Origin Resource Sharing for GitHub Pages to communicate with Railway API.

### 3. Authentication & Session Management
Implement token-based authentication to replace server-side sessions.

### 4. Async Task Processing
Add background job processing for heavy operations.

## Detailed Implementation

### 1.1 Convert Routes to API Endpoints

**Current Flask Routes (web_app/app.py):**
```python
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_jobs():
    # Current implementation returns rendered template
    return render_template('results.html', jobs=jobs)
```

**New API Routes:**
```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://yourusername.github.io'])

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/api/search', methods=['POST'])
def api_search_jobs():
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'site_name' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Process job search
        jobs = scrape_jobs(
            site_name=data['site_name'],
            search_term=data.get('search_term'),
            location=data.get('location'),
            results_wanted=data.get('results_wanted', 20)
        )
        
        # Return JSON response
        return jsonify({
            'success': True,
            'jobs': jobs.to_dict('records') if hasattr(jobs, 'to_dict') else jobs,
            'count': len(jobs),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['POST'])
def api_export_jobs():
    try:
        data = request.get_json()
        jobs_data = data.get('jobs', [])
        export_format = data.get('format', 'csv')
        
        if export_format == 'csv':
            # Generate CSV and return download URL or base64
            csv_content = convert_to_csv(jobs_data)
            return jsonify({
                'success': True,
                'download_url': create_download_url(csv_content),
                'filename': f'jobs_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 1.2 CORS Configuration

**Install and Configure CORS:**
```python
# In requirements.txt
Flask-CORS>=4.0.0

# In app.py
from flask_cors import CORS

# Configure CORS for production
CORS(app, 
     origins=['https://yourusername.github.io'],  # Your GitHub Pages domain
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)
```

### 1.3 Environment Configuration

**Create config.py:**
```python
import os
from dataclasses import dataclass

@dataclass
class Config:
    # Flask configuration
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key')
    FLASK_ENV: str = os.environ.get('FLASK_ENV', 'production')
    
    # CORS configuration
    FRONTEND_URL: str = os.environ.get('FRONTEND_URL', 'https://yourusername.github.io')
    
    # API configuration
    API_VERSION: str = 'v1'
    API_PREFIX: str = f'/api/{API_VERSION}'
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.environ.get('RATE_LIMIT_PER_MINUTE', '60'))
    
    # Background tasks
    CELERY_BROKER_URL: str = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')

config = Config()
```

### 1.4 Error Handling & Validation

**Add comprehensive error handling:**
```python
from functools import wraps
from pydantic import BaseModel, ValidationError

class JobSearchRequest(BaseModel):
    site_name: str
    search_term: str = ""
    location: str = ""
    results_wanted: int = 20
    
    class Config:
        extra = "forbid"

def validate_json(model_class):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                
                # Validate with Pydantic
                validated_data = model_class(**data)
                request.validated_data = validated_data
                return f(*args, **kwargs)
            
            except ValidationError as e:
                return jsonify({'error': 'Validation failed', 'details': e.errors()}), 400
            except Exception as e:
                return jsonify({'error': 'Invalid request format'}), 400
        
        return decorated_function
    return decorator

@app.route('/api/search', methods=['POST'])
@validate_json(JobSearchRequest)
def api_search_jobs():
    data = request.validated_data
    # Use validated data
    jobs = scrape_jobs(
        site_name=data.site_name,
        search_term=data.search_term,
        location=data.location,
        results_wanted=data.results_wanted
    )
    # ... rest of implementation
```

### 1.5 Background Task Processing

**For heavy operations, implement async processing:**
```python
# Add to requirements.txt
celery>=5.3.0
redis>=4.6.0

# Create tasks.py
from celery import Celery
from jobspy import scrape_jobs

celery = Celery('jobspy_api')
celery.config_from_object('config')

@celery.task(bind=True)
def async_job_search(self, search_params):
    try:
        jobs = scrape_jobs(**search_params)
        return {
            'status': 'completed',
            'jobs': jobs.to_dict('records'),
            'count': len(jobs)
        }
    except Exception as e:
        self.retry(countdown=60, max_retries=3)
        return {'status': 'failed', 'error': str(e)}

# In app.py
@app.route('/api/search/async', methods=['POST'])
@validate_json(JobSearchRequest)
def api_search_jobs_async():
    data = request.validated_data
    
    # Start background task
    task = async_job_search.delay(data.dict())
    
    return jsonify({
        'task_id': task.id,
        'status': 'processing',
        'message': 'Job search started. Use /api/task/{task_id} to check status'
    })

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = async_job_search.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {'status': 'processing', 'progress': 0}
    elif task.state == 'SUCCESS':
        response = task.result
    else:
        response = {'status': 'failed', 'error': str(task.info)}
    
    return jsonify(response)
```

## Updated File Structure

```
web_app/
├── app.py              # Main Flask application with API routes
├── config.py           # Configuration management
├── tasks.py            # Background task definitions
├── models/
│   ├── __init__.py
│   ├── requests.py     # Pydantic request models
│   └── responses.py    # Pydantic response models
├── utils/
│   ├── __init__.py
│   ├── validators.py   # Custom validation functions
│   └── helpers.py      # Utility functions
└── requirements.txt    # Updated dependencies
```

## Updated Requirements.txt

```txt
# Existing dependencies
jobspy>=1.0.0
Flask>=3.0.0
gunicorn>=21.2.0

# New API dependencies
Flask-CORS>=4.0.0
pydantic>=2.3.0
celery>=5.3.0
redis>=4.6.0
python-dotenv>=1.0.0

# Development dependencies (optional)
pytest>=7.0.0
pytest-flask>=1.2.0
```

## Testing the API

**Create test_api.py:**
```python
import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_search_endpoint(client):
    search_data = {
        'site_name': 'indeed',
        'search_term': 'python developer',
        'location': 'taipei',
        'results_wanted': 5
    }
    
    response = client.post('/api/search', 
                          data=json.dumps(search_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'jobs' in data
```

## Railway Deployment Configuration

**Update Procfile:**
```
web: cd web_app && python3 -m gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -
worker: cd web_app && celery -A tasks worker --loglevel=info
```

**Railway Environment Variables:**
```
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
FRONTEND_URL=https://yourusername.github.io
RATE_LIMIT_PER_MINUTE=60
CELERY_BROKER_URL=redis://redis:6379/0
```

## Completion Checklist

- [ ] Convert all routes to API endpoints
- [ ] Add CORS configuration
- [ ] Implement request validation
- [ ] Add error handling
- [ ] Create background task processing
- [ ] Update requirements.txt
- [ ] Create configuration management
- [ ] Write API tests
- [ ] Update Railway deployment
- [ ] Test API endpoints locally
- [ ] Deploy and test API on Railway

## Next Steps

After completing Phase 1, proceed to [Phase 2: Frontend Development](./phase2_frontend_development.md) to build the React application that will consume this API.