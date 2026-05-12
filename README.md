# Ankit Verma — Portfolio

A full-stack portfolio built with a single-page HTML/JS frontend and a FastAPI backend for contact form handling.

## Project Structure

```
portifolio/
├── ankitportfolio.html   # Frontend (static, self-contained)
├── backend/
│   ├── main.py           # FastAPI application
│   └── requirements.txt  # Python dependencies
├── Dockerfile            # Container for the backend
├── docker-compose.yml    # Local dev with Docker
├── Procfile              # For Heroku / Railway / Render
├── .env.example          # Environment variable template
└── .gitignore
```

---

## Local Development

### 1. Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload --port 8000
```

The API will be at `http://localhost:8000`.  
Swagger UI (debug mode): `http://localhost:8000/docs`

> Enable debug mode: `set DEBUG=true` (Windows) / `export DEBUG=true` (macOS/Linux)

### 2. Frontend

Open `ankitportfolio.html` directly in your browser, or serve it with any static file server:

```bash
npx serve .
```

---

## Deployment

### Option A — Render (recommended, free tier)

1. Push the repo to GitHub.
2. Create a new **Web Service** on [render.com](https://render.com).
3. Set **Build Command**: `pip install -r backend/requirements.txt`
4. Set **Start Command**: `gunicorn backend.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
5. Add environment variables (see `.env.example`):
   - `ALLOWED_ORIGINS` = your frontend domain (e.g. `https://ankitverma.netlify.app`)
6. Deploy the static `ankitportfolio.html` on **Netlify** / **GitHub Pages** / **Cloudflare Pages**.
7. In `ankitportfolio.html`, update `API_BASE` constant to your Render backend URL.

### Option B — Docker

```bash
docker compose up --build
```

### Option C — Heroku / Railway

```bash
git push heroku main   # Procfile is already configured
```

---

## Environment Variables

| Variable         | Description                          | Default                    |
|------------------|--------------------------------------|----------------------------|
| `DATABASE_URL`   | Database connection string           | `sqlite:///./portfolio.db` |
| `ALLOWED_ORIGINS`| Comma-separated allowed CORS origins | `localhost` variants       |
| `DEBUG`          | Expose `/docs` and `/redoc`          | unset (disabled)           |
