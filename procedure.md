# 📁 Crop Health Monitoring System

## 🧠 Backend (FastAPI)

### 📌 Setup Steps

#### Install Python 
    CMD:
        winget --version
        winget install Python.Python.3.12
        python --version
1. Go to backend folder
   cd backend

2. Create virtual environment
   python -m venv .venv

3. Activate virtual environment
   CMD:
   .\.venv\Scripts\activate

4. Install dependencies
   pip install -r requirements.txt

5. Run backend server
   python -m uvicorn app.main:app --reload

### 🚀 Backend URL
http://127.0.0.1:8000

### ⚠️ Notes
- `.venv` folder is not included in Git
- Always activate `.venv` before running backend


--------------------------------------------------

## 📱 Frontend (React Native)

### 📌 Setup Steps

1. Create React Native app
   npx @react-native-community/cli init frontend

2. Go to frontend folder
   cd frontend

3. Install dependencies
   npm install


### ▶️ Run the App

1. Run Android app ------->>> Open forntend folder on cmd and run command.
   npx react-native run-android


--------------------------------------------------

## 🔄 Workflow

1. Start backend server
2. Start frontend app
3. Connect frontend to backend using:
   http://127.0.0.1:8000


--------------------------------------------------

## 📌 Tech Stack

- Backend: FastAPI  
- Frontend: React Native  
- Languages: Python, JavaScript