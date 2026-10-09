# AgentShield AI - Complete Setup Guide

AgentShield is a security gateway for AI agents with a full-stack application: FastAPI backend + React/TanStack frontend with integrated security engines.

## Quick Start (2 steps)

### 1. Start Backend
```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Backend runs at: **http://localhost:8000**

### 2. Start Frontend
```powershell
cd frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:8080** (or 5173 if port 8080 is busy)

---

## What's Connected

### Backend API (FastAPI)
- **Base URL:** `http://localhost:8000`
- **Key Endpoints:**
  - `GET /api/events` - Audit logs of all agent actions
  - `GET /api/threats` - Detected threats
  - `GET /api/policies` - Active security policies
  - `POST /api/agent/message` - Evaluate agent message
  - `GET /api/gateway/evaluate` - Gateway status

### Frontend (React + TanStack)
- **Port:** 8080 (or 5173)
- **Database:** SQLite (`agentshield.db` in backend folder)
- **Auto-filled Demo Data:** 3 agents, sample emails, audit logs

### CORS Configuration
Backend is configured to accept requests from:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://localhost:8080`

---

## Backend Structure

```
backend/
├── main.py                 # FastAPI app + routes
├── requirements.txt        # Python dependencies
├── database/
│   └── db.py              # SQLite setup + seed data
├── models/
│   └── schemas.py         # Pydantic models
├── security/
│   ├── prompt_injection.py
│   ├── privilege_escalation.py
│   ├── data_exfiltration.py
│   └── [8+ security engines]
├── routes/
│   ├── events.py          # Audit log endpoints
│   ├── threats.py         # Threat detection
│   └── gateway.py         # Main gateway logic
└── tests/
    └── 49 tests (all passing)
```

**Security Engines Included:**
- Prompt Injection Detection
- Privilege Escalation Prevention
- Data Exfiltration Blocking
- File Access Control
- Network Request Filtering
- API Key Detection & Redaction
- PII/Sensitive Data Detection
- Malicious Pattern Recognition
- Resource Quota Enforcement
- Behavioral Anomaly Detection

---

## Frontend Structure

```
frontend/
├── src/
│   ├── routes/
│   │   ├── index.tsx           # Landing page
│   │   ├── auth.tsx            # Authentication
│   │   └── _authenticated/
│   │       ├── dashboard.tsx   # Main dashboard
│   │       ├── emails.tsx      # Email inspection
│   │       └── [other pages]
│   ├── lib/
│   │   ├── api.ts              # Backend API client
│   │   └── data.ts             # TanStack Query hooks
│   ├── components/
│   │   └── ui/                 # Radix UI components
│   └── styles.css
├── .env                        # Backend URL config
├── package.json
└── vitest.config.ts
```

---

## Demo Walkthrough

### 1. **Dashboard**
- View security metrics
- See blocked threats count
- Review recent incidents

### 2. **Audit Logs**
- All agent actions pass through the gateway
- View decisions: ALLOW, REDACT, REVIEW, BLOCK
- Check threat level and reasons

### 3. **Attack Simulation Lab**
- Run safe attack scenarios
- Test security rules
- See how threats are blocked

### 4. **Email Inspector**
- Inspect emails for hidden instructions
- Detect prompt injection attempts
- Flag sensitive data leaks

---

## API Examples

### Get Audit Logs
```bash
curl http://localhost:8000/api/events
```

### Evaluate Agent Message
```bash
curl -X POST http://localhost:8000/api/agent/message \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "DevOpsAgent",
    "action": "file.read",
    "tool": "read_file",
    "destination": "/engineering/secrets/prod.env",
    "content": "Read production secrets"
  }'
```

### Get Threats
```bash
curl http://localhost:8000/api/threats
```

### Get Policies
```bash
curl http://localhost:8000/api/policies
```

---

## Database

**Auto-created:** `agentshield.db` (SQLite)

**Tables:**
- `agents` - AI agents (InboxAssistant, DevOpsAgent, FinanceBot)
- `resources` - Files & data classified by sensitivity
- `policies` - Security rules & clearance levels
- `emails` - Sample emails for testing
- `audit_logs` - Complete action history

**Demo Data Included:**
- ✅ 3 active agents
- ✅ 15+ sample emails
- ✅ 50+ audit log entries
- ✅ 10+ security policies

---

## Troubleshooting

### Port 8000/8080 Already in Use
```powershell
# Backend: use different port
python -m uvicorn main:app --reload --port 8001

# Frontend: npm will auto-select if 8080 is busy
```

### Backend Not Responding
1. Check backend is running: `http://localhost:8000/docs`
2. Check CORS: Backend should show no CORS errors
3. Check .env: `VITE_API_BASE=http://localhost:8000/api`

### Frontend Can't Connect
1. Verify backend is running
2. Check browser console for CORS errors
3. Ensure `VITE_API_BASE` is set in `.env`

### Database Error
```powershell
# Reset database
cd backend
rm agentshield.db
python -c "from database.db import init_db; init_db()"
```

---

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLite** - Lightweight database
- **Pydantic** - Data validation
- **pytest** - Testing

### Frontend
- **React 19** - UI library
- **TanStack Router** - Routing
- **TanStack Query** - Data fetching
- **Tailwind CSS** - Styling
- **Radix UI** - Component library
- **Recharts** - Data visualization

---

## Key Features

✅ **Real-time Security Monitoring** - Every agent action logged
✅ **Deny-by-Default Gateway** - Block threats before execution
✅ **Multiple Decision Types** - ALLOW, REDACT, REVIEW, BLOCK
✅ **Attack Simulation Lab** - Test security rules safely
✅ **Audit Trail** - Complete action history with threat levels
✅ **Policy Engine** - Enforce security rules per agent/resource
✅ **Data Loss Prevention** - Detect & redact sensitive data
✅ **Prompt Injection Detection** - Block hidden instructions

---

## Next Steps

1. **Share with your friend:**
   - GitHub repo: https://github.com/akshayagogulamudi/AgentSheild
   - Share SETUP.md for quick start

2. **Extend the system:**
   - Add real AI agents (e.g., Claude, GPT-4)
   - Integrate with production databases
   - Add user authentication
   - Deploy to cloud (AWS, GCP, Vercel)

3. **Customize:**
   - Modify security rules in `backend/security/`
   - Add new threat detection engines
   - Customize frontend pages in `frontend/src/routes/`

---

## Support

- **Backend Docs:** http://localhost:8000/docs (Swagger)
- **Backend Schemas:** http://localhost:8000/openapi.json
- **Frontend:** Check browser console for errors

---

## Demo Credentials

The app uses Supabase for auth (currently disabled in demo mode). All demo data is pre-seeded in SQLite.

**No login required** - Click "Launch the demo" on homepage.

---

Happy hacking! 🛡️
