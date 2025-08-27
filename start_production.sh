#!/bin/bash

# LegalLex MVP2 Production Startup Script
echo "🚀 Starting LegalLex MVP2 Production Environment..."

# Create necessary directories
mkdir -p analyses daily_results

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Start cronjob scheduler in background
echo "⏰ Starting cronjob scheduler..."
python cronjob_scheduler.py &
CRONJOB_PID=$!
echo "Cronjob scheduler started with PID: $CRONJOB_PID"

# Start Streamlit app
echo "🌐 Starting Streamlit application..."
echo "🔗 The application will be available at: http://localhost:8501"
echo ""
echo "👤 Login credentials:"
echo "   Client: username 'Caper', password 'Caper'"
echo "   Admin: username 'lucasaurich', password 'caneta123'"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $CRONJOB_PID 2>/dev/null
    echo "✅ Services stopped."
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start Streamlit
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# Wait for cronjob process to finish (should run indefinitely)
wait $CRONJOB_PID