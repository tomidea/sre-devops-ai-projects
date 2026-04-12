# GTM Lead Enrichment Pipeline

An end-to-end AI-powered pipeline that takes raw leads, enriches them with company data, scores them against an Ideal Customer Profile using Claude, and generates personalized outreach emails for high-scoring leads.

## How It Works

leads.csv (raw leads)
|
[Load & Enrich] — Match leads with company data (industry, size, tech stack, funding)
|
[AI Scoring] — Claude scores each lead 1-100 against your ICP with reasoning
|
[Smart Filtering] — Only leads scoring 50+ get outreach emails
|
[AI Outreach] — Claude generates personalized emails referencing tech stack and pain points
|
[Store Results] — SQLite database + JSON report with full pipeline results

## Key Features

- **ICP-based scoring** — Configurable Ideal Customer Profile with target industries, company size, tech stack, roles, and funding stage
- **AI-powered scoring with reasoning** — Claude explains WHY each lead scored the way it did
- **Personalized outreach generation** — Emails reference specific tech stack, industry pain points, and role-relevant challenges
- **Smart filtering** — Only generates outreach for leads above score threshold, saving API costs
- **Full data pipeline** — CSV input, enrichment, AI processing, SQLite storage, JSON reporting
- **Pipeline summary** — Hot/warm/cold breakdown with ranked lead list

## Tech Stack

- **Python 3** — Core pipeline
- **Anthropic SDK** — Claude API for lead scoring and email generation
- **SQLite** — Persistent storage for enriched lead data
- **CSV** — Standard lead import format
- **JSON** — Company data enrichment and pipeline results

## Setup

```bash
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"
```

## Usage

```bash
# Run with default sample data
python3 pipeline.py

# Run with your own leads file
python3 pipeline.py your_leads.csv
```

## Input Format

### leads.csv
| Column | Description |
|--------|-------------|
| name | Contact name |
| email | Contact email |
| company | Company name |
| role | Job title |
| source | Lead source (LinkedIn, Website, Referral, etc.) |

### company_data.json
Company enrichment data keyed by company name with industry, size, revenue, tech_stack, and funding fields.

## ICP Configuration

Edit the ICP dictionary in pipeline.py to match your target customer:

```python
ICP = {
    "target_industries": ["E-commerce", "SaaS", "MarTech"],
    "min_company_size": 50,
    "preferred_tech": ["Shopify", "Salesforce", "HubSpot"],
    "preferred_roles": ["VP of Sales", "Head of Marketing"],
    "preferred_funding": ["Series A", "Series B", "Series C"]
}
```

## Prompt Engineering

- **Scoring prompt** — Includes full lead data, company data, and ICP criteria. Temperature=0 for consistent scoring. Returns structured JSON with score and reasoning.
- **Outreach prompt** — Temperature=0.7 for creative but professional emails. Rules enforce personalization, brevity, and clear CTAs. References specific tech stack and role-relevant pain points.

## Example Output

Lead Rankings:
[HOT]  Emma Davis (ShopScale): 95/100
[HOT]  Sarah Chen (TechFlow): 85/100
[HOT]  Lisa Park (RetailPro): 75/100
[WARM] Mike Okafor (GrowthStack): 65/100
[COLD] James Wilson (QuickLaunch): 25/100
Breakdown: 4 hot | 1 warm | 1 cold

