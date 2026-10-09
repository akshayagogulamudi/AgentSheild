# AgentShield AI - Intelligent Security Gateway for AI Agents

**Protect autonomous AI agents from prompt injection, data exfiltration, and unauthorized tool usage.**

AgentShield is a comprehensive security platform that intercepts and evaluates tool calls from AI agents before execution. Using multi-layer threat detection, it prevents malicious agents (compromised or jailbroken) from damaging your systems or leaking sensitive data.

## Quick Start

### 1. Start Backend (60 seconds)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend API available at: `http://localhost:8000` | Docs: `http://localhost:8000/docs`

### 2. Start Frontend (30 seconds)

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: `http://localhost:5173`

---

## Features

### 🛡️ 8 Security Pages

1. **Overview** - Real-time metrics, attack summary, system status
2. **Playground** - Chat interface to interact with the agent
3. **Attack Simulation Lab** - Trigger 3 real attack scenarios
4. **Security Gateway** - View and analyze gateway decisions
5. **Threat Detection** - Timeline of detected threats
6. **Security Policies** - Role-based permissions matrix
7. **Activity Logs** - Audit trail of all actions
8. **Settings** - System configuration

### 🎯 3 Attack Scenarios Demonstrated

| Attack | Detection | Result |
|--------|-----------|--------|
| **Prompt Injection** | Injected override fields with malicious instructions | BLOCKED |
| **Data Exfiltration** | Email to external addresses containing API keys | BLOCKED |
| **Unauthorized Tools** | Tool calls not permitted by role policy | BLOCKED |

### 🔒 Multi-Layer Security Engines

1. **Policy Engine** - Role-based access control (RBAC)
2. **Prompt Injection Detector** - Regex + fuzzy matching
3. **DLP Engine** - Detects sensitive data (API keys, passwords, PII)
4. **Intent Validator** - Semantic alignment checking
5. **Risk Scorer** - Aggregates checks into risk assessment

### 📊 Dashboard & Analytics

- Real-time security event streaming
- Risk distribution charts
- Threat categorization
- Gateway decision statistics
- Attack pattern recognition

---

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: SQLite
- **Security**: Custom multi-engine gateway
- **API**: RESTful with OpenAPI (Swagger UI)

### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Build**: Vite
- **Icons**: Lucide React
- **HTTP**: Axios

---

## How to Demo

### Step 1: View Dashboard
1. Open http://localhost:5173
2. Explore Overview page - see real-time metrics
3. Check Playground - interact with the agent

### Step 2: Trigger Attacks
1. Go to "Attack Simulation Lab"
2. Select attack scenario:
   - ✓ Prompt Injection
   - ✓ Data Exfiltration
   - ✓ Unauthorized Tool
3. Click "Execute Attack"
4. See AgentShield BLOCK the attack
5. View details in Threat Detection

### Step 3: Explore Security Engine
1. Go to "Security Gateway"
2. View gateway decisions with reasoning
3. See risk scores and threat tier
4. Review security checks that fired
5. Understand why each decision was made

### Step 4: Check Policies
1. Go to "Security Policies"
2. View role permissions matrix
3. Understand policy constraints
4. See why certain tools are blocked

---

## API Examples

### Evaluate a Tool Call

```bash
curl -X POST http://localhost:8000/api/gateway/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "send_email",
    "arguments": {
      "to": "manager@company.com",
      "subject": "Report",
      "body": "Monthly report"
    },
    "agent_role": "employee",
    "user_request": "Send the monthly report"
  }'
```

**Response:**
```json
{
  "decision": "ALLOW",
  "risk_score": 15,
  "risk_tier": "LOW",
  "explanation": "✓ All security checks passed",
  "checks": [
    {"name": "tool_permission", "passed": true},
    {"name": "dlp_engine", "passed": true},
    {"name": "recipient_validation", "passed": true}
  ]
}
```

### Trigger Attack Scenario

```bash
curl -X POST "http://localhost:8000/api/agent/mock?scenario=prompt_injection" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "read handbook",
    "agent_role": "employee"
  }'
```

**Response:**
```json
{
  "response_text": "I'll look that up for you",
  "blocked_tools": ["read_file"],
  "gateway_decisions": [
    {
      "decision": "BLOCK",
      "risk_score": 95,
      "risk_tier": "CRITICAL",
      "explanation": "✗ Prompt injection detected with high confidence"
    }
  ]
}
```

### Get Security Events

```bash
curl http://localhost:8000/api/events?limit=10
```

---

## Project Structure

```
AgentShield/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── database/                  # DB models & initialization
│   ├── routes/                    # API endpoints
│   ├── security/                  # Security engines
│   │   ├── gateway.py             # Main orchestrator
│   │   ├── policy_engine.py       # RBAC
│   │   ├── injection_detector.py  # Prompt injection
│   │   ├── dlp_engine.py          # Data leakage prevention
│   │   ├── risk_engine.py         # Risk scoring
│   │   └── intent_validator.py    # Intent validation
│   ├── agent/                     # AI agent service
│   ├── tests/                     # 49 integration tests
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/                 # 8 feature pages
│   │   ├── components/            # Reusable UI components
│   │   └── utils/                 # API client
│   ├── package.json               # Node dependencies
│   └── tsconfig.json              # TypeScript config
├── docs/
│   ├── DEPLOYMENT.md              # Setup guide
│   ├── ARCHITECTURE.md            # System design
│   └── ATTACKS.md                 # Attack analysis
└── README.md                       # This file
```

---

## Running Tests

### Backend Tests (49 tests, all passing ✓)

```bash
cd backend
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_integration.py -v

# Run with coverage
python -m pytest tests/ --cov=.
```

### Integration Tests Include
- ✓ Prompt injection attack detection
- ✓ Data exfiltration blocking
- ✓ Unauthorized tool rejection
- ✓ Security event recording
- ✓ Approval workflow
- ✓ Health check endpoints

---

## Configuration

### Backend Environment (.env)

```bash
# Optional: Live AI agent (requires Gemini API key)
GEMINI_API_KEY=your_api_key_here

# Database (default: SQLite)
DATABASE_URL=sqlite:///agentshield.db
```

Leave `GEMINI_API_KEY` empty to use mock agent mode.

### Frontend Configuration

Available in Settings page at runtime.

---

## Security Features Explained

### Policy Engine
- Enforces role-based access control
- 3 demo roles: employee, manager, admin
- Each role has defined tool permissions
- Blocks any tool not in role's allow list

### Prompt Injection Detector
- 40+ regex patterns for injection keywords
- Fuzzy matching for variations
- Scans tool arguments for malicious overrides
- Calculates confidence score (0-1)

### DLP Engine
- Detects API keys, passwords, credentials
- Scans for PII (SSN, credit cards)
- Identifies confidential document markers
- 3 severity levels: LOW/MEDIUM/HIGH

### Intent Validator
- Semantic alignment of user request vs agent action
- Flags misaligned operations
- Prevents goal divergence attacks

### Risk Scorer
- Aggregates all checks into risk score (0-100)
- 4 risk tiers: LOW/MEDIUM/HIGH/CRITICAL
- Makes final decision: ALLOW/REQUIRE_APPROVAL/BLOCK

---

## Architecture Highlights

```
Request Flow:
User → Frontend → Backend API → Security Gateway
                      ↓
                (Multi-layer checks)
                      ↓
                 Decision + Events
                      ↓
              Database + Frontend Update
```

**Gateway Evaluation** (< 50ms):
1. Tool Permission Check (hard block)
2. Intent Validation Check
3. Prompt Injection Detection
4. DLP Scanning
5. Resource Authorization
6. Argument Validation
7. Risk Scoring & Decision
8. Event Logging

---

## Production Deployment

### Backend
```bash
# Production ASGI server
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### Frontend Build
```bash
cd frontend
npm run build
# Deploy dist/ to CDN or static host
```

### Database
- Use PostgreSQL for production (more reliable than SQLite)
- Enable backups
- Monitor database size

### Monitoring
- Track gateway latency
- Monitor BLOCK vs ALLOW ratio
- Alert on CRITICAL risk threats
- Audit policy changes

---

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Verify dependencies
pip install -r requirements.txt

# Check port availability
netstat -an | grep 8000
```

### Frontend build errors
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Database errors
```bash
# Reset database
rm backend/agentshield.db
# Restart backend - it will recreate and seed
```

---

## Documentation

- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Complete setup & deployment guide
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design & components
- **[ATTACKS.md](docs/ATTACKS.md)** - Attack scenarios explained
- **API Docs**: http://localhost:8000/docs (Interactive Swagger UI)

---

## Performance Metrics

| Component | Latency | Notes |
|-----------|---------|-------|
| Policy lookup | 2-5ms | Cached |
| Injection detector | 5-10ms | Pattern matching |
| DLP scanner | 10-20ms | Regex patterns |
| Total gateway | < 50ms | All checks |
| Frontend build | < 2s | Vite optimized |

---

## Security Best Practices

1. **Review policies quarterly** - Ensure permissions are minimal
2. **Monitor gateway events** - Set up alerts for CRITICAL threats
3. **Run tests regularly** - Validate attack prevention works
4. **Keep dependencies updated** - Regular security patches
5. **Enable HTTPS** - Use reverse proxy with SSL in production
6. **Implement auth** - Add authentication middleware
7. **Audit logs** - Regular review of security events

---

## Contributing

This is a demonstration project for the AI Hackathon. Feel free to:
- Fork and experiment
- Add new detection engines
- Create custom policies
- Extend to other AI platforms

---

## Demo Video Flow

1. **30 seconds**: Show Overview dashboard
2. **1 min**: Send normal message in Playground
3. **2 min**: Trigger 3 attack scenarios
4. **1 min**: Show threats in Threat Detection
5. **1 min**: Explain architecture
6. **Total**: 5-6 minutes

---

## License

AgentShield is provided as-is for demonstration purposes.

---

## Support

For questions or issues:
1. Check documentation in `/docs`
2. Review API docs at `http://localhost:8000/docs`
3. Check console output for error messages
4. Review test cases in `backend/tests/`

---

**Ready to see AI security in action?**

```bash
# Start the demo in 2 commands:
cd backend && uvicorn main:app --reload &
cd frontend && npm run dev
```

Then open http://localhost:5173 and explore!

🛡️ **AgentShield - Keeping AI Agents Secure** 🛡️
