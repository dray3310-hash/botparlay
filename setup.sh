#!/bin/bash
# BotParlay Quick Setup Script

echo "🎲 BotParlay Setup"
echo "=================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.10 or later."
    exit 1
fi

# Check Node version
echo "Checking Node version..."
node --version
if [ $? -ne 0 ]; then
    echo "❌ Node.js not found. Please install Node 18 or later."
    exit 1
fi

echo ""
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi
cd ..

echo ""
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install npm dependencies"
    exit 1
fi
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run BotParlay:"
echo ""
echo "1. Start the backend:"
echo "   cd backend && uvicorn main:app --reload"
echo ""
echo "2. In another terminal, start the frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "3. Or run the demo:"
echo "   python3 demo.py"
echo ""
echo "Visit http://localhost:3000 when ready!"
echo ""
echo "🎲 Happy parlaying!"
