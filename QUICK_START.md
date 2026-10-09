# 🚀 AgentShield AI - Quick Start (30 seconds)

## Step 1: Backend
```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
✅ Backend ready at: **http://localhost:8000**

## Step 2: Frontend
```powershell
cd frontend
npm install
npm run dev
```
✅ Frontend ready at: **http://localhost:8080** or **http://localhost:5173**

---

## That's It! 🎉

Click the **"Launch the demo"** button on the homepage to start exploring.

### What You'll See:
- **Dashboard** → Security metrics & threat overview
- **Audit Logs** → Every agent action logged with decisions
- **Attack Lab** → Test security rules safely
- **Email Inspector** → Detect prompt injection attempts

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Port 8000 busy | `python -m uvicorn main:app --reload --port 8001` |
| Port 8080 busy | npm will auto-select next available port |
| Backend won't start | Check: `python -m pip install -r requirements.txt` |
| Frontend blank | Check browser console, ensure `VITE_API_BASE` is set |
| Can't connect | Both services running? Check `http://localhost:8000/docs` |

---

## API Endpoints

```
GET  /api/events           → Audit logs
GET  /api/threats          → Detected threats
GET  /api/policies         → Security policies
POST /api/agent/message    → Evaluate agent message
GET  /api/gateway/evaluate → Gateway status
```

---

## Project Structure

```
AgentShield/
├── backend/              # FastAPI + 10+ security engines
├── frontend/             # React + TanStack + Radix UI
├── SETUP.md             # Full documentation
└── QUICK_START.md       # This file
```

---

## Tech Stack

🔙 **Backend:** FastAPI, SQLite, Pydantic  
🎨 **Frontend:** React 19, TanStack Router, Tailwind CSS, Recharts  

---

## Demo Data Included

✅ 3 AI agents (InboxAssistant, DevOpsAgent, FinanceBot)  
✅ 15+ sample emails with security issues  
✅ 50+ audit log entries  
✅ 10+ security policies  

No setup needed - everything auto-seeded!

---

## Next: Share with Your Friend

Send them:
1. GitHub repo: https://github.com/akshayagogulamudi/AgentSheild
2. This file: `QUICK_START.md`
3. Full docs: `SETUP.md`

---

**Questions?** Check the browser console or backend logs at `http://localhost:8000/docs`

Happy hacking! 🛡️
