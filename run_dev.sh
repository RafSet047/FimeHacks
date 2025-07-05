#!/bin/bash

# AI Chat Development Runner
# This script helps run both frontend and backend in development mode

echo "🚀 AI Chat Development Setup"
echo "=============================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

if ! command_exists python; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ All prerequisites are available"

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend && npm install && cd ..
else
    echo "✅ Frontend dependencies already installed"
fi

# Build React app for production
echo "🔨 Building React app for production..."
cd frontend && npm run build && cd ..

echo ""
echo "🎯 Choose your development mode:"
echo "1. Production mode (React served by FastAPI on :8080)"
echo "2. Development mode (React dev server on :3000, FastAPI on :8080)"
echo "3. Build React app only"
echo ""

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "🚀 Starting production mode on http://localhost:8080"
        python -c "
import uvicorn
from src.main import app
print('📱 Access the chat interface at: http://localhost:8080')
print('🔗 API documentation at: http://localhost:8080/docs')
uvicorn.run(app, host='0.0.0.0', port=8080, reload=False)
"
        ;;
    2)
        echo "🔧 Starting development mode..."
        echo "📱 Frontend: http://localhost:3000"
        echo "🔗 Backend API: http://localhost:8080"
        echo ""
        echo "Starting FastAPI backend..."
        python -c "
import uvicorn
from src.main import app
uvicorn.run(app, host='0.0.0.0', port=8080, reload=True)
" &

        echo "Starting React development server..."
        cd frontend && npm run dev
        ;;
    3)
        echo "🔨 Building React app..."
        cd frontend && npm run build
        echo "✅ Build complete! Files are in frontend/dist/"
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
