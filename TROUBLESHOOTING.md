# LexIndia Project - Troubleshooting Guide

## Quick Fixes (Try These First)

### 1. **Port Already in Use (Most Common)**

```powershell
# Kill Python process using port 8000
taskkill /F /IM python.exe
Start-Sleep -Seconds 2

# Then start backend again
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. **Dependencies Missing**

```powershell
# Activate virtual environment
cd backend
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Try again
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. **Database Issues**

```powershell
# Reseed database
cd backend
python seed_data.py

# Regenerate embeddings
python setup/generate_embeddings.py
```

### 4. **Python Cache Conflict**

```powershell
# Delete all cache files
cd backend
Get-ChildItem -Path . -Directory -Filter __pycache__ -Recurse | Remove-Item -Recurse -Force

# Try again
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Complete Fresh Start

### Option 1: Automatic (Recommended)

```powershell
# Run the fresh start script
.\start_project_fresh.ps1
```

### Option 2: Manual Step-by-Step

```powershell
# 1. Kill old processes
taskkill /F /IM python.exe 2>$null

# 2. Activate virtual environment
cd backend
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Seed database
python seed_data.py

# 5. Generate embeddings
python setup/generate_embeddings.py

# 6. Start backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Common Errors & Solutions

### Error: "Address already in use"

**Problem:** Port 8000 still in use
**Solution:**

```powershell
taskkill /F /IM python.exe
Start-Sleep -Seconds 2
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Error: "ModuleNotFoundError: No module named 'xyz'"

**Problem:** Missing dependencies
**Solution:**

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Error: "connection refused" (database)

**Problem:** PostgreSQL not running or database empty
**Solution:**

```powershell
# Reseed database
cd backend
python seed_data.py

# Check database
python check_db.py
```

### Error: "No embeddings found" / "Fallback mode"

**Problem:** Embeddings not generated
**Solution:**

```powershell
cd backend
python setup/generate_embeddings.py
```

### Error: "Frontend build fails"

**Problem:** Node modules missing
**Solution:**

```powershell
cd frontend
npm install
npm run build
```

---

## Checklist Before Running

- [ ] Close VS Code or restart it
- [ ] Kill all Python/Node processes
- [ ] Virtual environment activated
- [ ] Dependencies installed (pip install -r requirements.txt)
- [ ] Database seeded (python seed_data.py)
- [ ] Embeddings generated (python setup/generate_embeddings.py)
- [ ] .env file exists with correct config
- [ ] No **pycache** conflicts (delete if exists)
- [ ] Port 8000 not in use (taskkill /F /IM python.exe)

---

## Development Workflow Best Practices

### When Starting Work

```powershell
# 1. Kill old processes
taskkill /F /IM python.exe 2>$null

# 2. Activate venv
cd backend
.\venv\Scripts\Activate.ps1

# 3. Pull latest changes
cd ..
git pull origin master

# 4. Install any new dependencies
cd backend
pip install -r requirements.txt

# 5. Start backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### When Making Changes

```powershell
# 1. Make your changes in VS Code
# 2. Changes auto-reload (--reload flag)
# 3. Test changes

# 4. When done, commit
cd ..
git add .
git commit -m "Description of changes"
git push origin master
```

### After Pulling Changes

```powershell
# Always rerun fresh start
.\start_project_fresh.ps1
```

---

## Advanced Troubleshooting

### Check What's Using Port 8000

```powershell
Get-NetTCPConnection -LocalPort 8000 | Select-Object -Property State, OwningProcess
```

### View Python Process Details

```powershell
Get-Process python | Select-Object Id, ProcessName, Path, Threads
```

### Check Database Connection

```powershell
cd backend
python check_db.py
```

### View Backend Logs

```powershell
# Last 50 lines
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 2>&1 | Select-String -Last 50
```

### Reset Everything

```powershell
# Nuclear option - reset project to clean state
cd backend

# Remove venv
Remove-Item -Recurse -Force venv

# Remove cache
Get-ChildItem -Path . -Directory -Filter __pycache__ -Recurse | Remove-Item -Recurse -Force

# Recreate everything
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed_data.py
python setup/generate_embeddings.py

# Start fresh
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Prevention Tips

1. **Always use virtual environment** - Prevents Python conflicts
2. **Close VS Code before restarting** - Releases all file locks
3. **Kill processes explicitly** - Don't rely on close buttons
4. **Commit changes regularly** - Easy to rollback if issues
5. **Use fresh start script** - Automates the entire process
6. **Check logs first** - Errors usually show root cause
7. **One terminal per service** - Backend in one, frontend in another

---

## Still Having Issues?

Try in this order:

1. Restart computer
2. Run fresh start script: `.\start_project_fresh.ps1`
3. Check git status: `git status`
4. Reset to last commit: `git reset --hard HEAD`
5. Delete venv and reinstall: Nuclear option above
6. Check error logs carefully - they usually tell you what's wrong

Good luck! 🚀
