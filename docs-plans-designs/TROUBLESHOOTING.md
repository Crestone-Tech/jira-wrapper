# Troubleshooting Guide

## Common Issues and Solutions

### Issue: "No module named 'jira'" or "No module named 'pytest'"

**Symptoms:**
- `ModuleNotFoundError: No module named 'jira'`
- `No module named pytest`
- Tests fail to run

**Cause:** Dependencies are not installed or virtual environment is not activated.

**Solution:**

1. **Make sure you're in the project directory:**
   ```powershell
   cd C:\Users\ellio\dev\gcrs_world\jira-wrapper
   ```

2. **Activate your virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   You should see `(venv)` at the start of your prompt.

3. **Install the package with all dependencies:**
   ```powershell
   pip install -e ".[dev]"
   ```

4. **Verify installation:**
   ```powershell
   pip list | Select-String "jira"
   pip list | Select-String "pytest"
   ```

5. **Try running tests again:**
   ```powershell
   pytest
   ```

### Issue: "The python test process was terminated before it could exit"

**Symptoms:**
- Test process exits with code 1
- No clear error message shown
- Tests don't run

**Possible Causes:**

1. **Dependencies not installed** (most common)
   - See solution above

2. **Import errors in test files**
   - Check that all imports work:
     ```powershell
     python -c "import jira_wrapper"
     ```

3. **Syntax errors in test files**
   - Check for Python syntax errors:
     ```powershell
     python -m py_compile tests/test_*.py
     ```

**Solution:**

Run tests with verbose output to see the actual error:
```powershell
pytest -v
```

Or run a specific test file:
```powershell
pytest tests/test_models.py -v
```

### Issue: Virtual Environment Not Activated

**Symptoms:**
- `pip list` doesn't show `jira-wrapper`
- Python can't find installed modules
- Tests fail with import errors

**Solution:**

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Verify activation (should show venv path)
where python
# Should show: C:\Users\ellio\dev\gcrs_world\jira-wrapper\venv\Scripts\python.exe
```

### Issue: "Execution Policy" Error

**Symptoms:**
```
cannot be loaded because running scripts is disabled on this system
```

**Solution:**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again:
```powershell
.\venv\Scripts\Activate.ps1
```

### Issue: Tests Pass but IDE Shows Errors

**Symptoms:**
- Tests run fine with `pytest`
- But IDE (VS Code, PyCharm) shows import errors

**Solution:**

1. **Select the correct Python interpreter:**
   - In VS Code: Press `Ctrl+Shift+P` → "Python: Select Interpreter"
   - Choose the one in `venv\Scripts\python.exe`

2. **Reload the window:**
   - VS Code: `Ctrl+Shift+P` → "Developer: Reload Window"

### Issue: "pytest: command not found"

**Symptoms:**
- `pytest` command doesn't work
- But `python -m pytest` works

**Solution:**

Use the module form:
```powershell
python -m pytest
```

Or ensure pytest is in your PATH (should be after `pip install -e ".[dev]"`).

### Quick Diagnostic Commands

Run these to check your setup:

```powershell
# 1. Check Python version
python --version

# 2. Check if venv is activated (should show venv path)
where python

# 3. Check installed packages
pip list

# 4. Check if jira-wrapper is installed
pip show jira-wrapper

# 5. Test imports
python -c "import jira_wrapper; print('OK')"
python -c "import pytest; print('OK')"

# 6. Run tests
pytest -v
```

### Still Having Issues?

1. **Check the full error output:**
   ```powershell
   pytest -v --tb=short
   ```

2. **Run a single test to isolate the issue:**
   ```powershell
   pytest tests/test_models.py::TestIssueCreate::test_to_jira_dict_basic -v
   ```

3. **Check for syntax errors:**
   ```powershell
   python -m py_compile jira_wrapper/*.py tests/*.py
   ```

4. **Reinstall everything:**
   ```powershell
   # Deactivate venv
   deactivate
   
   # Remove venv
   Remove-Item -Recurse -Force venv
   
   # Create new venv
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # Reinstall
   pip install -e ".[dev]"
   ```

