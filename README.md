# VaporCAM

A modern **Project Controls** web application that synchronizes Jira
work items and provides engineers and Control Account Managers (CAMs)
with a collaborative Earned Value Management (EVM) dashboard.

## Features

### Multi-Project Support

-   Support for multiple projects within a single VaporCAM instance
-   Project-specific URLs
-   Automatic project isolation
-   Foundation for future project-level permissions

### Jira Integration

-   Synchronize Jira Stories and Tasks using the Jira REST API
-   Automatic Feature hierarchy discovery
-   Import Story Points, Status, Assignee, Feature, and Charge Codes
-   Direct hyperlinks back to Jira
-   Multiple Jira projects supported

### Project Controls

-   Baseline Budget
-   Jira Story Points
-   Actuals
-   ETC
-   EAC
-   Variance
-   Feature-level rollups
-   Monthly planning for ETC and Actuals

### Dashboard

-   Spreadsheet-inspired interface
-   Collapsible Features
-   Search
-   Show Done / Hide Done
-   Sticky headers
-   Color-coded EVMS columns
-   Direct Jira links

# Installation

VaporCAM can be installed on either Windows for development or Ubuntu Linux for production deployments.

---

## Windows Development

### Clone the repository

```bash
git clone https://github.com/vaporwarelabs/vaporCAM.git
cd vaporCAM
```

### Run the installation script

```powershell
.\install.ps1
```

The installer will:

- Create a Python virtual environment
- Install required Python packages
- Create a default `.env`
- Run Django migrations

### Create a Django superuser

```powershell
python manage.py createsuperuser
```

---

## Ubuntu Linux Deployment

Production deployments are performed using the companion repository:

```
vaporCAM-deploy
```

The deployment automation configures:

- Python virtual environment
- Gunicorn
- Nginx
- systemd services
- Static files
- Django migrations
- Optional Django superuser creation

Deployment has been validated on Ubuntu 24.04 LTS.

---

# Environment Variables

Only server-specific settings belong in `.env`.

```env
DJANGO_DEBUG=False

DJANGO_ALLOWED_HOSTS=

JIRA_BASE_URL=https://jira.example.org

JIRA_PAT=
```

Project-specific configuration (Jira JQL, project names, etc.) is stored in the VaporCAM database.

---

# Running VaporCAM

## Activate the virtual environment

Windows

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux

```bash
source .venv/bin/activate
```

---

## Run database migrations

```bash
python manage.py migrate
```

---

## Create a superuser

```bash
python manage.py createsuperuser
```

---

## Synchronize Jira

Synchronize every configured project:

```bash
python manage.py sync_jira
```

Synchronize a single project:

```bash
python manage.py sync_jira --project demo-project
```

---

## Import Actuals

```bash
python manage.py import_actuals actuals.xlsx
```

---

## Start the development server

```bash
python manage.py runserver
```

Browse to:

```
http://127.0.0.1:8000/
```

or

```
http://<server-name>.local/
```

when using mDNS.

---

## Typical Development Workflow

```bash
git pull

source .venv/bin/activate

python manage.py migrate

python manage.py sync_jira

python manage.py runserver
```

## Roadmap

-   Project selector
-   Deployment hardening
-   Excel round-trip import
-   Charge code analytics
-   Database backup service
-   Project-level permissions

## Vision

VaporCAM bridges engineering execution and project controls, providing a
collaborative workspace for planning, forecasting, actuals, and earned
value management.

## Author

Brian Register\
VaporWare Labs

## License

MIT License.
