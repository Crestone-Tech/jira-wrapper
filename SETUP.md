# Setup and Installation Guide - Windows PowerShell

This guide will walk you through setting up the jira-wrapper project from scratch on Windows using PowerShell.

## Prerequisites

Before you begin, make sure you have:

1. **Python 3.11 or higher** installed
   - Check with: `python --version`
   - Download from: https://www.python.org/downloads/
   - **Important:** During installation, check "Add Python to PATH"

2. **PowerShell 5.1 or higher** (Windows 10/11 comes with PowerShell 5.1+)
   - Check with: `$PSVersionTable.PSVersion`
   - If needed, install PowerShell 7+ from: https://aka.ms/powershell-release

3. **A Jira instance** with API access
   - You'll need:
     - Jira base URL (e.g., `https://your-domain.atlassian.net`)
     - Your email address
     - An API token (see [Getting a Jira API Token](#getting-a-jira-api-token) below)

## Step-by-Step Setup

### Step 1: Open PowerShell

1. Press `Win + X` and select **Windows PowerShell** or **Terminal**
2. Or search for "PowerShell" in the Start menu
3. Navigate to your project directory (if not already there)

### Step 2: Verify Python Version

```powershell
python --version
```

You should see something like: `Python 3.11.x` or higher

**If Python is not found:**
- Make sure Python is added to your PATH
- Restart PowerShell after installing Python
- Try `py --version` instead (Python launcher)

### Step 3: Navigate to Project Directory

```powershell
# If you're not already in the project directory
cd C:\Users\ellio\dev\gcrs_world\jira-wrapper

# Or navigate to wherever you cloned/extracted the project
cd path\to\jira-wrapper
```

### Step 4: Create a Virtual Environment (Recommended)

Using a virtual environment isolates project dependencies:

```powershell
# Create the virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1
```

**If you get an execution policy error:**
```powershell
# Run this command to allow scripts (one-time setup)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You should see `(venv)` at the beginning of your PowerShell prompt when activated.

**Alternative activation method (if above doesn't work):**
```powershell
.\venv\Scripts\activate
```

### Step 5: Install the Project

Install the project in editable mode with all dependencies:

```powershell
# Install with development dependencies (includes pytest for testing)
pip install -e ".[dev]"
```

This will install:
- `jira` - The underlying Jira library
- `pydantic` - For data validation and models
- `python-dotenv` - For loading environment variables
- `pytest` - For running tests (dev dependency)
- `pytest-cov` - For test coverage (dev dependency)
- `pytest-mock` - For mocking in tests (dev dependency)

**Note:** The installation may take a few minutes as it downloads all dependencies.

### Step 6: Verify Installation

Check that the package is installed correctly:

```powershell
python -c "import jira_wrapper; print(jira_wrapper.__version__)"
```

You should see: `0.1.0`

### Step 7: Set Up Environment Variables

Create a `.env` file in the project root:

**Option 1: Using PowerShell (Recommended)**
```powershell
New-Item -Path .env -ItemType File
```

**Option 2: Using Notepad**
```powershell
notepad .env
```

**Option 3: Using VS Code (if installed)**
```powershell
code .env
```

Then add your Jira credentials to `.env`:

```
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_api_token_here
JIRA_PROJECT_KEY=PROJ
JIRA_TIMEOUT_SECONDS=30
```

**⚠️ Important:** Never commit the `.env` file to version control! It contains sensitive credentials.

**To edit the file later:**
```powershell
notepad .env
# or
code .env
```

### Step 8: Get Your Jira API Token

If you don't have a Jira API token yet:

1. Log in to your Jira instance
2. Click on your profile picture (top right)
3. Go to **Account Settings** → **Security**
4. Find **API tokens** section
5. Click **Create API token**
6. Give it a label (e.g., "jira-wrapper")
7. Copy the token and paste it into your `.env` file

### Step 9: Test the Installation

Run the test suite to verify everything works:

```powershell
pytest
```

You should see all tests passing. If you want more detailed output:

```powershell
pytest -v
```

For test coverage:

```powershell
pytest --cov=jira_wrapper --cov-report=term
```

### Step 10: Try a Quick Test

Create a simple test script to verify your connection:

**Using PowerShell to create the file:**
```powershell
@"
from jira_wrapper import JiraWrapper

try:
    jira = JiraWrapper.from_env()
    print("✅ Successfully connected to Jira!")
    print(f"   Base URL: {jira.config.base_url}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
"@ | Out-File -FilePath test_connection.py -Encoding utf8
```

**Or create it manually with Notepad:**
```powershell
notepad test_connection.py
```

Then paste this content:
```python
from jira_wrapper import JiraWrapper

try:
    jira = JiraWrapper.from_env()
    print("✅ Successfully connected to Jira!")
    print(f"   Base URL: {jira.config.base_url}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run it:

```powershell
python test_connection.py
```

## Troubleshooting

### Issue: "No module named 'jira'"

**Solution:** Make sure you've activated your virtual environment and installed dependencies:
```powershell
# Make sure venv is activated (you should see (venv) in prompt)
.\venv\Scripts\Activate.ps1

# Then install
pip install -e ".[dev]"
```

### Issue: "ModuleNotFoundError: No module named 'dotenv'"

**Solution:** The `python-dotenv` package might not be installed. Reinstall:
```powershell
pip install python-dotenv
```

### Issue: Execution Policy Error when activating venv

**Error:** `cannot be loaded because running scripts is disabled on this system`

**Solution:** Run this command (one-time setup):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again:
```powershell
.\venv\Scripts\Activate.ps1
```

### Issue: "JiraAuthenticationError: Failed to authenticate"

**Possible causes:**
1. Wrong email address
2. Invalid or expired API token
3. Incorrect base URL

**Solution:**
- Double-check your `.env` file values
- Generate a new API token in Jira
- Make sure the base URL doesn't have a trailing slash

### Issue: "ValidationError" when loading config

**Solution:** Make sure all required environment variables are set:
- `JIRA_BASE_URL`
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`

### Issue: Tests fail with import errors

**Solution:** Make sure you're in the project directory and have installed in editable mode:
```powershell
# Verify you're in the right directory
Get-Location

# Should show: C:\Users\ellio\dev\gcrs_world\jira-wrapper

# Reinstall if needed
pip install -e ".[dev]"
```

### Issue: Python command not found

**Solution:** Try using `py` instead of `python`:
```powershell
py --version
py -m venv venv
py -m pip install -e ".[dev]"
```

Or add Python to your PATH:
1. Search for "Environment Variables" in Windows
2. Edit "Path" variable
3. Add Python installation directory (e.g., `C:\Python311`)
4. Add Scripts directory (e.g., `C:\Python311\Scripts`)
5. Restart PowerShell

## Next Steps

Once setup is complete:

1. **Read the README.md** for usage examples
2. **Check FEATURES.md** to see what's implemented
3. **Try creating your first issue:**
   ```python
   from jira_wrapper import JiraWrapper, IssueCreate
   
   jira = JiraWrapper.from_env()
   issue = jira.create_issue(
       IssueCreate(
           project_key='PROJ',
           summary='Test issue',
           description='This is a test'
       )
   )
   print(f"Created: {issue.key}")
   ```

## Development Workflow

1. **Open PowerShell** and navigate to project directory
2. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
3. **Make changes** to the code
4. **Run tests** to verify:
   ```powershell
   pytest
   ```
5. **Check coverage:**
   ```powershell
   pytest --cov=jira_wrapper --cov-report=term
   ```
6. **Test manually** with your Jira instance

## Quick Reference Commands

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Deactivate virtual environment
deactivate

# Install/update dependencies
pip install -e ".[dev]"

# Run tests
pytest
pytest -v  # Verbose output

# Run with coverage
pytest --cov=jira_wrapper --cov-report=html
# Then open htmlcov/index.html in browser

# Check installed packages
pip list

# Update pip
python -m pip install --upgrade pip
```

## Uninstalling

To remove the package:

```powershell
pip uninstall jira-wrapper
```

To remove the virtual environment:

```powershell
# Deactivate first
deactivate

# Then delete the venv directory
Remove-Item -Recurse -Force venv
```

## Additional Windows-Specific Tips

### Using Git Bash instead of PowerShell

If you prefer Git Bash (which comes with Git for Windows):

```bash
# Create venv
python -m venv venv

# Activate (Git Bash uses different syntax)
source venv/Scripts/activate

# Rest of commands are the same
pip install -e ".[dev]"
```

### Using Windows Terminal

Windows Terminal provides a better experience:
- Install from Microsoft Store or: https://aka.ms/terminal
- Supports tabs, multiple shells (PowerShell, CMD, Git Bash)
- Better Unicode support

### File Encoding

If you encounter encoding issues with `.env` file:
```powershell
# Create .env with UTF-8 encoding
New-Item -Path .env -ItemType File -Value "JIRA_BASE_URL=https://example.atlassian.net`nJIRA_EMAIL=user@example.com`nJIRA_API_TOKEN=token" -Encoding UTF8
```

