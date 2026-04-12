import anthropic
import json
import csv
import sqlite3
import sys
from datetime import datetime


client = anthropic.Anthropic()


# Ideal Customer Profile - this is what we score leaads against
ICP = {
    "target_industries": ["E-commerce", "SaaS", "MarTech"],
    "min_company_size": 50,
    "preferred_tech": ["Shopify", "Shopify Plus", "Salesforce", "HubSpot"],
    "preferred_roles": ["VP of Sales", "Head of Marketing", "Director of Operations", "VP of Revenue"],
    "preferred_funding": ["Series A", "Series B", "Series C"],

}

def load_leads(filename):
    leads = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(row)
    print(f"Loaded {len(leads)} leads from {filename}")
    return leads

def load_company_data(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    print(f"Loaded data for {len(data)} companies")
    return data

def setup_database():
    db = sqlite3.connect('leads.db')
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enriched_leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        company TEXT,
        role TEXT,
        industry TEXT,
        source TEXT,
        company_size INTEGER,
        tech_stack TEXT,
        revenue TEXT,
        funding TEXT,
        icp_score INTEGER,
        score_reasoning TEXT,
        outreach_email TEXT,
        processed_at TEXT
    )
    """)
    db.commit()
    return db   


def score_lead(lead, company_info):
    prompt = f"""Score this lead against our Ideal Customer Profile (ICP) and explain your reasoning.


LEAD:
Name: {lead['name']}
Role: {lead['role']}
Company: {lead['company']}
Source: {lead['source']}

COMPANY DATA:
Industry: {company_info.get('industry', 'Unknown')}
Size: {company_info.get('size', 'Unknown')}
Revenues: {company_info.get('revenues', 'Unknown')}
Tech Stack: {', '.join(company_info.get('tech_stack', []))}
Funding: {company_info.get('funding', 'Unknown')}

IDEAL CUSTOMER PROFILE:
Target Industries: {', '.join(ICP['target_industries'])}
Minimum Company Size: {ICP['min_company_size']} employees
Preferred Tech: {', '.join(ICP['preferred_tech'])}
Preferred Roles: {', '.join(ICP['preferred_roles'])}
Preferred Funding: {', '.join(ICP['preferred_funding'])}

Respond with ONLY valid JSON:
{{"Score": <0-100>, "reasoning": "<2-3 sentences explaining the sccore>"}}"""
    

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            temperature=0,
            system="You are a lead scoring expert. score leads against the ICP. Respond with ONLY valid JSON, no other text.",
            messages=[{"role": "user", "content": prompt}]
        )
        result = json.loads(response.content[0].text)
        return result['Score'], result['reasoning']
    except Exception as e:
        return 0, f"Sccoring error: {e}"
    
def generate_outreach(lead, company_info, score_reasoning):
    prompt = f"""Write a short, personalized outreach email for this lead.


LEAD:
Name: {lead['name']}
Role: {lead['role']}
Company: {lead['company']}


COMPANY DATA:
Industry: {company_info.get('industry', 'Unknown')}
Tech Stack: {', '.join(company_info.get('tech_stack', []))}


CONTEXT: {score_reasoning}

Rules:
1. Keep it under 100 words
2. Reference their specificc tech stack or industry
3. Focus on a pain point relevant to their role
4. Inccclude a clear call to action
5. Professional but conversational tone
6. Do not use generic phrases like "I hope this find you well" or "I wanted to reach out"

Respond with ONLY the email body text, nothing else."""
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            temperature=0.7,
            system="You are an expert SDR who writes highly personalized outreach emails. Write only email body.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"Email generation error: {e}"
    

def run_pipeline(leads_file="leads.csv", ccompany_file="company_data.json"):
    print("=" * 60)
    print("GTM LEAD ENRICHMENT PIPELINE")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    #load data
    leads = load_leads(leads_file)
    company_data = load_company_data(ccompany_file)
    db = setup_database()
    cursor = db.cursor()

    #track Stats
    total_tokens_in = 0
    total_tokens_out = 0
    results = []


    for i, lead in enumerate(leads):
        print(f"\n[{i+1}/{len(leads)}] Processing: {lead['name']} from {lead['company']}")

        # step 1: Enrich with company data
        company_info = company_data.get(lead['company'], {})
        if company_info:
            print(f" Enriched: {company_info.get('industry')} | {company_info.get('size')} employees | {company_info.get('funding')}")
        else:
            print(f" WARNING: No company data found for {lead['company']}")
            company_info = {}


        # step 2: Score lead with AI
        score, reasoning = score_lead(lead, company_info)
        print(f" ICP Score: {score}/100")
        print(f" Reasoning: {reasoning[:100]}...")

        #step 3: Generate outreach email (only for leads scoring 50+)
        if score >= 50:
            email = generate_outreach(lead, company_info, reasoning)
            print(f" Outreach: Generated ({len(email.split())} words")
        else:
            email = "Score too low for outreach"
            print(f" Outreach: Skipped (score below threshold)")


        # Step 4: Save to database
        cursor.execute("""
        INSERT INTO enriched_leads
        (name, email, company, role, industry, source, company_size, tech_stack, revenue, funding, icp_score, score_reasoning, outreach_email, processed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lead['name'],
            lead['email'],
            lead['company'],
            lead['role'],
            company_info.get('industry', 'Unknown'),
            lead['source'],
            company_info.get('size', 'Unknown'),
            ', '.join(company_info.get('tech_stack', [])),
            company_info.get('revenue', 'Unknown'),
            company_info.get('funding', 'Unknown'),
            score,
            reasoning,
            email,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        db.commit()

        results.append({
            "name": lead['name'],
            "company": lead['company'],
            "score": score,
            "reasoning": reasoning,
        })

    # summary
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Leads processed: {len(results)}")

    scored = sorted(results, key=lambda x: x['score'], reverse=True)
    print(f"\nLead Rankings:")
    for r in scored:
        status = "HOT" if r['score'] >= 75 else "WARM" if r['score'] >= 50 else "COLD"
        print(f" [{status}] {r['name']} {r['company']} {r['score']}/100)")
            
    hot = sum(1 for r in results if r['score'] >= 75)
    warm = sum(1 for r in results if 50 <= r['score'] < 75)
    cold = sum(1 for r in results if r['score'] < 50)
    print(f"\nBreakdown: {hot} hot | {warm} warm | {cold} cold")

    # Save ressults to JSON
    with open("pipeline_results.json", 'w') as f:
        json.dump({
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_leads": len(results),
            "results": scored
        }, f, indent=2)
    print("\nResults saved to pipeline_results.json")
    print(f"Database saved to leads.db")

    db.close()


if __name__ == "__main__":
    leads_file = sys.argv[1] if len(sys.argv) > 1 else "leads.csv"
    company_file = sys.argv[2] if len(sys.argv) > 2 else "company_data.json"
    run_pipeline(leads_file, company_file)