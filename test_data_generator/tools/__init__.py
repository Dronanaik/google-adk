"""Tools package for Test Data Generator agent."""

from .personal_data import (
    generate_names,
    generate_emails,
    generate_phone_numbers,
    generate_addresses,
    generate_user_profiles,
)
from .business_data import (
    generate_company_names,
    generate_product_names,
    generate_prices,
    generate_invoice_data,
)
from .numeric_data import (
    generate_integers,
    generate_floats,
    generate_dates,
    generate_timestamps,
    generate_uuids,
)
from .custom_patterns import (
    generate_from_regex,
    generate_from_format,
    generate_json_data,
    generate_csv_data,
)

__all__ = [
    # Personal data
    "generate_names",
    "generate_emails",
    "generate_phone_numbers",
    "generate_addresses",
    "generate_user_profiles",
    # Business data
    "generate_company_names",
    "generate_product_names",
    "generate_prices",
    "generate_invoice_data",
    # Numeric data
    "generate_integers",
    "generate_floats",
    "generate_dates",
    "generate_timestamps",
    "generate_uuids",
    # Custom patterns
    "generate_from_regex",
    "generate_from_format",
    "generate_json_data",
    "generate_csv_data",
]
