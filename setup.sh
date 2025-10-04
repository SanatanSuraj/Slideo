#!/bin/bash

# Presenton Local Setup Script
# Clean setup for OpenAI and Google Gemini integrations only
echo "🚀 Setting up Presenton for local development..."
echo "📋 This setup supports OpenAI and Google Gemini integrations only"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 20+ from https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ is not installed. Please install Python 3.11+ from https://python.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo "❌ Node.js version 20+ is required. Current version: $(node -v)"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo "❌ Python 3.11+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"
echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Install Next.js dependencies
echo "📦 Installing Next.js dependencies..."
cd servers/nextjs
if npm install; then
    echo "✅ Next.js dependencies installed successfully"
else
    echo "❌ Failed to install Next.js dependencies"
    exit 1
fi
cd ../..

# Install Python dependencies with fallback
echo "📦 Installing Python dependencies..."
cd servers/fastapi

# Try pip3 first, then fall back to python3 -m pip
if command -v pip3 &> /dev/null; then
    echo "🔧 Using pip3 to install dependencies..."
    if pip3 install -r requirements.txt; then
        echo "✅ Python dependencies installed successfully with pip3"
    else
        echo "⚠️  pip3 failed, trying python3 -m pip..."
        if python3 -m pip install -r requirements.txt; then
            echo "✅ Python dependencies installed successfully with python3 -m pip"
        else
            echo "❌ Failed to install Python dependencies"
            exit 1
        fi
    fi
else
    echo "🔧 Using python3 -m pip to install dependencies..."
    if python3 -m pip install -r requirements.txt; then
        echo "✅ Python dependencies installed successfully with python3 -m pip"
    else
        echo "❌ Failed to install Python dependencies"
        exit 1
    fi
fi
cd ../..

# Create app_data directory
echo "📁 Creating app_data directory..."
mkdir -p app_data
echo "✅ App data directory created"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "✅ .env file created from env.example"
        echo "⚠️  Please edit .env file and add your API keys:"
        echo "   - OPENAI_API_KEY for OpenAI integration"
        echo "   - GOOGLE_API_KEY for Google Gemini integration"
    else
        echo "📝 Creating basic .env file..."
        cat > .env << EOF
# Presenton Environment Configuration
# Add your API keys below

# LLM Configuration (choose one)
LLM=openai
# LLM=google

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Google Configuration  
GOOGLE_API_KEY=your-google-api-key-here

# Image Generation Provider
IMAGE_PROVIDER=dall-e-3

# Optional Settings
CAN_CHANGE_KEYS=true
WEB_GROUNDING=false
DISABLE_ANONYMOUS_TELEMETRY=false
EOF
        echo "✅ Basic .env file created"
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and add your API keys:"
echo "   - OPENAI_API_KEY for OpenAI integration"
echo "   - GOOGLE_API_KEY for Google Gemini integration"
echo ""
echo "2. Start the application:"
echo "   npm run dev    # Development mode with hot reload"
echo "   npm start      # Production mode"
echo ""
echo "3. Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🔑 Supported LLM Providers:"
echo "   - OpenAI (GPT-4, GPT-3.5, etc.)"
echo "   - Google Gemini (Gemini 2.0 Flash, etc.)"
echo "   - Anthropic Claude (Claude 3.5 Sonnet, etc.)"
echo "   - Custom OpenAI-compatible endpoints"
echo ""
echo "🖼️  Supported Image Providers:"
echo "   - DALL-E 3 (OpenAI)"
echo "   - Gemini Flash (Google)"
echo "   - Pexels (Free stock photos)"
echo "   - Pixabay (Free stock photos)"
echo ""
echo "✨ Presenton is ready to use!"