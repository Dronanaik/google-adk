# Test Data Generator Agent

An intelligent test data generator built with [Google ADK (Agent Development Kit)](https://google.github.io/adk-docs/) that creates realistic, structured test data for software testing, database seeding, and development purposes.

## Features

### 🎭 Personal Data Generation
- **Names**: Generate realistic first and last names with gender options
- **Emails**: Create email addresses with custom domains
- **Phone Numbers**: Generate phone numbers for different countries
- **Addresses**: Create complete addresses with street, city, state, zip
- **User Profiles**: Generate complete user profiles with all details

### 💼 Business Data Generation
- **Company Names**: Generate realistic company names
- **Products**: Create product names with optional descriptions
- **Prices**: Generate price values with currency formatting
- **Invoices**: Create complete invoice data with line items, taxes, totals

### 🔢 Numeric & Temporal Data
- **Integers**: Random integers within specified ranges
- **Floats**: Floating-point numbers with precision control
- **Dates**: Generate dates within custom ranges and formats
- **Timestamps**: ISO format timestamps with timezone options
- **UUIDs**: Generate version 1 or 4 UUIDs

### 🎨 Custom Pattern Generation
- **Regex Patterns**: Generate strings matching regex patterns
- **Format Strings**: Create data from custom format templates
- **JSON Data**: Generate structured JSON based on schemas
- **CSV Data**: Create CSV files with custom columns and types

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd test_data_generator
   ```

2. **Create and activate a Python virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux/Mac
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your Google API key**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your Google API key:
     ```
     GOOGLE_API_KEY=your_actual_api_key_here
     ```
   - Get your API key from [Google AI Studio](https://aistudio.google.com/apikey)

## Usage

### Running with CLI

Start the agent in command-line interface mode:

```bash
adk run
```

Then interact with the agent using natural language:

```
> Generate 5 user profiles
> I need 20 email addresses with domain example.com
> Create 10 random dates between 2024-01-01 and 2024-12-31
> Generate invoice data for 3 transactions
```

### Running with Web Interface

Start the agent with a web UI:

```bash
adk run --ui
```

This will open a browser interface where you can interact with the agent.

### Example Queries

Here are some example queries you can use:

**Personal Data:**
- "Generate 10 random names"
- "I need 50 email addresses for testing"
- "Create 20 phone numbers for US and UK"
- "Generate 5 complete user profiles with all details"

**Business Data:**
- "Give me 15 company names"
- "Generate 10 products with descriptions"
- "Create 5 invoices with multiple line items"
- "I need 100 random prices between $10 and $500"

**Numeric Data:**
- "Generate 50 random integers between 1 and 100"
- "Create 20 dates in January 2024"
- "I need 10 UUIDs"
- "Generate timestamps for the last 30 days"

**Custom Patterns:**
- "Generate 10 strings matching pattern [A-Z]{3}-\\d{4}"
- "Create data in format USER-{number:5}"
- "Generate JSON with fields: id (uuid), name (name), age (integer)"
- "Create a CSV with columns: id, email, company"

## Programmatic Usage

You can also use the agent programmatically in your Python code:

```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent import root_agent
import asyncio

async def generate_test_data():
    # Set up session
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_data_gen",
        user_id="user123",
        session_id="session123"
    )
    
    # Create runner
    runner = Runner(
        agent=root_agent,
        app_name="test_data_gen",
        session_service=session_service
    )
    
    # Send query
    query = "Generate 5 user profiles"
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    # Get response
    events = runner.run_async(
        user_id="user123",
        session_id="session123",
        new_message=content
    )
    
    async for event in events:
        if event.is_final_response():
            print(event.content.parts[0].text)

# Run
asyncio.run(generate_test_data())
```

## Available Tools

The agent has access to the following tools:

### Personal Data Tools
- `generate_names(count, gender)` - Generate names
- `generate_emails(count, domain)` - Generate emails
- `generate_phone_numbers(count, country_code)` - Generate phone numbers
- `generate_addresses(count, country)` - Generate addresses
- `generate_user_profiles(count)` - Generate complete user profiles

### Business Data Tools
- `generate_company_names(count)` - Generate company names
- `generate_product_names(count, include_description)` - Generate products
- `generate_prices(count, min_price, max_price, currency)` - Generate prices
- `generate_invoice_data(count)` - Generate invoices

### Numeric Data Tools
- `generate_integers(count, min_value, max_value)` - Generate integers
- `generate_floats(count, min_value, max_value, precision)` - Generate floats
- `generate_dates(count, start_date, end_date, format)` - Generate dates
- `generate_timestamps(count, start_date, end_date, include_timezone)` - Generate timestamps
- `generate_uuids(count, version)` - Generate UUIDs

### Custom Pattern Tools
- `generate_from_regex(pattern, count)` - Generate from regex
- `generate_from_format(format_string, count)` - Generate from format
- `generate_json_data(schema, count)` - Generate JSON
- `generate_csv_data(columns, column_types, count)` - Generate CSV

## Project Structure

```
test_data_generator/
├── agent.py                 # Main agent definition
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment configuration
├── README.md               # This file
├── example_usage.py        # Example usage script
└── tools/                  # Data generation tools
    ├── __init__.py
    ├── personal_data.py    # Personal data generators
    ├── business_data.py    # Business data generators
    ├── numeric_data.py     # Numeric data generators
    └── custom_patterns.py  # Custom pattern generators
```

## Contributing

This agent is built using Google ADK. To extend functionality:

1. Add new tool functions in the appropriate `tools/*.py` file
2. Import and add the tool to the `root_agent` tools list in `agent.py`
3. Update the agent's instruction to include information about the new tool

## License

This project uses the Google ADK framework. Please refer to the [Google ADK license](https://github.com/google/adk-docs/blob/main/LICENSE) for details.

## Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Faker Library Documentation](https://faker.readthedocs.io/)
- [Google AI Studio](https://aistudio.google.com/)
