# JobSpy v2 Setup Guide

## Required API Keys and Configuration

### 1. SECRET_KEY ✅ (Required)

Generate a secure secret key for JWT tokens:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Example output: `Giw175VHrFW456I1RJ6ggFnca3PjPEFFaJhznguTa5w`

### 2. OPENAI_API_KEY 🔑 (Required for AI features)

**Where to get it:**
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up/login to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)

**Cost:** ~$0.01-0.03 per job analysis (with our cost optimization)

### 3. GOOGLE_VISION_API_KEY ❌ (Optional - Not Used)

**Currently not needed** - JobSpy v2 uses OpenAI GPT-4V instead of Google Vision API.

## Quick Setup Steps

### 1. Copy Environment File
```bash
cd JobSpy-v2
cp .env.example .env
```

### 2. Edit .env File
```bash
# Open .env and update:
SECRET_KEY=your_generated_secret_key_here
OPENAI_API_KEY=sk-your_openai_key_here
```

### 3. Start the System
```bash
# Start all services
docker-compose up -d

# Or start manually:
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the Application
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000 (if running)

## Minimum Required Configuration

```env
# Minimum .env file content:
DATABASE_URL=postgresql://jobspy:password@localhost:5432/jobspy
REDIS_URL=redis://localhost:6379
SECRET_KEY=Giw175VHrFW456I1RJ6ggFnca3PjPEFFaJhznguTa5w
OPENAI_API_KEY=sk-your_openai_key_here
```

## Cost Estimates

- **OpenAI GPT-4V:** ~$0.01-0.03 per job page analysis
- **Daily limit:** $50 (configurable)
- **Local VLM fallback:** Free (when cost limit reached)

## Need Help?

1. Check the [Implementation Summary](./IMPLEMENTATION_SUMMARY.md)
2. View API docs at http://localhost:8000/docs
3. Check logs: `docker-compose logs backend`