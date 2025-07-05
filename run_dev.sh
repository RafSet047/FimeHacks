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

# Install admin panel dependencies if needed
if [ ! -d "admin-panel/node_modules" ]; then
    echo "📦 Installing admin panel dependencies..."
    cd admin-panel && npm install && cd ..
else
    echo "✅ Admin panel dependencies already installed"
fi

# Build React app for production
echo "🔨 Building React app for production..."
cd frontend && npm run build && cd ..

# Build admin panel for production
echo "🔨 Building admin panel for production..."
cd admin-panel && npm run build && cd ..

echo ""
echo "🎯 Choose your development mode:"
echo "1. Production mode (React + Admin Panel served by FastAPI on :8080)"
echo "2. Development mode (React dev server on :3000, FastAPI on :8080)"
echo "3. Development mode with Admin Panel (React on :3000, Admin Panel on :3001, FastAPI on :8080)"
echo "4. Build React app and Admin Panel only"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🚀 Starting production mode on http://localhost:8080"
        echo "📱 Access the chat interface at: http://localhost:8080"
        echo "🔧 Access the admin panel at: http://localhost:8080/admin"
        echo "🔗 API documentation at: http://localhost:8080/docs"
        PYTHONPATH=. python -m src.main
        ;;
    2)
        echo "🔧 Starting development mode..."
        echo "📱 Frontend: http://localhost:3000"
        echo "🔗 Backend API: http://localhost:8080"
        echo ""
        echo "Starting FastAPI backend..."
        PYTHONPATH=. python -m src.main &

        echo "Starting React development server..."
        cd frontend && npm run dev
        ;;
    3)
        echo "🔧 Starting development mode with Admin Panel..."
        echo "📱 Frontend: http://localhost:3000"
        echo "🔧 Admin Panel: http://localhost:3001"
        echo "🔗 Backend API: http://localhost:8080"
        echo ""
        echo "Starting FastAPI backend..."
        PYTHONPATH=. python -m src.main &

        echo "Starting React development server..."
        cd frontend && npm run dev &

        echo "Starting Admin Panel development server..."
        cd admin-panel && npm run dev
        ;;
    4)
        echo "🔨 Building React app and Admin Panel..."
        cd frontend && npm run build && cd ..
        echo "✅ Frontend build complete! Files are in frontend/dist/"
        cd admin-panel && npm run build && cd ..
        echo "✅ Admin Panel build complete! Files are in admin-panel/dist/"
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
