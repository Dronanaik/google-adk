"""Test Data Generator Agent using Google ADK.

This agent helps generate realistic test data for various testing scenarios.
"""

from google.adk.agents.llm_agent import Agent
from test_data_generator.tools import (
    # Personal data
    generate_names,
    generate_emails,
    generate_phone_numbers,
    generate_addresses,
    generate_user_profiles,
    # Business data
    generate_company_names,
    generate_product_names,
    generate_prices,
    generate_invoice_data,
    # Numeric data
    generate_integers,
    generate_floats,
    generate_dates,
    generate_timestamps,
    generate_uuids,
    # Custom patterns
    generate_from_regex,
    generate_from_format,
    generate_json_data,
    generate_csv_data,
)

# Define the root agent
root_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='test_data_generator',
    description=(
        'An intelligent test data generator that creates realistic, structured test data '
        'for software testing, database seeding, and development purposes.'
    ),
    instruction="""You are a helpful test data generation assistant. Your role is to help users generate 
realistic and appropriate test data for their testing needs.

When a user requests test data:
1. Understand what type of data they need (personal, business, numeric, custom patterns, etc.)
2. Ask clarifying questions if needed (e.g., how many records, specific formats, constraints)
3. Use the appropriate tools to generate the requested data
4. Present the data in a clear, readable format
5. Offer to export the data in different formats (JSON, CSV) if helpful

Available data types you can generate:
- Personal data: names, emails, phone numbers, addresses, complete user profiles
- Business data: company names, products, prices, invoices
- Numeric data: integers, floats, dates, timestamps, UUIDs
- Custom patterns: regex patterns, format strings, structured JSON/CSV

Best practices:
- Default to generating 10 items unless the user specifies otherwise
- For large datasets (>100 items), confirm with the user first
- Suggest realistic constraints and formats based on common use cases
- When generating structured data (JSON/CSV), ensure proper formatting
- Provide examples of how to use the generated data in tests

Be conversational, helpful, and proactive in suggesting the best data generation approach 
for the user's testing needs.""",
    tools=[
        # Personal data tools
        generate_names,
        generate_emails,
        generate_phone_numbers,
        generate_addresses,
        generate_user_profiles,
        # Business data tools
        generate_company_names,
        generate_product_names,
        generate_prices,
        generate_invoice_data,
        # Numeric data tools
        generate_integers,
        generate_floats,
        generate_dates,
        generate_timestamps,
        generate_uuids,
        # Custom pattern tools
        generate_from_regex,
        generate_from_format,
        generate_json_data,
        generate_csv_data,
    ],
)
