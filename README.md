# ESG Assessment System — Net-Zero Alignment Diagnostic Platform

## Overview

This project is an AI-powered ESG (Environmental, Social, and Governance) assessment system inspired by Neuberger Berman's net-zero alignment methodology. It provides dynamic, visual assessments of a company's ESG performance and transition readiness.

## Key Features

- **AI-powered company search** — Finds and validates companies, supports fuzzy matching, and resolves similar company names.
- **Automated ESG data collection** — Collects ESG reports, emissions data, ESG ratings, and related news.
- **Six-dimension assessment engine** — Scores companies from 1 to 5 across long-term ambition, near- and medium-term targets, emissions performance, disclosure, decarbonization strategy, and capital allocation.
- **Greenwashing detection** — Identifies potential greenwashing signals and adjusts assessment scores accordingly.
- **Interactive dashboard** — Presents radar charts, alignment status labels, and detailed strengths and weaknesses.
- **Transparent data sources** — Shows the AI search process and the sources used during an assessment.
- **Actionable recommendations** — Highlights transition risks and suggests practical improvement pathways.
- **Report export** — Exports PDF and Excel reports and supports peer benchmarking.

## Technology Stack

- **Backend:** Python and Flask
- **Frontend:** HTML5, CSS3, and JavaScript
- **Charts:** ECharts
- **AI providers:** DeepSeek API, OpenAI API, or Anthropic Claude API

## Project Structure

```text
ESG_Dashboard/
├── app.py                    # Flask application entry point
├── config.py                 # Application configuration
├── ai_search_engine.py       # AI search engine
├── data_collector.py         # ESG data collection
├── evaluation_engine.py      # ESG evaluation engine
├── report_generator.py       # PDF and Excel report generation
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── README.md
├── static/
│   ├── css/
│   │   └── style.css         # Application styles
│   └── js/
│       ├── main.js           # Main frontend logic
│       ├── chart.js          # Chart configuration
│       └── api.js            # API requests
├── templates/
│   └── index.html            # Main page template
├── data/                     # Sample and runtime data
├── reports/                  # Generated reports (not committed)
├── docs/                     # Project documentation
├── 启动ESG系统.bat           # Windows startup script
└── 一键启动.bat              # Windows one-click startup script
```

## Quick Start

### 1. Create and activate a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure an AI provider

Copy the environment template:

```bash
cp .env.example .env
```

On Windows Command Prompt, use:

```bat
copy .env.example .env
```

Open `.env` and add at least one API key. DeepSeek is the primary provider used by the search engine:

```dotenv
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-chat
```

Optional fallback providers can also be configured:

```dotenv
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

Never commit your real `.env` file or API keys.

### 4. Start the application

From the command line:

```bash
python app.py
```

Windows users can alternatively run either startup script:

```bat
一键启动.bat
```

Open [http://localhost:5000](http://localhost:5000) in a browser.

## How the AI Features Work

### Company Search

- Enter a company name; fuzzy matching is supported.
- The AI validates whether the company exists.
- If several similar companies are found, the system asks the user to choose one.
- If no company is found, the user is prompted to enter another name.

### Assessment Process

The interface displays live progress while the system searches for:

- Company information
- ESG and sustainability reports
- Carbon emissions data
- ESG ratings
- Relevant news and controversies

### Data Sources

The results page lists the sources used by the AI, including ESG reports, news articles, and rating agencies. Available source links can be opened directly for verification.

## Assessment Dimensions

| Dimension | What It Evaluates |
| --- | --- |
| Long-term ambition | Net-zero commitments and alignment with a 1.5°C pathway |
| Near- and medium-term targets | Interim targets and Scope 1, 2, and 3 coverage |
| Emissions performance | Historical emissions trajectory and reduction performance |
| Disclosure | Transparency and alignment with major reporting standards |
| Decarbonization strategy | Credibility and feasibility of the transition plan |
| Capital allocation | Green capital expenditure, investment, and revenue exposure |

## Development Team

| Team | Responsibility | Members |
| --- | --- | ---: |
| Task Force A | Data and AI backend | 2 |
| Task Force B | Frontend and visualization | 2 |
| Task Force C | System integration and agile management | 3 |

## Security Notes

- Keep API keys in `.env`; the file is excluded by `.gitignore`.
- Do not commit virtual environments, generated reports, caches, or evaluation history.
- Review AI-generated findings and their cited sources before using them for investment or compliance decisions.

## License

This project is licensed under the MIT License.
