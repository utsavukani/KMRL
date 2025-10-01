@echo off
REM KMRL Optimization System - Windows Demo Runner
REM Launches the complete system for demonstration

echo 🚄 Starting KMRL Optimization System Demo...
echo ==============================================

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r deployment\requirements.txt

REM Generate synthetic data if not exists
if not exist "data\synthetic_dataset.csv" (
    echo 📊 Generating synthetic dataset...
    cd data
    python generate_synthetic_data.py
    cd ..
)

REM Start backend server in background
echo 🖥️ Starting FastAPI backend server...
cd backend
start /b python main.py
cd ..

REM Wait for backend to start
echo ⏳ Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

REM Start frontend server
echo 🌐 Starting frontend server...
cd frontend
start /b python -m http.server 8080
cd ..

echo.
echo ✅ KMRL Optimization System is now running!
echo.
echo 🔗 Access URLs:
echo    📱 Frontend Dashboard: http://localhost:8080
echo    🔧 API Documentation: http://localhost:8000/docs
echo    📊 API Health Check: http://localhost:8000/health
echo.
echo 🎯 Demo Scenarios:
echo    1. View train fleet status and assignments
echo    2. Run optimization for tomorrow's schedule
echo    3. Test what-if simulation scenarios
echo    4. Check ML delay predictions
echo    5. Export optimization results
echo.
echo ⏹️  Press Ctrl+C to stop servers or close this window
echo.
echo 🌐 Opening dashboard in your default browser...
start http://localhost:8080

REM Keep the window open
pause