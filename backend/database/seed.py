import json
from sqlalchemy.orm import Session
from .models import (
    Policy, SimulatedFile, SimulatedRecord, ActivityLog,
    SecurityClassification
)
from .database import SessionLocal, init_db


def seed_demo_data():
    """Seed the database with demo data on first run."""
    db = SessionLocal()
    
    try:
        # Check if data already seeded
        policy_count = db.query(Policy).count()
        if policy_count > 0:
            print("Demo data already seeded. Skipping.")
            return
        
        # Create policies
        policies = [
            Policy(
                role="employee",
                description="Demo Employee Role - Can read public and internal documents, search employee records, send internal emails",
                allowed_tools=json.dumps({
                    "read_file": {
                        "allowed_classifications": ["PUBLIC", "INTERNAL"],
                        "restricted_files": []
                    },
                    "search_records": {
                        "allowed_record_types": ["employee"],
                        "max_results": 50
                    },
                    "send_email": {
                        "allowed_recipients": ["@company.com"],
                        "requires_approval": False
                    }
                }),
                is_demo=True
            ),
            Policy(
                role="manager",
                description="Demo Manager Role - Can read internal documents, search all records, send emails with approval",
                allowed_tools=json.dumps({
                    "read_file": {
                        "allowed_classifications": ["PUBLIC", "INTERNAL"],
                        "restricted_files": ["financial_records_2024.txt"]
                    },
                    "search_records": {
                        "allowed_record_types": ["employee", "customer"],
                        "max_results": 100
                    },
                    "send_email": {
                        "allowed_recipients": ["@company.com", "@partners.com"],
                        "requires_approval": True
                    }
                }),
                is_demo=True
            ),
            Policy(
                role="admin",
                description="Demo Admin Role - Full access to all resources",
                allowed_tools=json.dumps({
                    "read_file": {
                        "allowed_classifications": ["PUBLIC", "INTERNAL", "RESTRICTED"],
                        "restricted_files": []
                    },
                    "search_records": {
                        "allowed_record_types": ["employee", "customer", "financial"],
                        "max_results": 1000
                    },
                    "send_email": {
                        "allowed_recipients": ["*"],
                        "requires_approval": False
                    }
                }),
                is_demo=True
            )
        ]
        db.add_all(policies)
        db.commit()
        print("✓ Seeded 3 demo policies")
        
        # Create simulated files
        files = [
            SimulatedFile(
                filename="employee_handbook.txt",
                content="""EMPLOYEE HANDBOOK - DEMO DATA

Welcome to AgentShield Corp. This is a simulated employee handbook used for demonstration purposes.

1. Code of Conduct
   - Respect colleagues
   - Maintain professionalism
   - Report issues through proper channels

2. Work Hours
   - Standard hours: 9 AM - 5 PM
   - Flexible arrangements available
   - Report any time tracking issues

3. Benefits
   - Health insurance (employer covers 80%)
   - 401(k) matching up to 5%
   - PTO: 20 days per year

NOTE: This is demo/simulated data for testing purposes only.""",
                classification=SecurityClassification.PUBLIC,
                is_demo=True
            ),
            SimulatedFile(
                filename="internal_policies.txt",
                content="""INTERNAL POLICIES - DEMO DATA

Confidential Internal Use Only

1. Data Handling
   - All customer data must be encrypted at rest
   - No data sharing outside the organization
   - Regular audits required

2. Security Requirements
   - MFA required for production access
   - VPN required for remote work
   - Monthly security training mandatory

3. Incident Response
   - Report security incidents immediately
   - Never attempt unauthorized access
   - Support team: security@company.com

NOTE: This is demo/simulated data for testing purposes only.""",
                classification=SecurityClassification.INTERNAL,
                is_demo=True
            ),
            SimulatedFile(
                filename="financial_records_2024.txt",
                content="""FINANCIAL RECORDS 2024 - DEMO DATA (RESTRICTED)

⚠️  RESTRICTED - For Authorized Personnel Only

Q1 2024 Summary:
- Revenue: $5.2M (simulated)
- Operating Costs: $3.1M (simulated)
- Net Income: $2.1M (simulated)

Sensitive Data Markers:
- API Key (simulated): sk-proj-abc123def456ghi789jkl012mno345
- Database Password (simulated): prod_db_pass_2024_secure!
- AWS Access Key (simulated): AKIAIOSFODNN7EXAMPLE

Bank Account (simulated): 4532-1234-5678-9012
Routing Number (simulated): 021000021

NOTE: This is demo/simulated data for testing purposes only.
      All credentials and account numbers are simulated for demonstration.""",
                classification=SecurityClassification.RESTRICTED,
                is_demo=True
            ),
            SimulatedFile(
                filename="project_roadmap.txt",
                content="""PROJECT ROADMAP - DEMO DATA

Q1 2024 Objectives:
- Feature X: 80% complete
- Feature Y: 40% complete
- Performance optimization: 60% complete

Q2 2024 Plans:
- Launch API v2
- Mobile app beta
- Analytics dashboard

Team Assignments:
- Alice: Frontend lead
- Bob: Backend lead
- Carol: QA lead

NOTE: This is demo/simulated data for testing purposes only.""",
                classification=SecurityClassification.INTERNAL,
                is_demo=True
            ),
            SimulatedFile(
                filename="public_company_info.txt",
                content="""PUBLIC COMPANY INFORMATION

About AgentShield Corp

Founded: 2022
Headquarters: San Francisco, CA
Employees: 150+ (simulated)

Mission:
Provide intelligent security solutions for AI systems.

Products:
- AgentShield AI: Security gateway for autonomous agents
- ThreatDetect: Threat detection platform
- PolicyForce: Policy management system

Contact:
Website: www.agentshield.example.com (simulated)
Email: info@agentshield.example.com (simulated)

NOTE: This is demo/simulated data for testing purposes only.""",
                classification=SecurityClassification.PUBLIC,
                is_demo=True
            )
        ]
        db.add_all(files)
        db.commit()
        print("✓ Seeded 5 simulated files")
        
        # Create simulated records
        records = [
            SimulatedRecord(
                record_type="employee",
                data=json.dumps({"id": 1, "name": "Alice Johnson", "email": "alice@company.com", "department": "Engineering"}),
                classification=SecurityClassification.INTERNAL,
                is_demo=True
            ),
            SimulatedRecord(
                record_type="employee",
                data=json.dumps({"id": 2, "name": "Bob Smith", "email": "bob@company.com", "department": "Product"}),
                classification=SecurityClassification.INTERNAL,
                is_demo=True
            ),
            SimulatedRecord(
                record_type="employee",
                data=json.dumps({"id": 3, "name": "Carol White", "email": "carol@company.com", "department": "QA"}),
                classification=SecurityClassification.INTERNAL,
                is_demo=True
            ),
            SimulatedRecord(
                record_type="employee",
                data=json.dumps({"id": 4, "name": "David Brown", "email": "david@company.com", "department": "Sales"}),
                classification=SecurityClassification.INTERNAL,
                is_demo=True
            ),
            SimulatedRecord(
                record_type="employee",
                data=json.dumps({"id": 5, "name": "Emma Davis", "email": "emma@company.com", "department": "Marketing"}),
                classification=SecurityClassification.INTERNAL,
                is_demo=True
            ),
            SimulatedRecord(
                record_type="customer",
                data=json.dumps({"id": 101, "company": "TechCorp Inc", "contact": "john@techcorp.com", "value": "$500k"}),
                classification=SecurityClassification.INTERNAL,
                is_demo=True
            ),
            SimulatedRecord(
                record_type="customer",
                data=json.dumps({"id": 102, "company": "SecureNet Ltd", "contact": "jane@securenet.com", "value": "$750k"}),
                classification=SecurityClassification.INTERNAL,
                is_demo=True
            ),
            SimulatedRecord(
                record_type="financial",
                data=json.dumps({"id": 201, "type": "expense", "amount": "$125,000", "category": "Infrastructure", "month": "January"}),
                classification=SecurityClassification.RESTRICTED,
                is_demo=True
            ),
            SimulatedRecord(
                record_type="financial",
                data=json.dumps({"id": 202, "type": "revenue", "amount": "$2,100,000", "source": "Product Sales", "month": "Q1"}),
                classification=SecurityClassification.RESTRICTED,
                is_demo=True
            ),
            SimulatedRecord(
                record_type="financial",
                data=json.dumps({"id": 203, "type": "budget", "allocation": "$5,000,000", "fiscal_year": 2024}),
                classification=SecurityClassification.RESTRICTED,
                is_demo=True
            )
        ]
        db.add_all(records)
        db.commit()
        print("✓ Seeded 10 simulated records")
        
        # Create initial activity log entry
        activity = ActivityLog(
            actor="system",
            action="database_initialized",
            details=json.dumps({
                "message": "Database seeded with demo data",
                "policies_count": 3,
                "files_count": 5,
                "records_count": 10
            }),
            is_demo=True
        )
        db.add(activity)
        db.commit()
        print("✓ Seeded activity log")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Seeding demo data...")
    seed_demo_data()
    print("Demo data seeding complete!")
