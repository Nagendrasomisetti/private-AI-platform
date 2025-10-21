#!/bin/bash

# PrivAI Desktop - Unix Launcher
# This script launches the PrivAI desktop application

echo ""
echo "========================================"
echo "    PrivAI Desktop Application"
echo "========================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python from https://python.org/"
    exit 1
fi

echo "Checking dependencies..."

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing Electron dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

# Check if frontend is built
if [ ! -d "../frontend/build" ]; then
    echo "Building frontend..."
    cd ../frontend
    npm install
    npm run build
    cd ../electron-app
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to build frontend"
        exit 1
    fi
fi

# Check if backend dependencies are installed
if [ ! -d "../backend/venv" ]; then
    echo "Setting up backend..."
    cd ../backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ../electron-app
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to setup backend"
        exit 1
    fi
fi

echo ""
echo "Starting PrivAI Desktop..."
echo ""

# Start the application
npm start

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to start PrivAI Desktop"
    echo "Please check the error messages above"
    exit 1
fi

echo ""
echo "PrivAI Desktop has been closed."
