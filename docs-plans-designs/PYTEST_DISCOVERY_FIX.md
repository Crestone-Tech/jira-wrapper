# Fixing Pytest Discovery Error in VS Code

If you're seeing "pytest discovery error" in the VS Code test tab, follow these steps:

## Quick Fix Steps

### 1. Select the Correct Python Interpreter

**In VS Code:**
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: `Python: Select Interpreter`
3. Choose the interpreter from your venv:
   ```
   .\venv\Scripts\python.exe
   ```
   Or the full path:
   ```
   C:\Users\ellio\dev\gcrs_world\jira-wrapper\venv\Scripts\python.exe
   ```

**Verify it's selected:**
- Look at the bottom-right of VS Code status bar
- It should show: `Python 3.x.x ('venv': venv)`

### 2. Reload VS Code Window

After selecting the interpreter:
1. Press `Ctrl+Shift+P`
2. Type: `Developer: Reload Window`
3. Press Enter

### 3. Check Test Discovery

1. Open the Test Explorer (beaker icon in sidebar, or `Ctrl+Shift+T`)
2. VS Code should automatically discover tests
3. If not, click the refresh icon in the Test Explorer

## Manual Test Discovery

If automatic discovery doesn't work:

1. Open Command Palette (`Ctrl+Shift+P`)
2. Type: `Python: Configure Tests`
3. Select: `pytest`
4. Select: `tests` (or the root directory)

## Verify Setup

Run these commands in PowerShell to verify everything is set up:

```powershell
# Make sure venv is activated
.\venv\Scripts\Activate.ps1

# Check pytest is installed
pytest --version

# Check Python can import the package
python -c "import jira_wrapper; print('OK')"

# Run tests manually
pytest tests/ -v
```

## Common Issues

### Issue: "No tests discovered"

**Solution:**
1. Make sure `.vscode/settings.json` exists (created above)
2. Check that `python.testing.pytestEnabled` is `true`
3. Reload VS Code window
4. Check the Output panel (`View` → `Output` → select "Python Test Log")

### Issue: "Python extension not installed"

**Solution:**
1. Install the Python extension from VS Code marketplace
2. Search for: "Python" by Microsoft
3. Install and reload VS Code

### Issue: "Import errors in tests"

**Solution:**
1. Make sure you've installed dependencies:
   ```powershell
   pip install -e ".[dev]"
   ```
2. Check that the venv Python is selected
3. Restart VS Code

### Issue: "pytest not found"

**Solution:**
1. Activate venv: `.\venv\Scripts\Activate.ps1`
2. Install pytest: `pip install pytest`
3. Or reinstall all: `pip install -e ".[dev]"`

## VS Code Settings File

The `.vscode/settings.json` file has been created with:
- Correct Python interpreter path
- Pytest enabled
- Test discovery configured
- Python path set correctly

If you need to manually edit it:
1. Press `Ctrl+Shift+P`
2. Type: `Preferences: Open Workspace Settings (JSON)`

## Still Not Working?

1. **Check Output Panel:**
   - `View` → `Output`
   - Select "Python Test Log" from dropdown
   - Look for error messages

2. **Check Python Extension:**
   - Make sure Python extension is installed and enabled
   - Check extension version (should be recent)

3. **Try Manual Command:**
   ```powershell
   # In terminal, run:
   python -m pytest tests/ --collect-only
   ```
   This shows what pytest can discover

4. **Reset VS Code:**
   - Close VS Code
   - Delete `.vscode` folder (optional, will recreate)
   - Reopen VS Code
   - Select Python interpreter again

## Alternative: Run Tests from Terminal

If VS Code test discovery still doesn't work, you can always run tests from the terminal:

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models.py -v

# Run specific test
pytest tests/test_models.py::TestIssueCreate::test_to_jira_dict_basic -v
```

