# AgentShield Deployment Guide

## System Requirements

- **Python**: 3.9 or higher
- **Node.js**: 18 or higher
- **npm**: 8 or higher
- **Git**: For version control
- **SQLite**: For database (included with Python)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AgentShield
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

### 4. Environment Setup

```bash
# Create .env file from example
cp backend/.env.example backend/.env

# Edit backend/.env with your configuration
# GEMINI_API_KEY=your_key_here (optional, uses mock mode if not set)
```

## Running the Application

### Start Backend Server

```bash
cd backend

# Using uvicorn directly
uvicorn main:app --reload --port 8000

# Or using Python module
python -m uvicorn main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Start Frontend Development Server

```bash
cd frontend

# Development mode with hot reload
npm run dev

# Frontend will be available at http://localhost:5173
```

### Production Build

For production deployment, build the frontend first:

```bash
cd frontend
npm run build

# Output will be in dist/ directory
```

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_integration.py -v

# Run with coverage report
python -m pytest tests/ --cov=.
```

### Frontend Tests

```bash
cd frontend

# If tests are configured
npm run test
```

## Database Management

### Initialize Database

The database is automatically initialized on first backend startup. Demo data is seeded if the database is empty.

### Reset Database

To reset and reseed the database:

```bash
# Delete the database file
rm agentshield.db

# Restart the backend - it will automatically recreate and seed
cd backend
uvicorn main:app --reload --port 8000
```

### Database File Location

- **Development**: `backend/agentshield.db` (SQLite file)
- **In-memory (tests)**: Temporary in-memory SQLite databases

## Project Structure

```
AgentShield/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── database/            # Database models and initialization
│   ├── routes/              # API endpoint handlers
│   ├── security/            # Security engines (gateway, injection detection, etc.)
│   ├── agent/               # AI agent service and mock agent
│   ├── tools/               # Tool implementations
│   ├── tests/               # Test suites
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages/components
│   │   ├── components/      # Reusable components
│   │   ├── utils/           # Utility functions and API client
│   │   └── index.tsx        # Entry point
│   ├── package.json         # Node dependencies
│   └── tsconfig.json        # TypeScript configuration
└── docs/                    # Documentation files
```

## API Endpoints

### Health & Status

- `GET /health` - Health check
- `GET /api/status` - API status
- `GET /api/gateway/health` - Gateway health

### Gateway Evaluation

- `POST /api/gateway/evaluate` - Evaluate tool call security
- `GET /api/gateway/events` - Get security events

### Agent Endpoints

- `POST /api/agent/message` - Process user message through agent
- `POST /api/agent/mock` - Mock agent with scenarios
- `GET /api/agent/status` - Agent status (mock or live)

### Security Events & Threats

- `GET /api/events` - Get security events
- `GET /api/threats` - Get detected threats
- `GET /api/activity-logs` - Get activity logs

### Policies & Configuration

- `GET /api/policies` - Get security policies
- `GET /api/policies/{id}` - Get specific policy

## Troubleshooting

### Backend Won't Start

- Ensure Python 3.9+ is installed: `python --version`
- Check if port 8000 is available: `netstat -an | grep 8000`
- Verify all dependencies installed: `pip install -r requirements.txt`

### Frontend Build Errors

- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Clear npm cache: `npm cache clean --force`
- Check Node version: `node --version` (should be 18+)

### Database Issues

- Delete corrupted database and restart backend to reseed
- Check file permissions on `agentshield.db`

### CORS Issues

- Backend CORS is configured for localhost:5173 and localhost:3000
- Modify CORS settings in `backend/main.py` if using different ports

## Performance Optimization

### Backend

- Use production ASGI server (e.g., Gunicorn + Uvicorn) instead of `--reload`
- Enable caching for policy lookups
- Consider database connection pooling for production

### Frontend

- Built assets are optimized and minified
- Serve from CDN for production
- Enable gzip compression in web server

## Security Considerations

- Never commit `.env` files with real API keys to version control
- Use HTTPS in production (reverse proxy with SSL)
- Implement authentication/authorization middleware
- Regularly update dependencies: `pip install --upgrade -r requirements.txt`
- Run security tests: `pytest tests/test_gateway.py -v`

## Deployment Platforms

### Local Development
```bash
# Terminal 1 - Backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### Docker (Optional)

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment

- **Heroku**: Configure Procfile with gunicorn and build scripts
- **AWS**: Use Lambda for API, S3 for frontend
- **Google Cloud**: Cloud Run for backend, Firebase Hosting for frontend
- **Vercel**: Frontend deployment with serverless backend option

## Support & Documentation

- API Documentation: http://localhost:8000/docs (Swagger UI)
- Architecture: See `docs/ARCHITECTURE.md`
- Attack Scenarios: See `docs/ATTACKS.md`
- README: See `README.md`
