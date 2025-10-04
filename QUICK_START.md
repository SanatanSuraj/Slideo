# 🚀 Presenton Quick Start Guide

## Prerequisites
- **Node.js 20+** - [Download here](https://nodejs.org/)
- **Python 3.11+** - [Download here](https://python.org/)

## 🎯 Quick Setup & Run

### 1. Setup Dependencies
```bash
# Run the setup script
bash setup.sh
```

### 2. Configure API Keys
**API keys are configured exclusively through environment variables** - no manual key entry in the UI.

Edit the `.env` file and add your API keys:
```bash
# Copy the example file
cp .env.example .env

# Edit with your API keys
nano .env
```

**Required Environment Variables:**
```bash
# Choose your LLM provider
LLM=openai  # or google, anthropic

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o

# Google Gemini Configuration  
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_MODEL=gemini-2.0-flash-exp

# Anthropic Claude Configuration (Optional)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

**Security Note:** API keys are never stored in the browser or local storage. They are only read from environment variables for maximum security.

### 3. Start the Application
```bash
# Run the development environment
./run_local.sh
```

## 🌐 Access URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MCP Server**: http://localhost:8001

## 🛑 Stop the Application
Press `Ctrl+C` in the terminal where the script is running.

## 🔧 Manual Commands (Alternative)

If you prefer to run servers manually:

```bash
# Terminal 1 - FastAPI Backend
cd servers/fastapi
python3 server.py --port 8000 --reload

# Terminal 2 - Next.js Frontend  
cd servers/nextjs
npm run dev
```

## 🆘 Troubleshooting

### Port Already in Use
The `run_local.sh` script automatically kills existing processes on ports 3000 and 8000.

### Missing Dependencies
Run the setup script again:
```bash
bash setup.sh
```

### API Keys Not Working
1. Check your `.env` file has the correct API keys
2. Verify the API keys are valid and have sufficient credits
3. Check the console output for specific error messages

## 📋 Supported Providers

### LLM Providers
- **OpenAI** (GPT-4, GPT-3.5, etc.)
- **Google Gemini** (Gemini 2.0 Flash, etc.)
- **Anthropic Claude** (Claude 3.5 Sonnet, etc.)
- **Custom OpenAI-compatible** endpoints

### Image Providers
- **DALL-E 3** (OpenAI)
- **Gemini Flash** (Google)
- **Pexels** (Free stock photos)
- **Pixabay** (Free stock photos)

## 🎉 You're Ready!

Once everything is running, you can:
1. Create AI-powered presentations
2. Upload documents to generate presentations
3. Customize templates and themes
4. Export to PDF and PPTX formats
