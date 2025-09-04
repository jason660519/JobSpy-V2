# Browser Extension Implementation Guide

## Overview

The browser extension approach provides seamless job site integration by injecting scraping directly into web pages, bypassing CORS restrictions completely.

## Architecture

```
Browser Extension
├── Extension Popup (Search Interface)
├── Background Service Worker (Data Management)
└── Content Scripts (Site-specific Scrapers)
```

## Quick Setup

### 1. Project Structure
```
jobspy-extension/
├── manifest.json
├── popup/
│   ├── popup.html
│   ├── popup.js
│   └── popup.css
├── background/
│   └── background.js
├── content-scripts/
│   ├── indeed.js
│   ├── linkedin.js
│   └── common.js
└── icons/
```

### 2. Manifest (manifest.json)
```json
{
  "manifest_version": 3,
  "name": "JobSpy Browser Extension",
  "version": "1.0.0",
  "permissions": ["activeTab", "storage", "scripting"],
  "host_permissions": [
    "https://www.indeed.com/*",
    "https://www.linkedin.com/*",
    "https://www.glassdoor.com/*"
  ],
  "background": {
    "service_worker": "background/background.js"
  },
  "content_scripts": [
    {
      "matches": ["https://www.indeed.com/*"],
      "js": ["content-scripts/indeed.js"]
    }
  ],
  "action": {
    "default_popup": "popup/popup.html"
  }
}
```

### 3. Content Script (content-scripts/indeed.js)
```javascript
class IndeedScraper {
    constructor() {
        chrome.runtime.onMessage.addListener(this.handleMessage.bind(this));
    }

    async handleMessage(message, sender, sendResponse) {
        if (message.type === 'SCRAPE_JOBS') {
            const jobs = await this.scrapeJobs(message.params);
            sendResponse({ success: true, jobs });
        }
        return true;
    }

    async scrapeJobs(params) {
        const jobs = [];
        const jobCards = document.querySelectorAll('[data-result-id]');
        
        jobCards.forEach(card => {
            const title = card.querySelector('[data-testid="job-title"]')?.textContent?.trim();
            const company = card.querySelector('[data-testid="company-name"]')?.textContent?.trim();
            const location = card.querySelector('[data-testid="job-location"]')?.textContent?.trim();
            const description = card.querySelector('.job-snippet')?.textContent?.trim();
            const url = card.querySelector('[data-testid="job-title"] a')?.href;
            
            if (title && company) {
                jobs.push({
                    title,
                    company,
                    location: location || 'N/A',
                    description: (description || '').substring(0, 300),
                    url: url || '',
                    site: 'Indeed',
                    scrapedAt: new Date().toISOString()
                });
            }
        });
        
        return jobs.slice(0, params.resultsWanted || 20);
    }
}

new IndeedScraper();
```

### 4. Background Script (background/background.js)
```javascript
class JobSpyExtension {
    constructor() {
        this.jobs = new Map();
        chrome.runtime.onMessage.addListener(this.handleMessage.bind(this));
    }

    async handleMessage(message, sender, sendResponse) {
        switch (message.type) {
            case 'SEARCH_JOBS':
                return await this.searchJobs(message.params);
            case 'GET_JOBS':
                return this.getJobs(message.searchId);
            case 'EXPORT_JOBS':
                return await this.exportJobs(message.searchId, message.format);
        }
    }

    async searchJobs(params) {
        const searchId = Date.now().toString();
        const results = { searchId, jobs: [], errors: [] };
        
        try {
            // Create tab for Indeed search
            const searchUrl = `https://www.indeed.com/jobs?q=${encodeURIComponent(params.searchTerm)}&l=${encodeURIComponent(params.location)}`;
            
            const tab = await chrome.tabs.create({ url: searchUrl, active: false });
            
            // Wait for page load and scrape
            return new Promise((resolve) => {
                chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
                    if (tabId === tab.id && info.status === 'complete') {
                        chrome.tabs.onUpdated.removeListener(listener);
                        
                        chrome.tabs.sendMessage(tab.id, {
                            type: 'SCRAPE_JOBS',
                            params
                        }, (response) => {
                            chrome.tabs.remove(tab.id);
                            
                            if (response && response.success) {
                                results.jobs = response.jobs;
                                this.jobs.set(searchId, results);
                                resolve({ success: true, searchId, jobCount: response.jobs.length });
                            } else {
                                resolve({ success: false, error: 'Scraping failed' });
                            }
                        });
                    }
                });
            });
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    getJobs(searchId) {
        const results = this.jobs.get(searchId);
        return results ? { success: true, jobs: results.jobs } : { success: false };
    }

    async exportJobs(searchId, format) {
        const results = this.jobs.get(searchId);
        if (!results) return { success: false, error: 'No jobs found' };

        const content = format === 'csv' ? this.convertToCSV(results.jobs) : JSON.stringify(results.jobs, null, 2);
        const blob = new Blob([content], { type: format === 'csv' ? 'text/csv' : 'application/json' });
        const url = URL.createObjectURL(blob);
        
        await chrome.downloads.download({
            url,
            filename: `jobspy_results_${new Date().toISOString().split('T')[0]}.${format}`
        });

        return { success: true };
    }

    convertToCSV(jobs) {
        if (!jobs.length) return '';
        const headers = Object.keys(jobs[0]).join(',');
        const rows = jobs.map(job => Object.values(job).map(val => `"${val}"`).join(','));
        return [headers, ...rows].join('\n');
    }
}

new JobSpyExtension();
```

### 5. Popup Interface (popup/popup.html)
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { width: 350px; padding: 20px; font-family: Arial, sans-serif; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .search-btn { width: 100%; padding: 12px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .search-btn:hover { background: #45a049; }
        .loading { text-align: center; padding: 20px; }
        .spinner { border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .results { max-height: 300px; overflow-y: auto; }
        .job-card { border: 1px solid #eee; padding: 10px; margin-bottom: 10px; border-radius: 4px; }
        .job-title { font-weight: bold; color: #2196F3; }
        .job-company { color: #666; }
        .export-btn { margin: 5px; padding: 8px 15px; background: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div>
        <h2>🔍 JobSpy Extension</h2>
        
        <form id="search-form">
            <div class="form-group">
                <label>Job Title:</label>
                <input type="text" id="search-term" placeholder="Software Engineer">
            </div>
            
            <div class="form-group">
                <label>Location:</label>
                <input type="text" id="location" placeholder="San Francisco, CA">
            </div>
            
            <div class="form-group">
                <label>Results:</label>
                <select id="results-count">
                    <option value="10">10</option>
                    <option value="20" selected>20</option>
                    <option value="50">50</option>
                </select>
            </div>
            
            <button type="submit" class="search-btn">🚀 Search Jobs</button>
        </form>
        
        <div id="loading" style="display: none;">
            <div class="loading">
                <div class="spinner"></div>
                <p>Searching jobs...</p>
            </div>
        </div>
        
        <div id="results" style="display: none;">
            <div id="results-header">
                <p><span id="job-count">0</span> jobs found</p>
                <button id="export-csv" class="export-btn">Export CSV</button>
                <button id="export-json" class="export-btn">Export JSON</button>
            </div>
            <div id="jobs-container"></div>
        </div>
        
        <div id="error" style="display: none; color: red; text-align: center;">
            <p id="error-message">Error occurred</p>
        </div>
    </div>
    
    <script src="popup.js"></script>
</body>
</html>
```

### 6. Popup Logic (popup/popup.js)
```javascript
let currentSearchId = null;

document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const errorDiv = document.getElementById('error');

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const params = {
            searchTerm: document.getElementById('search-term').value,
            location: document.getElementById('location').value,
            resultsWanted: parseInt(document.getElementById('results-count').value)
        };

        showLoading();
        
        try {
            const response = await chrome.runtime.sendMessage({
                type: 'SEARCH_JOBS',
                params
            });

            if (response.success) {
                currentSearchId = response.searchId;
                showResults(response.jobCount);
                await loadJobsDisplay();
            } else {
                showError(response.error);
            }
        } catch (error) {
            showError(error.message);
        }
    });

    document.getElementById('export-csv').addEventListener('click', () => exportJobs('csv'));
    document.getElementById('export-json').addEventListener('click', () => exportJobs('json'));

    function showLoading() {
        loadingDiv.style.display = 'block';
        resultsDiv.style.display = 'none';
        errorDiv.style.display = 'none';
    }

    function showResults(count) {
        loadingDiv.style.display = 'none';
        resultsDiv.style.display = 'block';
        errorDiv.style.display = 'none';
        document.getElementById('job-count').textContent = count;
    }

    function showError(message) {
        loadingDiv.style.display = 'none';
        resultsDiv.style.display = 'none';
        errorDiv.style.display = 'block';
        document.getElementById('error-message').textContent = message;
    }

    async function loadJobsDisplay() {
        if (!currentSearchId) return;

        const response = await chrome.runtime.sendMessage({
            type: 'GET_JOBS',
            searchId: currentSearchId
        });

        if (response.success) {
            const container = document.getElementById('jobs-container');
            container.innerHTML = '';

            response.jobs.slice(0, 5).forEach(job => {
                const jobCard = document.createElement('div');
                jobCard.className = 'job-card';
                jobCard.innerHTML = `
                    <div class="job-title">${job.title}</div>
                    <div class="job-company">${job.company}</div>
                    <div>${job.location}</div>
                    <div style="font-size: 12px; margin-top: 5px;">${job.description.substring(0, 100)}...</div>
                `;
                container.appendChild(jobCard);
            });
        }
    }

    async function exportJobs(format) {
        if (!currentSearchId) return;

        await chrome.runtime.sendMessage({
            type: 'EXPORT_JOBS',
            searchId: currentSearchId,
            format
        });
    }
});
```

## Installation

1. **Load Extension in Chrome:**
   - Open `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select extension folder

2. **Test Extension:**
   - Click extension icon in toolbar
   - Enter search terms
   - Click "Search Jobs"

## Benefits

- ✅ **No CORS restrictions**: Direct site access
- ✅ **Browser integration**: Native experience
- ✅ **Easy distribution**: Chrome/Firefox stores
- ✅ **Automatic updates**: Through store
- ✅ **Cross-platform**: Works on any OS

## Limitations

- ❌ **Site dependency**: Breaks if layouts change
- ❌ **Detection risk**: May be blocked by sites
- ❌ **Limited resources**: Browser-constrained processing
- ❌ **Maintenance**: Requires updates for site changes

This extension provides excellent browser integration while leveraging local processing power for job searching across multiple platforms.