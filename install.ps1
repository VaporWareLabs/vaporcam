# setup_dev.ps1
# PowerShell script to create a local Django development environment
# for the Project Controls application.

Write-Host "========================================"
Write-Host " VaporCAM - Development Setup"
Write-Host "========================================"

# Ensure we are in the project root
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PROJECT_ROOT

# ---------------------------------------------------------------------
# 1. Create Python virtual environment
# ---------------------------------------------------------------------
if (-not (Test-Path ".venv")) {
    Write-Host "`nCreating virtual environment..."
    python -m venv .venv
} else {
    Write-Host "`nVirtual environment already exists."
}

# ---------------------------------------------------------------------
# 2. Activate virtual environment
# ---------------------------------------------------------------------
Write-Host "Activating virtual environment..."
& ".\.venv\Scripts\Activate.ps1"

# ---------------------------------------------------------------------
# 3. Upgrade pip
# ---------------------------------------------------------------------
Write-Host "`nUpgrading pip..."
python -m pip install --upgrade pip

# ---------------------------------------------------------------------
# 4. Install required packages
# ---------------------------------------------------------------------
if (Test-Path "requirements.txt") {
    Write-Host "`nInstalling dependencies from requirements.txt..."
    pip install -r requirements.txt
} else {
    Write-Host "`nNo requirements.txt found. Installing core packages..."
    pip install django requests python-dotenv openpyxl
}

# ---------------------------------------------------------------------
# 5. Create .env file if missing
# ---------------------------------------------------------------------
if (-not (Test-Path ".env")) {
    Write-Host "`nCreating .env template..."
    $template = @"
JIRA_BASE_URL=https://jira.example.org
JIRA_PAT=your_personal_access_token_here
JIRA_JQL=project = vaporCAM AND issuetype = Story AND (statusCategory != Done OR resolved >= "2026-03-01")
"@
    # Use .NET method to write UTF-8 without BOM
    [System.IO.File]::WriteAllText((Join-Path $PROJECT_ROOT ".env"), $template, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host ".env file created. Edit it with your Jira settings."
} else {
    Write-Host "`n.env file already exists."
    
    # Remove UTF-8 BOM if present to prevent issues with environment variable loading
    Write-Host "Checking .env for UTF-8 BOM..."
    $envFile = Join-Path $PROJECT_ROOT ".env"
    $bytes = [System.IO.File]::ReadAllBytes($envFile)
    if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        Write-Host "BOM detected! Removing it..."
        $content = [System.IO.File]::ReadAllText($envFile)
        [System.IO.File]::WriteAllText($envFile, $content, (New-Object System.Text.UTF8Encoding($false)))
        Write-Host "BOM removed successfully."
    } else {
        Write-Host "No BOM detected."
    }
}

# ---------------------------------------------------------------------
# 6. Run migrations
# ---------------------------------------------------------------------
Write-Host "`nRunning Django migrations..."
python manage.py makemigrations
python manage.py migrate

# ---------------------------------------------------------------------
# 7. Optional superuser
# ---------------------------------------------------------------------
Write-Host "`nSetup complete."

Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Edit .env with your Jira URL and PAT"
Write-Host "2. Create a SuperUser account:"
Write-Host "      python manage.py createsuperuser"
Write-Host "3. Activate the environment:"
Write-Host "      .\.venv\Scripts\Activate.ps1"
Write-Host "4. Sync Jira:"
Write-Host "      python manage.py sync_jira"
Write-Host "5. Start server:"
Write-Host "      python manage.py runserver"
Write-Host ""
Write-Host "Open http://127.0.0.1:8000/"