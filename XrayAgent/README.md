# XrayAgent 🧪

A multi-agent system built with Google ADK for automated test case management in Jira using the Xray plugin. This agent intelligently generates test cases from user stories and seamlessly integrates them into Xray for comprehensive test management.

## 🌟 Features

- **Multi-Agent Architecture**: Hierarchical agent system with specialized subagents
- **Jira Integration**: Comprehensive Jira REST API v3 wrapper with 73+ functions
- **Xray Test Management**: Automated test case creation and import to Xray Cloud
- **Intelligent Test Generation**: AI-powered test case generation from user stories
- **Bulk Operations**: Efficient bulk import of test cases with job status tracking

## 🏗️ Architecture

```
XrayAgent/
├── agent.py              # Root agent orchestrator
├── tools.py              # Xray API integration tools
└── subagents/
    ├── jira_agent/       # Jira API operations
    │   ├── agent.py
    │   ├── prompts.py
    │   └── tools.py      # 73+ Jira API functions
    └── xray_agent/       # Xray-specific operations
        ├── agent.py
        └── prompts.py
```

### Agent Hierarchy

- **Root Agent (XrayAgent)**: Main orchestrator for user interactions
- **Jira Subagent**: Handles all Jira API operations including:
  - Custom field management (associations, contexts, options, values)
  - Field configurations and schemes
  - Issue types and type schemes
  - 9 API groups with 73+ specialized functions
- **Xray Subagent**: Manages Xray-specific test operations

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Google ADK installed
- Jira Cloud instance
- Xray Cloud subscription
- Valid API credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Dronanaik/google-adk.git
   cd google-adk/XrayAgent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   # Google AI Configuration
   GOOGLE_MODEL_NAME=gemini-2.0-flash-exp
   GOOGLE_API_KEY=your_google_api_key
   
   # Jira Configuration
   JIRA_URL=https://your-domain.atlassian.net
   JIRA_USERNAME=your-email@example.com
   JIRA_API_TOKEN=your_jira_api_token
   
   # Xray Configuration
   XRAY_BASE_URL=https://xray.cloud.getxray.app/api/v2
   XRAY_CLIENT_ID=your_xray_client_id
   XRAY_CLIENT_SECRET=your_xray_client_secret
   ```

### Running the Agent

```bash
# Using ADK CLI
adk web

# Or run directly
python -m XrayAgent.agent
```

## 📚 Core Functionality

### Xray API Tools

#### Authentication
```python
from XrayAgent.tools import get_xray_token, build_auth_header

# Get authentication token
token = get_xray_token(client_id, client_secret)
headers = build_auth_header(token)
```

#### Import Manual Tests
```python
from XrayAgent.tools import import_manual_tests_cloud

test_payload = [{
    "projectKey": "XSP1",
    "summary": "Login functionality test",
    "testType": "Manual",
    "steps": [
        {"action": "Enter username", "result": "Accepted"},
        {"action": "Enter password", "result": "Accepted"},
        {"action": "Click login", "result": "User redirected to dashboard"}
    ]
}]

result = import_manual_tests_cloud(token, test_payload)
```

#### Check Import Status
```python
from XrayAgent.tools import get_import_job_status

job_id = result['jobId']
status = get_import_job_status(token, job_id)
```

### Jira API Coverage

The Jira subagent provides comprehensive coverage of Jira REST API v3:

**Implemented API Groups (73+ functions):**
- ✅ Issue Custom Field Associations (4 functions)
- ✅ Issue Custom Field Configuration (3 functions)
- ✅ Issue Custom Field Contexts (13 functions)
- ✅ Issue Custom Field Options (7 functions)
- ✅ Issue Custom Field Values (2 functions)
- ✅ Issue Field Configurations (16 functions)
- ✅ Issue Fields (9 functions)
- ✅ Issue Types (8 functions)
- ✅ Issue Type Schemes (9 functions)

## 🎯 Use Cases

1. **Automated Test Case Generation**
   - Extract user stories from Jira
   - Generate comprehensive test cases using AI
   - Import test cases to Xray automatically

2. **Test Management Automation**
   - Bulk import of manual test cases
   - Synchronize test cases across projects
   - Track import job status

3. **Custom Field Management**
   - Create and configure custom fields
   - Manage field contexts and options
   - Associate fields with issue types

## 🔧 Configuration

### Jira API Token

1. Log in to Atlassian Account
2. Go to Security → API tokens
3. Create a new token
4. Copy the token to your `.env` file

### Xray Credentials

1. Log in to Xray Cloud
2. Go to API Keys section
3. Generate Client ID and Client Secret
4. Add credentials to your `.env` file

## 📖 API Reference

### Xray Tools

| Function | Description |
|----------|-------------|
| `get_xray_token()` | Authenticate and get Bearer token |
| `build_auth_header()` | Build authorization headers |
| `import_manual_tests_cloud()` | Bulk import test cases |
| `get_import_job_status()` | Check import job status |

### Jira Tools

The Jira subagent provides 73+ functions across 9 API groups. See `subagents/jira_agent/tools.py` for complete documentation.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🔗 Links

- [Google ADK Documentation](https://github.com/google/adk)
- [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Xray Cloud API](https://docs.getxray.app/display/XRAYCLOUD/REST+API)

## 👤 Author

**Drona Naik**
- GitHub: [@Dronanaik](https://github.com/Dronanaik)

---

Built with ❤️ using Google ADK
