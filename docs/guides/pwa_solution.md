# Progressive Web App (PWA) Implementation Guide

## Overview

The PWA approach provides a mobile-friendly, app-like experience with offline capabilities while running entirely in the browser using local computing resources.

## Architecture

```
Progressive Web App
├── Service Worker (Offline caching & background sync)
├── Web Workers (Heavy processing tasks)
├── Main App (React/Vue interface)
└── IndexedDB (Local data storage)
```

## Key Features

- 📱 **Mobile-friendly**: Responsive design optimized for touch
- 🔄 **Offline capability**: Work without internet after initial load
- ⚡ **Background processing**: Web Workers for intensive tasks
- 💾 **Local storage**: IndexedDB for job data persistence
- 🏠 **Installable**: Add to home screen like native app

## Project Structure

```
jobspy-pwa/
├── public/
│   ├── index.html
│   ├── manifest.json
│   ├── sw.js (Service Worker)
│   └── icons/
├── src/
│   ├── components/
│   ├── workers/
│   │   └── job-scraper.worker.js
│   ├── services/
│   │   ├── storage.js
│   │   ├── scraper.js
│   │   └── offline.js
│   ├── App.js
│   └── index.js
└── package.json
```

## Implementation

### 1. Web App Manifest (public/manifest.json)

```json
{
  "name": "JobSpy PWA",
  "short_name": "JobSpy",
  "description": "Local job search powered by your device",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#667eea",
  "theme_color": "#667eea",
  "orientation": "portrait-primary",
  "categories": ["business", "productivity"],
  "lang": "en",
  "icons": [
    {
      "src": "icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable any"
    }
  ],
  "screenshots": [
    {
      "src": "screenshots/mobile.png",
      "sizes": "540x720",
      "type": "image/png",
      "form_factor": "narrow"
    }
  ]
}
```

### 2. Service Worker (public/sw.js)

```javascript
const CACHE_NAME = 'jobspy-v1';
const STATIC_CACHE = 'jobspy-static-v1';
const DYNAMIC_CACHE = 'jobspy-dynamic-v1';

const STATIC_ASSETS = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/icons/icon-192x192.png'
];

// Install event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate event
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event
self.addEventListener('fetch', (event) => {
  const { request } = event;
  
  // Skip cross-origin requests
  if (!request.url.startsWith(self.location.origin)) {
    return;
  }

  event.respondWith(
    caches.match(request)
      .then(response => {
        if (response) {
          return response;
        }

        return fetch(request)
          .then(response => {
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            const responseToCache = response.clone();
            caches.open(DYNAMIC_CACHE)
              .then(cache => cache.put(request, responseToCache));

            return response;
          })
          .catch(() => {
            // Return offline page for navigation requests
            if (request.mode === 'navigate') {
              return caches.match('/');
            }
          });
      })
  );
});

// Background sync for offline job searches
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-job-search') {
    event.waitUntil(processOfflineSearches());
  }
});

async function processOfflineSearches() {
  // Process any queued job searches
  const searches = await getQueuedSearches();
  for (const search of searches) {
    try {
      await performJobSearch(search);
      await removeFromQueue(search.id);
    } catch (error) {
      console.error('Background search failed:', error);
    }
  }
}
```

### 3. Web Worker for Job Scraping (src/workers/job-scraper.worker.js)

```javascript
// Web Worker for intensive job scraping tasks
class JobScrapingWorker {
    constructor() {
        this.scrapers = new Map();
        this.initializeScrapers();
        
        self.onmessage = this.handleMessage.bind(this);
    }

    initializeScrapers() {
        // Indeed scraper
        this.scrapers.set('indeed', {
            searchUrl: (term, location) => 
                `https://www.indeed.com/jobs?q=${encodeURIComponent(term)}&l=${encodeURIComponent(location)}`,
            
            async scrape(params) {
                try {
                    const response = await fetch(`/api/proxy?url=${encodeURIComponent(this.searchUrl(params.searchTerm, params.location))}`);
                    const html = await response.text();
                    return this.parseIndeedJobs(html);
                } catch (error) {
                    throw new Error(`Indeed scraping failed: ${error.message}`);
                }
            },

            parseIndeedJobs(html) {
                // Use DOMParser to parse HTML in worker
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                
                const jobs = [];
                const jobCards = doc.querySelectorAll('[data-result-id]');
                
                jobCards.forEach(card => {
                    try {
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
                    } catch (error) {
                        console.error('Error parsing job card:', error);
                    }
                });
                
                return jobs;
            }
        });
    }

    async handleMessage(event) {
        const { type, data, id } = event.data;
        
        try {
            switch (type) {
                case 'SEARCH_JOBS':
                    const results = await this.searchJobs(data);
                    self.postMessage({ type: 'SEARCH_COMPLETE', data: results, id });
                    break;
                
                case 'HEALTH_CHECK':
                    self.postMessage({ type: 'HEALTH_OK', id });
                    break;
                
                default:
                    throw new Error(`Unknown message type: ${type}`);
            }
        } catch (error) {
            self.postMessage({ 
                type: 'ERROR', 
                data: { error: error.message }, 
                id 
            });
        }
    }

    async searchJobs(params) {
        const { sites, searchTerm, location, resultsWanted = 20 } = params;
        const results = {
            jobs: [],
            siteResults: {},
            errors: []
        };

        const searchPromises = sites.map(async (site) => {
            try {
                const scraper = this.scrapers.get(site);
                if (!scraper) {
                    throw new Error(`Unsupported site: ${site}`);
                }

                const jobs = await scraper.scrape(params);
                results.siteResults[site] = {
                    success: true,
                    count: jobs.length,
                    jobs
                };
                
                return jobs;
            } catch (error) {
                results.errors.push({ site, error: error.message });
                results.siteResults[site] = {
                    success: false,
                    error: error.message
                };
                return [];
            }
        });

        const allJobs = await Promise.all(searchPromises);
        results.jobs = allJobs.flat().slice(0, resultsWanted);

        return results;
    }
}

// Initialize worker
new JobScrapingWorker();
```

### 4. Storage Service (src/services/storage.js)

```javascript
// IndexedDB wrapper for local job data storage
class JobStorageService {
    constructor() {
        this.dbName = 'JobSpyDB';
        this.version = 1;
        this.db = null;
    }

    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.version);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve();
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // Create object stores
                if (!db.objectStoreNames.contains('searches')) {
                    const searchStore = db.createObjectStore('searches', { keyPath: 'id' });
                    searchStore.createIndex('timestamp', 'timestamp', { unique: false });
                }
                
                if (!db.objectStoreNames.contains('jobs')) {
                    const jobStore = db.createObjectStore('jobs', { keyPath: 'id' });
                    jobStore.createIndex('searchId', 'searchId', { unique: false });
                    jobStore.createIndex('site', 'site', { unique: false });
                }
                
                if (!db.objectStoreNames.contains('settings')) {
                    db.createObjectStore('settings', { keyPath: 'key' });
                }
            };
        });
    }

    async saveSearch(searchData) {
        const transaction = this.db.transaction(['searches', 'jobs'], 'readwrite');
        const searchStore = transaction.objectStore('searches');
        const jobStore = transaction.objectStore('jobs');
        
        // Save search metadata
        await searchStore.put(searchData);
        
        // Save individual jobs
        for (const job of searchData.jobs) {
            job.id = `${searchData.id}_${Date.now()}_${Math.random()}`;
            job.searchId = searchData.id;
            await jobStore.put(job);
        }
        
        return searchData.id;
    }

    async getSearch(searchId) {
        const transaction = this.db.transaction(['searches', 'jobs'], 'readonly');
        const searchStore = transaction.objectStore('searches');
        const jobStore = transaction.objectStore('jobs');
        
        const search = await this.promisifyRequest(searchStore.get(searchId));
        const jobsIndex = jobStore.index('searchId');
        const jobs = await this.promisifyRequest(jobsIndex.getAll(searchId));
        
        return { ...search, jobs };
    }

    async getSearchHistory(limit = 50) {
        const transaction = this.db.transaction(['searches'], 'readonly');
        const store = transaction.objectStore('searches');
        const index = store.index('timestamp');
        
        return this.promisifyRequest(
            index.getAll(null, limit)
        );
    }

    async deleteSearch(searchId) {
        const transaction = this.db.transaction(['searches', 'jobs'], 'readwrite');
        const searchStore = transaction.objectStore('searches');
        const jobStore = transaction.objectStore('jobs');
        
        await searchStore.delete(searchId);
        
        // Delete associated jobs
        const jobsIndex = jobStore.index('searchId');
        const jobs = await this.promisifyRequest(jobsIndex.getAll(searchId));
        
        for (const job of jobs) {
            await jobStore.delete(job.id);
        }
    }

    async saveSettings(settings) {
        const transaction = this.db.transaction(['settings'], 'readwrite');
        const store = transaction.objectStore('settings');
        
        for (const [key, value] of Object.entries(settings)) {
            await store.put({ key, value });
        }
    }

    async getSettings() {
        const transaction = this.db.transaction(['settings'], 'readonly');
        const store = transaction.objectStore('settings');
        const allSettings = await this.promisifyRequest(store.getAll());
        
        const settings = {};
        allSettings.forEach(item => {
            settings[item.key] = item.value;
        });
        
        return settings;
    }

    promisifyRequest(request) {
        return new Promise((resolve, reject) => {
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }
}

export default JobStorageService;
```

### 5. Main App Component (src/App.js)

```javascript
import React, { useState, useEffect } from 'react';
import JobStorageService from './services/storage';
import './App.css';

function App() {
    const [searchParams, setSearchParams] = useState({
        searchTerm: '',
        location: '',
        sites: ['indeed'],
        resultsWanted: 20
    });
    
    const [searchResults, setSearchResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [storageService] = useState(new JobStorageService());
    const [worker, setWorker] = useState(null);

    useEffect(() => {
        // Initialize storage and worker
        const initializeApp = async () => {
            await storageService.init();
            
            const jobWorker = new Worker('/workers/job-scraper.worker.js');
            jobWorker.onmessage = handleWorkerMessage;
            setWorker(jobWorker);
        };
        
        initializeApp();
        
        return () => {
            if (worker) worker.terminate();
        };
    }, []);

    const handleWorkerMessage = (event) => {
        const { type, data, id } = event.data;
        
        switch (type) {
            case 'SEARCH_COMPLETE':
                setLoading(false);
                setSearchResults(data);
                saveSearchResults(data);
                break;
                
            case 'ERROR':
                setLoading(false);
                setError(data.error);
                break;
        }
    };

    const saveSearchResults = async (results) => {
        const searchData = {
            id: Date.now().toString(),
            params: searchParams,
            timestamp: new Date().toISOString(),
            ...results
        };
        
        await storageService.saveSearch(searchData);
    };

    const handleSearch = async (e) => {
        e.preventDefault();
        
        if (!worker) {
            setError('Worker not initialized');
            return;
        }
        
        setLoading(true);
        setError(null);
        setSearchResults(null);
        
        worker.postMessage({
            type: 'SEARCH_JOBS',
            data: searchParams,
            id: Date.now()
        });
    };

    const exportResults = (format) => {
        if (!searchResults || !searchResults.jobs.length) return;
        
        const timestamp = new Date().toISOString().split('T')[0];
        let content, mimeType, filename;
        
        if (format === 'csv') {
            content = convertToCSV(searchResults.jobs);
            mimeType = 'text/csv';
            filename = `jobspy_results_${timestamp}.csv`;
        } else {
            content = JSON.stringify(searchResults.jobs, null, 2);
            mimeType = 'application/json';
            filename = `jobspy_results_${timestamp}.json`;
        }
        
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    };

    const convertToCSV = (jobs) => {
        const headers = Object.keys(jobs[0]).join(',');
        const rows = jobs.map(job => 
            Object.values(job).map(val => `"${val}"`).join(',')
        );
        return [headers, ...rows].join('\n');
    };

    return (
        <div className="app">
            <header className="app-header">
                <h1>🔍 JobSpy PWA</h1>
                <p>Local job search powered by your device</p>
            </header>

            <main className="app-main">
                <form onSubmit={handleSearch} className="search-form">
                    <div className="form-group">
                        <label>Job Title:</label>
                        <input
                            type="text"
                            value={searchParams.searchTerm}
                            onChange={(e) => setSearchParams({...searchParams, searchTerm: e.target.value})}
                            placeholder="e.g., Software Engineer"
                        />
                    </div>
                    
                    <div className="form-group">
                        <label>Location:</label>
                        <input
                            type="text"
                            value={searchParams.location}
                            onChange={(e) => setSearchParams({...searchParams, location: e.target.value})}
                            placeholder="e.g., San Francisco, CA"
                        />
                    </div>
                    
                    <div className="form-row">
                        <div className="form-group">
                            <label>Sites:</label>
                            <select
                                value={searchParams.sites[0]}
                                onChange={(e) => setSearchParams({...searchParams, sites: [e.target.value]})}
                            >
                                <option value="indeed">Indeed</option>
                                <option value="linkedin">LinkedIn</option>
                                <option value="glassdoor">Glassdoor</option>
                            </select>
                        </div>
                        
                        <div className="form-group">
                            <label>Results:</label>
                            <select
                                value={searchParams.resultsWanted}
                                onChange={(e) => setSearchParams({...searchParams, resultsWanted: parseInt(e.target.value)})}
                            >
                                <option value={10}>10</option>
                                <option value={20}>20</option>
                                <option value={50}>50</option>
                            </select>
                        </div>
                    </div>
                    
                    <button type="submit" disabled={loading} className="search-btn">
                        {loading ? '🔄 Searching...' : '🚀 Search Jobs'}
                    </button>
                </form>

                {loading && (
                    <div className="loading">
                        <div className="spinner"></div>
                        <p>Searching jobs using your device...</p>
                    </div>
                )}

                {error && (
                    <div className="error">
                        <p>❌ {error}</p>
                    </div>
                )}

                {searchResults && (
                    <div className="results">
                        <div className="results-header">
                            <h2>Found {searchResults.jobs.length} jobs</h2>
                            <div className="export-buttons">
                                <button onClick={() => exportResults('csv')}>📊 Export CSV</button>
                                <button onClick={() => exportResults('json')}>📄 Export JSON</button>
                            </div>
                        </div>
                        
                        <div className="jobs-grid">
                            {searchResults.jobs.map((job, index) => (
                                <div key={index} className="job-card">
                                    <h3>{job.title}</h3>
                                    <p className="company">{job.company}</p>
                                    <p className="location">📍 {job.location}</p>
                                    <p className="description">{job.description}</p>
                                    <p className="site">Source: {job.site}</p>
                                    {job.url && (
                                        <a href={job.url} target="_blank" rel="noopener noreferrer">
                                            View Job
                                        </a>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default App;
```

## Installation and Deployment

### 1. Development Setup

```bash
# Create React app
npx create-react-app jobspy-pwa
cd jobspy-pwa

# Install PWA dependencies
npm install workbox-webpack-plugin

# Add to package.json scripts:
# "build-pwa": "npm run build && npx workbox generateSW"
```

### 2. Production Deployment

```bash
# Build for production
npm run build

# Deploy to hosting service (Netlify, Vercel, GitHub Pages)
# The built files in 'build/' folder are ready for deployment
```

## Benefits

- 📱 **Mobile-optimized**: Touch-friendly interface
- 🔄 **Offline capable**: Works without internet
- ⚡ **Fast performance**: Local processing with Web Workers
- 💾 **Data persistence**: IndexedDB for local storage
- 🏠 **Installable**: Add to home screen
- 🌐 **Cross-platform**: Works on any device with browser

## Limitations

- 🌐 **CORS restrictions**: Limited direct site access
- 🔗 **Proxy dependency**: May need backend for some operations
- 📱 **Mobile processing**: Limited by device capabilities
- 🔒 **Security constraints**: Browser security restrictions

This PWA approach provides excellent mobile experience while leveraging local device resources for job searching and data processing.