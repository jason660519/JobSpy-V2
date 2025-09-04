# Desktop Application Implementation Guide

## Overview

The desktop application approach provides the best performance and feature compatibility by running JobSpy locally using Electron and integrating with your existing Python codebase.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                Desktop Application                   │
├─────────────────────────────────────────────────────┤
│  Electron Main Process                              │
│  ├── Window Management                              │
│  ├── Python Process Communication                  │
│  └── File System Access                            │
├─────────────────────────────────────────────────────┤
│  Renderer Process (UI)                             │
│  ├── React/HTML Interface                          │
│  ├── Job Search Forms                              │
│  ├── Results Display                               │
│  └── Export Functions                              │
├─────────────────────────────────────────────────────┤
│  Python Backend                                     │
│  ├── Existing JobSpy Core                          │
│  ├── Platform Scrapers                             │
│  ├── Data Processing                               │
│  └── JSON API Interface                            │
└─────────────────────────────────────────────────────┘
```

## Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Node.js**: Version 18.0.0 or higher
- **Python**: Version 3.10 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 500MB free disk space

### Development Tools
```bash
# Check Node.js version
node --version  # Should be 18.0.0+

# Check Python version
python --version  # Should be 3.10+

# Install global tools
npm install -g electron
```

## Project Setup

### 1. Initialize Desktop Project

```bash
# Create new desktop application directory
mkdir jobspy-desktop
cd jobspy-desktop

# Initialize npm project
npm init -y

# Install Electron and dependencies
npm install electron python-shell
npm install --save-dev electron-builder

# Create basic directory structure
mkdir -p src/main src/renderer src/python assets
```

### 2. Project Structure

```
jobspy-desktop/
├── package.json
├── main.js                 # Electron main process
├── src/
│   ├── main/
│   │   ├── main.js         # Main process logic
│   │   └── preload.js      # Preload script for security
│   ├── renderer/
│   │   ├── index.html      # Main UI
│   │   ├── app.js          # Frontend logic
│   │   ├── style.css       # Application styling
│   │   └── components/     # UI components
│   └── python/
│       ├── job_scraper.py  # Python backend interface
│       ├── requirements.txt
│       └── utils/
├── assets/
│   ├── icon.png           # Application icon
│   └── splash.png         # Splash screen
└── dist/                  # Built application
```

## Core Implementation

### 3. Main Process (main.js)

```javascript
const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const { PythonShell } = require('python-shell');
const path = require('path');
const fs = require('fs');

// Keep a global reference of the window object
let mainWindow;
let pythonProcess = null;

function createWindow() {
    // Create the browser window
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'src/main/preload.js')
        },
        icon: path.join(__dirname, 'assets/icon.png'),
        show: false, // Don't show until ready
        titleBarStyle: 'default'
    });

    // Load the app
    mainWindow.loadFile('src/renderer/index.html');

    // Show window when ready to prevent visual flash
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    // Handle window closed
    mainWindow.on('closed', () => {
        mainWindow = null;
        if (pythonProcess) {
            pythonProcess.kill();
        }
    });

    // Open external links in browser
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });
}

// App event handlers
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// IPC Handlers for communication with renderer process

// Handle job search requests
ipcMain.handle('search-jobs', async (event, searchParams) => {
    return new Promise((resolve, reject) => {
        const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
        
        const options = {
            mode: 'json',
            pythonPath: pythonPath,
            scriptPath: path.join(__dirname, 'src/python'),
            args: [JSON.stringify(searchParams)]
        };

        PythonShell.run('job_scraper.py', options, (err, results) => {
            if (err) {
                console.error('Python execution error:', err);
                reject({
                    success: false,
                    error: err.message,
                    details: err.toString()
                });
            } else {
                try {
                    const result = results[0];
                    resolve(result);
                } catch (parseError) {
                    reject({
                        success: false,
                        error: 'Failed to parse Python response',
                        details: parseError.toString()
                    });
                }
            }
        });
    });
});

// Handle file export
ipcMain.handle('export-data', async (event, { data, format, filename }) => {
    try {
        const { filePath } = await dialog.showSaveDialog(mainWindow, {
            defaultPath: filename,
            filters: [
                { name: 'CSV files', extensions: ['csv'] },
                { name: 'JSON files', extensions: ['json'] },
                { name: 'All files', extensions: ['*'] }
            ]
        });

        if (filePath) {
            let content;
            if (format === 'csv') {
                content = convertToCSV(data);
            } else {
                content = JSON.stringify(data, null, 2);
            }

            fs.writeFileSync(filePath, content);
            return { success: true, filePath };
        }

        return { success: false, error: 'Export cancelled' };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

// Handle app info requests
ipcMain.handle('get-app-info', async () => {
    return {
        version: app.getVersion(),
        platform: process.platform,
        arch: process.arch,
        electronVersion: process.versions.electron,
        nodeVersion: process.versions.node
    };
});

// Utility function to convert data to CSV
function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [headers.join(',')];
    
    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header] || '';
            // Escape quotes and wrap in quotes if contains comma
            return typeof value === 'string' && (value.includes(',') || value.includes('"'))
                ? `"${value.replace(/"/g, '""')}"`
                : value;
        });
        csvRows.push(values.join(','));
    });
    
    return csvRows.join('\n');
}
```

### 4. Preload Script (src/main/preload.js)

```javascript
const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // Job search operations
    searchJobs: (params) => ipcRenderer.invoke('search-jobs', params),
    
    // File operations
    exportData: (data, format, filename) => 
        ipcRenderer.invoke('export-data', { data, format, filename }),
    
    // App information
    getAppInfo: () => ipcRenderer.invoke('get-app-info'),
    
    // Platform detection
    platform: process.platform,
    
    // Version info
    versions: {
        node: process.versions.node,
        chrome: process.versions.chrome,
        electron: process.versions.electron
    }
});
```

### 5. Python Backend (src/python/job_scraper.py)

```python
#!/usr/bin/env python3
"""
JobSpy Desktop Integration
Provides JSON API interface for Electron frontend
"""

import sys
import json
import os
import traceback
from datetime import datetime
from pathlib import Path

# Add JobSpy to Python path
project_root = Path(__file__).parent.parent.parent.parent / 'JobSpy'
if project_root.exists():
    sys.path.insert(0, str(project_root))

try:
    from jobseeker import scrape_jobs
    import pandas as pd
    JOBSPY_AVAILABLE = True
except ImportError as e:
    JOBSPY_AVAILABLE = False
    IMPORT_ERROR = str(e)

def validate_params(params):
    """Validate search parameters"""
    required_fields = ['site_name']
    missing_fields = [field for field in required_fields if not params.get(field)]
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Validate site_name
    valid_sites = ['indeed', 'linkedin', 'glassdoor', 'zip_recruiter', 'google']
    if params['site_name'] not in valid_sites:
        raise ValueError(f"Invalid site_name. Must be one of: {', '.join(valid_sites)}")
    
    # Validate results_wanted
    results_wanted = params.get('results_wanted', 20)
    if not isinstance(results_wanted, int) or results_wanted < 1 or results_wanted > 100:
        raise ValueError("results_wanted must be an integer between 1 and 100")
    
    return True

def search_jobs_desktop(params):
    """Execute job search using JobSpy"""
    try:
        # Validate parameters
        validate_params(params)
        
        if not JOBSPY_AVAILABLE:
            return {
                'success': False,
                'error': 'JobSpy not available',
                'details': f'Import error: {IMPORT_ERROR}',
                'suggestion': 'Please ensure JobSpy is installed: pip install -e /path/to/JobSpy'
            }
        
        # Extract and sanitize parameters
        site_name = params.get('site_name', 'indeed')
        search_term = params.get('search_term', '').strip()
        location = params.get('location', '').strip()
        results_wanted = int(params.get('results_wanted', 20))
        
        # Determine country based on location
        country = 'taiwan' if any(keyword in location.lower() 
                                for keyword in ['taiwan', 'taipei', '台灣', '台北']) else 'usa'
        
        print(f"Starting job search: {site_name}, term='{search_term}', location='{location}', count={results_wanted}")
        
        # Execute JobSpy search
        start_time = datetime.now()
        
        df = scrape_jobs(
            site_name=site_name,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            country_indeed=country,
            verbose=1  # Enable some logging
        )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Process results
        if df.empty:
            return {
                'success': True,
                'jobs': [],
                'count': 0,
                'message': 'No jobs found matching your criteria',
                'execution_time': f'{execution_time:.2f}s',
                'search_params': params,
                'timestamp': datetime.now().isoformat()
            }
        
        # Convert DataFrame to list of dictionaries
        jobs = df.to_dict('records')
        
        # Clean and format job data
        cleaned_jobs = []
        for job in jobs:
            cleaned_job = {
                'title': str(job.get('title', 'N/A')),
                'company': str(job.get('company', 'N/A')),
                'location': str(job.get('location', 'N/A')),
                'description': str(job.get('description', 'No description available'))[:500],
                'salary': str(job.get('salary', 'Not specified')),
                'job_type': str(job.get('job_type', 'Not specified')),
                'date_posted': str(job.get('date_posted', 'Unknown')),
                'job_url': str(job.get('job_url', '')),
                'site': str(job.get('site', site_name)),
                'scraped_at': datetime.now().isoformat()
            }
            cleaned_jobs.append(cleaned_job)
        
        return {
            'success': True,
            'jobs': cleaned_jobs,
            'count': len(cleaned_jobs),
            'message': f'Successfully found {len(cleaned_jobs)} jobs',
            'execution_time': f'{execution_time:.2f}s',
            'search_params': params,
            'platform': site_name,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error in search_jobs_desktop: {error_details}")
        
        return {
            'success': False,
            'error': str(e),
            'details': error_details,
            'search_params': params,
            'timestamp': datetime.now().isoformat()
        }

def get_supported_sites():
    """Get list of supported job sites"""
    return {
        'sites': [
            {'value': 'indeed', 'label': 'Indeed', 'countries': ['usa', 'taiwan', 'canada', 'uk']},
            {'value': 'linkedin', 'label': 'LinkedIn', 'countries': ['global']},
            {'value': 'glassdoor', 'label': 'Glassdoor', 'countries': ['usa', 'canada', 'uk']},
            {'value': 'zip_recruiter', 'label': 'ZipRecruiter', 'countries': ['usa']},
            {'value': 'google', 'label': 'Google Jobs', 'countries': ['global']}
        ],
        'default': 'indeed'
    }

def main():
    """Main entry point for desktop integration"""
    try:
        if len(sys.argv) < 2:
            # Return supported sites info if no parameters
            result = get_supported_sites()
            print(json.dumps(result))
            return
        
        # Parse command line arguments
        params_json = sys.argv[1]
        params = json.loads(params_json)
        
        # Handle different command types
        command = params.get('command', 'search')
        
        if command == 'search':
            result = search_jobs_desktop(params)
        elif command == 'sites':
            result = get_supported_sites()
        else:
            result = {
                'success': False,
                'error': f'Unknown command: {command}',
                'available_commands': ['search', 'sites']
            }
        
        # Output result as JSON
        print(json.dumps(result))
        
    except json.JSONDecodeError as e:
        error_result = {
            'success': False,
            'error': 'Invalid JSON parameters',
            'details': str(e)
        }
        print(json.dumps(error_result))
    
    except Exception as e:
        error_result = {
            'success': False,
            'error': 'Unexpected error',
            'details': traceback.format_exc()
        }
        print(json.dumps(error_result))

if __name__ == '__main__':
    main()
```

### 6. Frontend UI (src/renderer/index.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JobSpy Desktop</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="app-container">
        <!-- Header -->
        <header class="app-header">
            <div class="header-content">
                <h1 class="app-title">
                    <span class="icon">🔍</span>
                    JobSpy Desktop
                </h1>
                <div class="header-info">
                    <span id="status-indicator" class="status-ready">Ready</span>
                    <button id="about-btn" class="header-btn">About</button>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="main-content">
            <!-- Search Form -->
            <section class="search-section">
                <div class="search-card">
                    <h2>Search Jobs Locally</h2>
                    <form id="job-search-form" class="search-form">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="site-name">Job Site:</label>
                                <select id="site-name" required>
                                    <option value="indeed">Indeed</option>
                                    <option value="linkedin">LinkedIn</option>
                                    <option value="glassdoor">Glassdoor</option>
                                    <option value="zip_recruiter">ZipRecruiter</option>
                                    <option value="google">Google Jobs</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label for="results-wanted">Results:</label>
                                <select id="results-wanted">
                                    <option value="10">10 jobs</option>
                                    <option value="20" selected>20 jobs</option>
                                    <option value="50">50 jobs</option>
                                    <option value="100">100 jobs</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="search-term">Job Title / Keywords:</label>
                                <input type="text" id="search-term" 
                                       placeholder="e.g., Python Developer, Data Scientist">
                            </div>
                            
                            <div class="form-group">
                                <label for="location">Location:</label>
                                <input type="text" id="location" 
                                       placeholder="e.g., Taipei, Taiwan">
                            </div>
                        </div>
                        
                        <div class="form-actions">
                            <button type="submit" id="search-btn" class="search-btn">
                                <span class="btn-icon">🚀</span>
                                Search Jobs Locally
                            </button>
                        </div>
                    </form>
                </div>
            </section>

            <!-- Loading Section -->
            <section id="loading-section" class="loading-section" style="display: none;">
                <div class="loading-card">
                    <div class="spinner"></div>
                    <h3>Searching Jobs...</h3>
                    <p>Using your local computer for maximum performance</p>
                    <div class="progress-info">
                        <span id="progress-text">Initializing search...</span>
                    </div>
                </div>
            </section>

            <!-- Results Section -->
            <section id="results-section" class="results-section" style="display: none;">
                <div class="results-header">
                    <div class="results-info">
                        <h2 id="results-title">Search Results</h2>
                        <p id="results-summary"></p>
                    </div>
                    <div class="results-actions">
                        <button id="export-csv-btn" class="export-btn">
                            📊 Export CSV
                        </button>
                        <button id="export-json-btn" class="export-btn">
                            📄 Export JSON
                        </button>
                    </div>
                </div>
                
                <div id="jobs-container" class="jobs-container">
                    <!-- Job cards will be inserted here -->
                </div>
            </section>

            <!-- Error Section -->
            <section id="error-section" class="error-section" style="display: none;">
                <div class="error-card">
                    <div class="error-icon">⚠️</div>
                    <h3>Search Error</h3>
                    <p id="error-message"></p>
                    <div class="error-actions">
                        <button id="retry-btn" class="retry-btn">Try Again</button>
                        <button id="clear-error-btn" class="clear-btn">Clear</button>
                    </div>
                </div>
            </section>
        </main>

        <!-- Footer -->
        <footer class="app-footer">
            <div class="footer-content">
                <span>JobSpy Desktop - Local job search powered by your computer</span>
                <span id="app-version"></span>
            </div>
        </footer>
    </div>

    <!-- About Modal -->
    <div id="about-modal" class="modal" style="display: none;">
        <div class="modal-content">
            <div class="modal-header">
                <h3>About JobSpy Desktop</h3>
                <button id="close-modal" class="close-btn">&times;</button>
            </div>
            <div class="modal-body">
                <p><strong>JobSpy Desktop</strong> runs entirely on your local computer for maximum performance and privacy.</p>
                <ul>
                    <li>🚀 No server delays or cold starts</li>
                    <li>💻 Uses your full CPU power</li>
                    <li>🔒 Complete privacy - data stays local</li>
                    <li>💰 Zero server costs</li>
                    <li>📱 Works offline after data fetch</li>
                </ul>
                <div class="version-info">
                    <p><strong>Version:</strong> <span id="modal-version"></span></p>
                    <p><strong>Platform:</strong> <span id="modal-platform"></span></p>
                    <p><strong>Electron:</strong> <span id="modal-electron"></span></p>
                </div>
            </div>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>
```

## Package Configuration

### 7. Package.json

```json
{
  "name": "jobspy-desktop",
  "productName": "JobSpy Desktop",
  "version": "1.0.0",
  "description": "Local job search application powered by JobSpy",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "dev": "electron . --enable-logging",
    "build": "electron-builder",
    "build-win": "electron-builder --win",
    "build-mac": "electron-builder --mac",
    "build-linux": "electron-builder --linux",
    "postinstall": "electron-builder install-app-deps"
  },
  "keywords": ["job search", "desktop", "scraping", "local"],
  "author": "JobSpy Team",
  "license": "MIT",
  "dependencies": {
    "electron": "^28.0.0",
    "python-shell": "^5.0.0"
  },
  "devDependencies": {
    "electron-builder": "^24.9.1"
  },
  "build": {
    "appId": "com.jobspy.desktop",
    "productName": "JobSpy Desktop",
    "directories": {
      "output": "dist"
    },
    "files": [
      "main.js",
      "src/**/*",
      "assets/**/*",
      "node_modules/**/*"
    ],
    "extraResources": [
      {
        "from": "src/python",
        "to": "python"
      }
    ],
    "win": {
      "target": "nsis",
      "icon": "assets/icon.ico"
    },
    "mac": {
      "target": "dmg",
      "icon": "assets/icon.icns"
    },
    "linux": {
      "target": "AppImage",
      "icon": "assets/icon.png"
    }
  }
}
```

## Installation and Usage

### 8. Development Setup

```bash
# 1. Clone and setup
git clone https://github.com/jason660519/jobseeker.git JobSpy
cd jobspy-desktop

# 2. Install Node.js dependencies
npm install

# 3. Setup Python environment
cd src/python
pip install -r requirements.txt

# 4. Install JobSpy in development mode
cd ../../../JobSpy
pip install -e .

# 5. Run the application
cd ../jobspy-desktop
npm start
```

### 9. Building for Distribution

```bash
# Build for current platform
npm run build

# Build for specific platforms
npm run build-win    # Windows
npm run build-mac    # macOS
npm run build-linux  # Linux

# The built application will be in the dist/ folder
```

## Performance Optimization

### 10. Python Process Management

The desktop app can be optimized by keeping a persistent Python process:

```javascript
// In main.js - add persistent Python process
let persistentPython = null;

function initializePythonProcess() {
    const options = {
        mode: 'json',
        pythonPath: process.platform === 'win32' ? 'python' : 'python3',
        scriptPath: path.join(__dirname, 'src/python'),
        args: ['--daemon']  // Run in daemon mode
    };
    
    persistentPython = new PythonShell('job_scraper.py', options);
    
    persistentPython.on('error', (err) => {
        console.error('Python process error:', err);
        persistentPython = null;
    });
}

// Initialize on app ready
app.whenReady().then(() => {
    createWindow();
    initializePythonProcess();
});
```

## Troubleshooting

### Common Issues

1. **Python not found**: Ensure Python 3.10+ is installed and in PATH
2. **JobSpy import error**: Install JobSpy with `pip install -e /path/to/JobSpy`
3. **Slow startup**: Add splash screen and preload common data
4. **Memory usage**: Implement result pagination and cleanup

### Performance Tips

- Enable Python bytecode compilation
- Implement result caching
- Use Web Workers for UI-heavy operations
- Optimize bundle size with tree shaking

## Next Steps

1. **Test the basic implementation**
2. **Add more advanced features** (job filtering, saved searches)
3. **Implement auto-updates** using electron-updater
4. **Add telemetry** for performance monitoring
5. **Create installer packages** for distribution

This desktop application provides the best performance by leveraging your local computer's full power while maintaining complete compatibility with your existing JobSpy codebase.