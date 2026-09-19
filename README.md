<p align="center">
  <img src="assets/banner.jpg" alt="MCP Naukri Banner" width="100%"/>
</p>

<h1 align="center">🚀 MCP Naukri</h1>

<p align="center">
  <strong>AI-Powered Job Search & Code Intelligence — via the Model Context Protocol</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/protocol-MCP-blueviolet?logo=data:image/svg+xml;base64,..." alt="MCP"/>
  <img src="https://img.shields.io/badge/Apify-Actor-green?logo=apify" alt="Apify"/>
  <img src="https://img.shields.io/badge/OpenAI-GPT--4o-orange?logo=openai" alt="OpenAI"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License"/>
</p>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#%EF%B8%8F-configuration)
- [Usage Guide](#-usage-guide)
  - [Naukri Job Search MCP](#-naukri-job-search-mcp-claude_mcppy)
  - [Codex Code Intelligence MCP](#-codex-code-intelligence-mcp-codex_mcppy)
- [API Reference](#-api-reference)
- [Supported Cities](#-supported-cities)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**MCP Naukri** is a suite of two **Model Context Protocol (MCP)** servers that supercharge AI assistants like **Claude Desktop**, **Cursor**, and other MCP-compatible clients with:

| Server | Purpose |
|---|---|
| **`claude_mcp.py`** | Search & inspect job postings on **Naukri.com** using the Apify scraper actor |
| **`codex_mcp.py`** | Generate, refactor, and review code using **OpenAI GPT-4o / o3-mini** models |

> 💡 **What is MCP?** The [Model Context Protocol](https://modelcontextprotocol.io/) is an open standard that lets AI models call external tools, access resources, and interact with APIs — turning them from passive chatbots into **action-capable agents**.

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Client (AI Host)                       │
│           Claude Desktop  /  Cursor  /  Custom App              │
└────────────────┬───────────────────────────┬────────────────────┘
                 │ stdio (JSON-RPC)          │ stdio (JSON-RPC)
                 ▼                           ▼
  ┌──────────────────────────┐  ┌──────────────────────────────┐
  │    claude_mcp.py         │  │      codex_mcp.py            │
  │  ┌────────────────────┐  │  │  ┌────────────────────────┐  │
  │  │ naukri_search_jobs  │  │  │  │ codex_generate_code    │  │
  │  │ naukri_get_details  │  │  │  │ codex_refactor_code    │  │
  │  └────────┬───────────┘  │  │  └────────────┬───────────┘  │
  │           │ HTTPS        │  │               │ HTTPS        │
  │           ▼              │  │               ▼              │
  │  ┌────────────────────┐  │  │  ┌────────────────────────┐  │
  │  │   Apify Cloud API  │  │  │  │   OpenAI API           │  │
  │  │   (Naukri Scraper) │  │  │  │   (GPT-4o / o3-mini)   │  │
  │  └────────────────────┘  │  │  └────────────────────────┘  │
  └──────────────────────────┘  └──────────────────────────────┘
```

### Data Flow

```
User Prompt ──► MCP Client ──► MCP Server ──► External API ──► Response
                  (Claude)       (stdio)       (Apify/OpenAI)
                    ▲                                │
                    └────────── Formatted Result ◄───┘
```

---

## ✨ Features

### 🔍 Naukri Job Search (`claude_mcp.py`)

- **Smart Job Search** — Search by keyword, location, experience, freshness & sort order
- **Detailed Job View** — Full job descriptions, skills, salary, company info & employee reviews
- **50+ City Support** — Pre-mapped Naukri city IDs for all major Indian cities
- **HTML Cleaning** — Raw HTML job descriptions auto-converted to clean readable text
- **Connection Pooling** — Reusable async HTTP client for optimal performance
- **Graceful Error Handling** — Actionable error messages for common API failures

### 💻 Codex Code Intelligence (`codex_mcp.py`)

- **Code Generation** — Generate production-ready code in any language from natural descriptions
- **Code Refactoring** — Optimize, fix bugs, add types, improve security in existing code
- **Multi-Model Support** — Choose between `gpt-4o`, `gpt-4o-mini`, and `o3-mini`
- **Language Agnostic** — Works with Python, TypeScript, Go, Rust, Java, and more

---

## 📋 Prerequisites

Before you begin, ensure you have:

| Requirement | Details |
|---|---|
| **Python** | Version **3.10** or higher |
| **pip** | Python package manager |
| **Apify Account** | [Sign up free](https://apify.com/) → Get your API token |
| **OpenAI Account** | [Get API key](https://platform.openai.com/api-keys) |
| **MCP Client** | Claude Desktop, Cursor, or any MCP-compatible client |

---

## 🛠 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/MCP-naukri.git
cd MCP-naukri
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Dependencies installed:**
> | Package | Purpose |
> |---|---|
> | `python-dotenv` | Load environment variables from `.env` |
> | `httpx` | Async HTTP client for Apify API calls |
> | `mcp` | Model Context Protocol server framework |
> | `pydantic` | Data validation and settings management |
> | `openai` | OpenAI Python SDK for GPT API access |

---

## ⚙️ Configuration

### 1. Create the `.env` File

Create a `.env` file in the project root:

```bash
touch .env
```

Add your API keys:

```env
# Required for Naukri Job Search (claude_mcp.py)
APIFY_API_TOKEN=your_apify_api_token_here

# Required for Code Intelligence (codex_mcp.py)
OPENAI_API_KEY=your_openai_api_key_here
```

> ⚠️ **Security:** Never commit your `.env` file. Add it to `.gitignore`:
> ```bash
> echo ".env" >> .gitignore
> ```

### 2. Getting Your API Keys

<details>
<summary><strong>🔑 Apify API Token</strong></summary>

1. Go to [apify.com](https://apify.com/) and create an account
2. Navigate to **Settings** → **Integrations** → **API Tokens**
3. Click **Create Token** and copy it
4. Paste into your `.env` as `APIFY_API_TOKEN`

</details>

<details>
<summary><strong>🔑 OpenAI API Key</strong></summary>

1. Go to [platform.openai.com](https://platform.openai.com/)
2. Navigate to **API Keys** → **Create new secret key**
3. Copy the key (it won't be shown again!)
4. Paste into your `.env` as `OPENAI_API_KEY`

</details>

### 3. Configure Your MCP Client

#### Claude Desktop

Edit your Claude Desktop config file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "naukri_mcp": {
      "command": "python",
      "args": ["/absolute/path/to/MCP-naukri/claude_mcp.py"],
      "env": {
        "APIFY_API_TOKEN": "your_apify_api_token_here"
      }
    },
    "codex_mcp": {
      "command": "python",
      "args": ["/absolute/path/to/MCP-naukri/codex_mcp.py"],
      "env": {
        "OPENAI_API_KEY": "your_openai_api_key_here"
      }
    }
  }
}
```

#### Cursor

Add to your Cursor MCP settings (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "naukri_mcp": {
      "command": "python",
      "args": ["/absolute/path/to/MCP-naukri/claude_mcp.py"]
    },
    "codex_mcp": {
      "command": "python",
      "args": ["/absolute/path/to/MCP-naukri/codex_mcp.py"]
    }
  }
}
```

> 📝 Replace `/absolute/path/to/MCP-naukri/` with the actual path on your system.

---

## 📘 Usage Guide

### 🔍 Naukri Job Search MCP (`claude_mcp.py`)

Once configured, ask your AI assistant naturally:

#### Search for Jobs

```
"Find me Python developer jobs in Bangalore posted in the last 7 days"
```

```
"Search for data scientist positions in Pune for freshers, sort by relevance"
```

```
"Show me 20 DevOps engineer jobs in Mumbai posted this week"
```

#### Get Job Details

```
"Get full details for Naukri job ID 220126040161"
```

```
"Show me the complete job description, salary, and required skills for job 220126040161"
```

#### Example: Search Flow

```
You:     "Find React developer jobs in Hyderabad, last 3 days, 2 years experience"

Claude:  [Calls naukri_search_jobs tool]
         → keyword: "React Developer"
         → location: "Hyderabad"
         → freshness_days: "3"
         → experience_years: 2
         → sort_by: "date"

Result:  Found 10 jobs for 'React Developer':

         **Senior React Developer** at TCS
           Location   : Hyderabad
           Experience : 2-5 Yrs
           Salary     : ₹8-15 LPA
           Skills     : React, Redux, TypeScript
           Posted     : 1 day ago
           Job ID     : 220126040161
           URL        : https://www.naukri.com/...
         ---
         ... (more results)
```

#### Example: Detail Flow

```
You:     "Get details for job 220126040161"

Claude:  [Calls naukri_get_job_details tool]
         → job_id: "220126040161"

Result:  # Senior React Developer
         **Company**: TCS
         **Location**: Hyderabad
         **Experience**: 2-5 Yrs
         **Salary**: ₹8-15 LPA
         **Work Mode**: Hybrid

         ## Required Skills
         React, Redux, TypeScript, Node.js, REST APIs

         ## Job Description
         We are looking for an experienced React developer...

         ## Employee Reviews (via AmbitionBox)
         - **Good Work Culture**: Great learning opportunities...
```

---

### 💻 Codex Code Intelligence MCP (`codex_mcp.py`)

#### Generate Code

```
"Generate a Python function to merge two sorted linked lists"
```

```
"Write a TypeScript REST API controller for user authentication with JWT"
```

```
"Create a Go function to perform binary search on a sorted slice"
```

#### Refactor Code

```
"Refactor this function to add type hints and handle edge cases:
def calc(a, b, op):
    if op == '+': return a+b
    if op == '-': return a-b"
```

```
"Optimize this SQL query builder for performance and add input sanitization"
```

#### Example: Code Generation Flow

```
You:     "Generate a Python async function to retry HTTP requests with
          exponential backoff, using httpx"

Claude:  [Calls codex_generate_code tool]
         → prompt: "async function to retry HTTP requests with exponential backoff using httpx"
         → language: "python"
         → model: "gpt-4o"

Result:  import httpx
         import asyncio
         from typing import Optional

         async def retry_request(
             url: str,
             max_retries: int = 3,
             base_delay: float = 1.0,
             ...
         ) -> httpx.Response:
             """Retry an HTTP GET with exponential backoff."""
             ...
```

---

## 📚 API Reference

### `claude_mcp.py` — Naukri Job Search Server

#### Tool: `naukri_search_jobs`

Search Naukri.com for job postings.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `keyword` | `str` | ✅ | — | Job title, skill, or tech stack |
| `location` | `str` | ❌ | `None` | City name (e.g., "Bangalore") |
| `max_jobs` | `int` | ❌ | `10` | Number of results (1–50) |
| `freshness_days` | `str` | ❌ | `"7"` | Posted within: `1`, `3`, `7`, `15`, `30`, `all` |
| `experience_years` | `int` | ❌ | `None` | Years of experience (0–35) |
| `sort_by` | `str` | ❌ | `"date"` | `"date"` or `"relevance"` |

#### Tool: `naukri_get_job_details`

Fetch full details for a specific job.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `job_id` | `str` | ✅ | — | Naukri Job ID from search results |

#### Resource: `naukri://cities`

Returns a comma-separated list of all supported city names.

---

### `codex_mcp.py` — Code Intelligence Server

#### Tool: `codex_generate_code`

Generate production-ready code.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `prompt` | `str` | ✅ | — | What to generate |
| `language` | `str` | ❌ | `"python"` | Target language |
| `model` | `str` | ❌ | `"gpt-4o"` | `gpt-4o`, `gpt-4o-mini`, or `o3-mini` |

#### Tool: `codex_refactor_code`

Refactor or review existing code.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `code` | `str` | ✅ | — | Source code to refactor |
| `instruction` | `str` | ✅ | — | Refactoring goals |
| `language` | `str` | ❌ | `"python"` | Language of the code |

---

## 🏙 Supported Cities

The Naukri MCP server supports **50+ Indian cities** with pre-mapped city IDs for accurate location filtering:

<details>
<summary><strong>Click to expand full city list</strong></summary>

| City | Aliases | Naukri ID |
|---|---|---|
| Mumbai | Bombay | 134 |
| Navi Mumbai | — | 138 |
| Thane | — | 323 |
| Mumbai Suburban | — | 135 |
| Bengaluru | Bangalore | 97 |
| Delhi | — | 382 |
| New Delhi | — | 6 |
| Delhi/NCR | NCR | 9508 |
| Gurugram | Gurgaon | 73 |
| Noida | — | 220 |
| Greater Noida | — | 350 |
| Faridabad | — | 72 |
| Ghaziabad | — | 213 |
| Pune | — | 139 |
| Hyderabad | — | 17 |
| Chennai | — | 183 |
| Kolkata | — | 232 |
| Ahmedabad | — | 51 |
| Surat | — | 64 |
| Vadodara | — | 65 |
| Jaipur | — | 173 |
| Lucknow | — | 216 |
| Kanpur | — | 215 |
| Indore | — | 125 |
| Bhopal | — | 123 |
| Chandigarh | — | 4 |
| Mohali | — | 167 |
| Coimbatore | — | 184 |
| Kochi | Ernakulam | 110/111 |
| Thiruvananthapuram | Trivandrum | 120 |
| Nagpur | — | 136 |
| Nashik | — | 137 |
| Visakhapatnam | Vizag | 26 |
| Bhubaneswar | — | 155 |
| Goa | — | 45 |
| Mangaluru | Mangalore | 105 |
| Mysuru | Mysore | 106 |
| Dehradun | — | 224 |
| Guwahati | — | 33 |
| Ludhiana | — | 166 |
| Amritsar | — | 162 |
| Patna | — | 38 |
| Ranchi | — | 94 |
| Jamshedpur | — | 93 |
| Raipur | — | 43 |
| Vijayawada | — | 25 |

</details>

> 💡 **Cities not in the list?** The server automatically appends the city name to the search keyword as a fallback.

---

## 📂 Project Structure

```
MCP-naukri/
├── claude_mcp.py       # 🔍 Naukri Job Search MCP Server
├── codex_mcp.py        # 💻 Code Intelligence MCP Server
├── requirements.txt    # 📦 Python dependencies
├── .env                # 🔐 API keys (create this — not committed)
├── .gitignore          # 🚫 Git ignore rules
├── assets/
│   └── banner.jpg      # 🖼  README banner image
└── README.md           # 📖 This file
```

---

## 🔧 Troubleshooting

<details>
<summary><strong>❌ "APIFY_API_TOKEN is not set"</strong></summary>

- Ensure `.env` exists in the project root
- Verify the token is correct: `APIFY_API_TOKEN=apify_api_xxxxxxx`
- If using Claude Desktop config, ensure `env` block has the token
- Restart your MCP client after changes

</details>

<details>
<summary><strong>❌ "OPENAI_API_KEY is not set"</strong></summary>

- Create `.env` with `OPENAI_API_KEY=sk-xxxxxxx`
- Ensure your OpenAI account has API credits
- Check the key hasn't been revoked at [platform.openai.com](https://platform.openai.com/api-keys)

</details>

<details>
<summary><strong>❌ HTTP 401 — Invalid API Token</strong></summary>

- Regenerate your Apify token at **Settings → Integrations**
- Update `.env` and restart the server

</details>

<details>
<summary><strong>❌ HTTP 429 — Rate Limit</strong></summary>

- Wait 30–60 seconds before retrying
- Reduce `max_jobs` to lower values
- Consider upgrading your Apify plan for higher limits

</details>

<details>
<summary><strong>❌ Timeout Error (120s)</strong></summary>

- The Apify actor takes too long; try a narrower search
- Reduce `max_jobs` or add more specific filters
- Check [Apify status page](https://status.apify.com/) for outages

</details>

<details>
<summary><strong>❌ Server not showing in Claude Desktop</strong></summary>

- Verify the config JSON is valid (use a JSON validator)
- Use **absolute paths** for the `args` field
- Ensure Python is in your system PATH
- Restart Claude Desktop completely (quit & reopen)
- Check Claude Desktop logs for MCP connection errors

</details>

<details>
<summary><strong>❌ ModuleNotFoundError</strong></summary>

- Ensure you've installed dependencies: `pip install -r requirements.txt`
- If using a virtual environment, make sure it's activated
- Use the full Python path in your MCP client config:
  ```json
  "command": "/path/to/venv/bin/python"
  ```

</details>

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m "Add amazing feature"`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ using <a href="https://modelcontextprotocol.io/">MCP</a> · <a href="https://apify.com/">Apify</a> · <a href="https://openai.com/">OpenAI</a>
</p>
