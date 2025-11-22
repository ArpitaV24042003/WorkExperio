@echo off
echo Starting WorkExperio Frontend...
cd frontend
if not exist node_modules (
    echo Installing dependencies...
    npm install
)
echo Starting development server...
npm run dev
pause


