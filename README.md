# TripPilot

Full-stack trip planning application: flight search, weather, hotels,
activities, and personal favorites.

**Live demo:** https://trippilot-irs3.onrender.com/

## MVP Features

- Route search followed by redirection to Luxair, Air France, and Ryanair
- Autocomplete across nearly 7,900 airports by code, city, or name
- Flight redirection to the airline's official website
- Hotel and activity redirection to a booking/search page
- Full interface in French and English
- Dark mode remembered in the browser
- Live current weather via Open-Meteo
- 10 demo hotels and 5 demo activities per destination
- Nearby airport detection using browser location permission
- No position stored on the server
- Separate sign-up and login pages, secured by session
- Flight and destination favorites
- No API key required for flights, weather, or location
- CSRF protection, input validation, `scrypt` hashing, secure cookies,
  and parameterized SQL queries via SQLAlchemy

## Running the Project

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

The API starts on `http://localhost:5000`.

On Windows PowerShell, use instead:

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173`. Vite automatically forwards `/api`
to the Flask backend, including session cookies.

## Tests

```bash
cd backend
pytest
```

```bash
cd frontend
npm run build
```

## How Flight Search Works

TripPilot prepares the route, date, and number of travelers, then
suggests the official websites of Luxair, Air France, and Ryanair.
Schedules and prices are not invented within the application: they are
checked on the chosen airline's website.

Before any production deployment, replace `SECRET_KEY` in `.env` with
a long random value and set `FLASK_ENV=production`. You can generate
a key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Destinations and Weather

The search recognizes IATA codes, cities, and airport names. For
example, `NYC` or `New Y` suggests New York's airports. The default
departure point is `LUX`. Weather is fetched live. Hotels and
activities are demo suggestions and open an external search.

The "Use my nearest airport" button uses the browser's built-in
location feature. The position is sent only long enough to calculate
the distance to airports and is not stored.

## Free Deployment: Render + Neon

The React frontend is built and then served by Flask on the same
domain. This avoids any CORS configuration and lets secure cookies
and CSRF protection work simply.

### 1. Create the free PostgreSQL database

1. Create an account on [Neon](https://console.neon.tech/) and a project.
2. In **Connect**, copy the full PostgreSQL connection string. It
   starts with `postgresql://` and must contain `sslmode=require`.
3. Never publish this value and never add it to Git.

### 2. Push the project to GitHub

Create a GitHub repository, then from the TripPilot folder:

```bash
git init
git add .
git commit -m "Prepare TripPilot deployment"
git branch -M main
git remote add origin https://github.com/YOUR-ACCOUNT/YOUR-REPO.git
git push -u origin main
```

### 3. Deploy on Render

1. On [Render](https://dashboard.render.com/), choose **New > Blueprint**.
2. Connect the GitHub repository. Render will automatically detect
   `render.yaml`.
3. When it asks for `DATABASE_URL`, paste the Neon connection string.
4. Start the deployment. `SECRET_KEY` is generated automatically by
   Render.
5. Open the free address `https://tripilot-....onrender.com`.

The endpoint `https://YOUR-SITE.onrender.com/api/health` should
respond with `{"status":"ok","service":"TripPilot API"}`.

### Local Production Check

```bash
npm ci --prefix frontend
npm run build --prefix frontend
pip install -r backend/requirements.txt
gunicorn --chdir backend --workers 1 --threads 4 run:app
```

Then open `http://localhost:8000`. In development, SQLite is used
if `DATABASE_URL` is not set.
