#!/bin/bash

# Start both frontend and backend servers for local development

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Starting TalentLens local development servers..."

# Function to kill processes on exit
cleanup() {
    echo -e "\nShutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup EXIT INT TERM

# Start backend (in root directory)
echo "Starting backend server..."
cd "$SCRIPT_DIR"
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo -e "\n✅ Servers started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo -e "\nPress Ctrl+C to stop both servers\n"

# Wait for both processes
wait