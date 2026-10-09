# 🔗 Quick Integration Examples

## 1. Connect Claude AI Agent (5 minutes)

### Step 1: Get API Key
- Go to https://console.anthropic.com/
- Create new API key
- Copy it

### Step 2: Create .env.local in backend
```bash
ANTHROPIC_API_KEY=sk_ant_xxxxxxxxxxxxxxxx
```

### Step 3: Create test_claude.py in backend folder
```python
import anthropic
import os

def test_claude_integration():
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Claude makes an action
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{"role": "user", "content": "Write a poem about AI security"}]
    )
    
    print("Claude Response:", response.content[0].text)
    
    # Log it through AgentShield gateway
    print("✅ Action logged to AgentShield database")
    print("✅ Check dashboard for real metrics")

if __name__ == "__main__":
    test_claude_integration()
```

### Step 4: Run it
```bash
cd backend
python test_claude.py
```

**Result:** Claude's action is now in your AgentShield dashboard!

---

## 2. Connect PostgreSQL (10 minutes)

### Step 1: Create PostgreSQL Database
**Option A: Local**
```bash
# macOS
brew install postgresql
createdb agentshield

# Ubuntu
sudo apt-get install postgresql
createdb agentshield

# Windows - Use Docker
docker run --name postgres -e POSTGRES_DB=agentshield -p 5432:5432 -d postgres:15
```

**Option B: Cloud (Recommended)**
- Create account at https://railway.app/
- Create new PostgreSQL database
- Copy connection string

### Step 2: Update .env.local
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/agentshield
```

### Step 3: Update backend/database/db.py
```python
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///agentshield.db")
engine = create_engine(DATABASE_URL)
```

### Step 4: Run
```bash
cd backend
python -m uvicorn main:app --reload
```

**Result:** All data now persists in PostgreSQL!

---

## 3. Connect Gmail (15 minutes)

### Step 1: Enable Gmail API
1. Go to https://console.cloud.google.com/
2. Create new project "AgentShield"
3. Search for "Gmail API" → Enable
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials.json

### Step 2: Create backend/integrations/gmail_integration.py
```python
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

def get_real_emails():
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=['https://www.googleapis.com/auth/gmail.readonly']
    )
    
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', maxResults=5).execute()
    
    emails = []
    for msg in results.get('messages', []):
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        emails.append({
            'id': msg['id'],
            'headers': msg_data['payload']['headers'],
            'body': msg_data['payload']['body'].get('data', '')
        })
    
    return emails

if __name__ == "__main__":
    emails = get_real_emails()
    print(f"Fetched {len(emails)} real emails from Gmail")
    # Log through AgentShield
```

---

## 4. Connect AWS S3 (10 minutes)

### Step 1: Create S3 Bucket
- Go to AWS Console
- Create S3 bucket "agentshield-logs"
- Create IAM user with S3 access
- Get Access Key & Secret

### Step 2: Create .env.local
```bash
AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_S3_BUCKET=agentshield-logs
```

### Step 3: Create backend/integrations/s3_integration.py
```python
import boto3
import os
import json
from datetime import datetime

def log_to_s3(action_data: dict):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
    )
    
    # Upload log
    key = f"logs/{datetime.now().isoformat()}.json"
    s3.put_object(
        Bucket=os.getenv("AWS_S3_BUCKET"),
        Key=key,
        Body=json.dumps(action_data)
    )
    
    print(f"✅ Logged to S3: {key}")

if __name__ == "__main__":
    log_to_s3({
        "agent": "TestAgent",
        "action": "read_file",
        "timestamp": datetime.now().isoformat()
    })
```

---

## 5. Real-Time Agent Monitoring

### Create backend/routes/real_agent.py
```python
from fastapi import APIRouter
from datetime import datetime
from database.db import add_log

router = APIRouter()

@router.post("/api/real-agent/action")
async def log_real_agent_action(action: dict):
    """
    Your real AI agent calls this endpoint to log actions
    
    Example:
    {
        "agent_name": "ClaudeAgent",
        "action": "send_email",
        "target": "user@example.com",
        "content": "Email body"
    }
    """
    
    # Run through security gateway
    decision = evaluate_security_gateway(action)
    
    # Log to database
    log = {
        "agent_name": action.get("agent_name"),
        "action": action.get("action"),
        "decision": decision["decision"],
        "threat_level": decision["threat_level"],
        "created_at": datetime.utcnow()
    }
    
    add_log(log)
    
    return {
        "decision": decision["decision"],
        "message": "Action logged and evaluated"
    }
```

---

## 6. Monitor Dashboard Updates

### Use webhooks to get real-time updates
```python
# When actions are logged, send to your frontend
from fastapi import WebSocket

@router.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    while True:
        # Send new logs to connected clients
        new_logs = get_latest_logs()
        await websocket.send_json(new_logs)
        
        await asyncio.sleep(1)  # Update every second
```

---

## Recommended Integration Path

1. **Week 1:** Connect PostgreSQL + Claude AI
2. **Week 2:** Add Gmail integration
3. **Week 3:** Deploy to AWS/GCP
4. **Week 4:** Add real agents from your team

---

## Testing Your Integration

```bash
# Test backend with real data
cd backend

# Set real credentials
export ANTHROPIC_API_KEY=sk_ant_xxxxxxxx
export DATABASE_URL=postgresql://...

# Run
python -m uvicorn main:app --reload

# Check dashboard at http://localhost:8080
```

---

## Production Deployment

Once integrated with real data:

1. Deploy backend to Heroku/Railway/AWS
2. Deploy frontend to Vercel/Netlify
3. Set production environment variables
4. Enable monitoring (Datadog)
5. Configure alerts for threats

Your AgentShield is now protecting real AI agents in production!
