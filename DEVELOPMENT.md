# 🚀 CityCamp AI Development Guide

## **Quick Start (Recommended)**

### **One-Command Startup:**
```bash
./scripts/start-dev.sh
```

This will:
- ✅ Automatically activate the virtual environment
- ✅ Clean up any existing processes
- ✅ Start both backend (Port 8000) and frontend (Port 3003/3004)
- ✅ Show service status and URLs
- ✅ Monitor both services

---

## **Manual Development Setup**

### **Option 1: Always Use Virtual Environment (Manual)**
```bash
# Every time you start development:
source scripts/activate-dev.sh

# Then start services:
cd backend && python -m app.main     # Terminal 1
cd frontend && npm run dev           # Terminal 2
```

### **Option 2: Automatic Virtual Environment (With direnv)**
```bash
# Install direnv (one-time setup):
brew install direnv                  # macOS
# or: sudo apt install direnv        # Linux

# Add to your shell (one-time):
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
source ~/.zshrc

# Allow the project:
direnv allow .

# Now the virtual environment activates automatically when you enter the directory!
```

---

## **🔧 Virtual Environment Management**

### **The Problem You Were Having:**
- You were running Python commands in the conda `(base)` environment
- The project dependencies are installed in `backend/venv/`
- Without activating the virtual environment, Python couldn't find the `app` module

### **How to Always Use Virtual Environment:**

**Method 1: Manual Activation (Every Session)**
```bash
cd /path/to/CityCamp_AI
source scripts/activate-dev.sh
# Now you're in the virtual environment for this terminal session
```

**Method 2: Automatic with direnv (Recommended)**
- The `.envrc` file will automatically activate the virtual environment
- Install direnv and allow the project (see Option 2 above)

**Method 3: IDE Integration**
- **VS Code**: Select the Python interpreter from `backend/venv/bin/python`
- **PyCharm**: Set Project Interpreter to `backend/venv/bin/python`

---

## **🎯 Development URLs**

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3003 | React app (main UI) |
| Backend API | http://localhost:8000 | FastAPI server |
| API Documentation | http://localhost:8000/docs | Interactive API docs |
| Health Check | http://localhost:8000/health | Backend status |

---

## **📊 Monitoring & Debugging**

### **Check Service Status:**
```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3003/

# Test meetings API
curl http://localhost:8000/api/v1/meetings/
```

### **View Logs:**
```bash
# If using start-dev.sh:
tail -f logs/backend.log
tail -f logs/frontend.log

# Check running processes:
ps aux | grep -E "(python.*app.main|vite)"
```

### **Kill Stuck Processes:**
```bash
# Kill by port
lsof -ti :8000 | xargs kill -9  # Backend
lsof -ti :3003 | xargs kill -9  # Frontend

# Or use the process IDs shown by start-dev.sh
kill [BACKEND_PID] [FRONTEND_PID]
```

---

## **🐛 Common Issues & Solutions**

### **"Address already in use" Error**
```bash
# Kill existing processes:
lsof -ti :8000 :3003 :3004 | xargs kill -9 2>/dev/null || true
```

### **"ModuleNotFoundError: No module named 'app'" Error**
```bash
# You're not in the virtual environment:
source scripts/activate-dev.sh
# Then try again
```

### **Frontend Import Errors (like CheckIcon)**
```bash
# Clear caches:
rm -rf frontend/node_modules/.vite frontend/dist
npm cache clean --force
```

### **Can't Connect to Database**
```bash
# Check if .env file exists:
ls -la backend/.env

# If missing, create it:
./scripts/setup_dev_environment.sh
```

---

## **⚙️ Environment Files**

### **Backend Environment (backend/.env)**
```bash
# View current environment:
cat backend/.env

# Recreate if needed:
./scripts/setup_dev_environment.sh
```

### **Scripts Available:**
- `scripts/activate-dev.sh` - Manual environment activation
- `scripts/start-dev.sh` - Complete development startup
- `scripts/setup_dev_environment.sh` - Create .env file
- `.envrc` - Automatic activation with direnv

---

## **🎯 Recommended Development Workflow**

### **Daily Startup:**
```bash
cd CityCamp_AI
./scripts/start-dev.sh
# Wait for "Development environment ready!" message
# Open http://localhost:3003 in your browser
```

### **Working with the Code:**
- Backend changes auto-reload (FastAPI with `--reload`)
- Frontend changes auto-reload (Vite HMR)
- Database changes require manual restart

### **Shutdown:**
```bash
# Press Ctrl+C in the start-dev.sh terminal
# Or kill the specific PIDs shown in the startup output
```

---

## **✅ Verification Checklist**

After starting development servers:

- [ ] Backend health: http://localhost:8000/health
- [ ] API docs load: http://localhost:8000/docs
- [ ] Frontend loads: http://localhost:3003
- [ ] Meetings page shows data: http://localhost:3003/meetings
- [ ] Virtual environment active: `which python` shows `venv/bin/python`

---

**🎉 You should now have:**
- ✅ Automatic virtual environment activation
- ✅ Both services running on correct ports
- ✅ Meeting data loading from the backend
- ✅ No more import or module errors
- ✅ Simple one-command development startup
