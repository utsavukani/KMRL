@echo off
REM KMRL Optimization System - Windows Setup Script
REM SIH25081 - AI-Driven Train Induction Planning & Scheduling

echo 🚄 Setting up KMRL Optimization System...
echo ==============================================

REM Create project directory structure
if not exist "kmrl_optimization_system" mkdir kmrl_optimization_system
cd kmrl_optimization_system

REM Create main directories
mkdir frontend\css frontend\js frontend\assets 2>nul
mkdir backend\models backend\api backend\utils 2>nul
mkdir data 2>nul
mkdir deployment 2>nul
mkdir tests 2>nul
mkdir notebooks 2>nul
mkdir docs 2>nul

echo 📁 Created project directory structure

REM Create essential files
echo. > frontend\index.html
echo. > frontend\css\style.css
echo. > frontend\js\dashboard.js

echo. > backend\main.py
echo. > backend\models\cp_sat_solver.py
echo. > backend\models\genetic_optimizer.py
echo. > backend\models\ml_predictor.py
echo. > backend\models\llm_explainer.py
echo. > backend\api\__init__.py
echo. > backend\api\ingestion.py
echo. > backend\api\optimization.py
echo. > backend\api\simulation.py
echo. > backend\api\prediction.py
echo. > backend\utils\__init__.py
echo. > backend\utils\data_validation.py
echo. > backend\utils\db_manager.py

echo. > data\generate_synthetic_data.py
echo. > data\schema_definitions.json
echo. > deployment\Dockerfile
echo. > deployment\docker-compose.yml
echo. > deployment\requirements.txt
echo. > tests\test_optimization.py
echo. > tests\test_constraints.py
echo. > tests\test_api.py
echo. > notebooks\ml_model_training.ipynb

echo 📄 Created essential project files

REM Create README
(
echo # KMRL AI-Driven Train Induction Planning System
echo ## SIH25081 - Smart India Hackathon 2025
echo.
echo ### Quick Start
echo ```bash
echo setup.bat
echo run_demo.bat
echo ```
echo.
echo ### Architecture
echo - **Frontend**: Vanilla HTML/CSS/JS with Tailwind
echo - **Backend**: FastAPI with OR-Tools ^& DEAP
echo - **Database**: SQLite for development
echo - **Deployment**: Docker + Free tier hosting
echo.
echo ### Features
echo - Multi-objective constraint optimization
echo - Real-time what-if simulation
echo - ML-powered delay prediction
echo - Explainable AI recommendations
echo.
echo ### Team: [Your Team Name]
echo ### Problem Statement: SIH25081
echo ### Organization: Kochi Metro Rail Limited ^(KMRL^)
) > README.md

echo 📋 Created README.md

echo.
echo ✅ Project setup complete!
echo.
echo Next steps:
echo 1. cd kmrl_optimization_system
echo 2. Run: python -m pip install -r deployment\requirements.txt
echo 3. Start development with backend files
echo.
echo Directory structure created:
dir /b 2>nul || echo Files created successfully!