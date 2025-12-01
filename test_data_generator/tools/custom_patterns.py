"""Custom pattern generation tools for test data."""

from typing import List, Dict, Any
import random
import string
import json
import csv
import io
from exrex import generate as regex_generate


def generate_from_regex(pattern: str, count: int = 10) -> List[str]:
    """
    Generate strings that match a given regex pattern.
    
    Args:
        pattern (str): Regular expression pattern to match
        count (int): Number of strings to generate (default: 10, max: 1000)
    
    Returns:
        List[str]: List of strings matching the regex pattern
    
    Examples:
        - Pattern '[A-Z]{3}-\\d{4}' generates strings like 'ABC-1234'
        - Pattern '\\d{3}-\\d{2}-\\d{4}' generates SSN-like strings
    """
    count = min(count, 1000)
    results = []
    
    try:
        for _ in range(count):
            # Convert generator to string by getting next value
            gen = regex_generate(pattern)
            results.append(next(gen) if hasattr(gen, '__next__') else str(gen))
    except Exception as e:
        return [f"Error generating from pattern: {str(e)}"]
    
    return results


def generate_from_format(format_string: str, count: int = 10) -> List[str]:
    """
    Generate data from a format string with placeholders.
    
    Args:
        format_string (str): Format string with placeholders:
            - {name} - Random name
            - {email} - Random email
            - {number:N} - Random N-digit number
            - {letter:N} - Random N letters
            - {uuid} - Random UUID
        count (int): Number of strings to generate (default: 10, max: 1000)
    
    Returns:
        List[str]: List of formatted strings
    
    Examples:
        - 'USER-{number:5}' generates 'USER-12345'
        - '{name}-{letter:3}' generates 'John-ABC'
    """
    count = min(count, 1000)
    results = []
    
    from faker import Faker
    import uuid
    fake = Faker()
    
    for _ in range(count):
        result = format_string
        
        # Replace placeholders
        result = result.replace("{name}", fake.first_name())
        result = result.replace("{email}", fake.email())
        result = result.replace("{uuid}", str(uuid.uuid4()))
        
        # Handle {number:N} pattern
        import re
        number_pattern = r'\{number:(\d+)\}'
        for match in re.finditer(number_pattern, result):
            digits = int(match.group(1))
            random_number = ''.join(random.choices(string.digits, k=digits))
            result = result.replace(match.group(0), random_number, 1)
        
        # Handle {letter:N} pattern
        letter_pattern = r'\{letter:(\d+)\}'
        for match in re.finditer(letter_pattern, result):
            length = int(match.group(1))
            random_letters = ''.join(random.choices(string.ascii_uppercase, k=length))
            result = result.replace(match.group(0), random_letters, 1)
        
        results.append(result)
    
    return results


def generate_json_data(schema: Dict[str, str], count: int = 10) -> str:
    """
    Generate structured JSON data based on a schema.
    
    Args:
        schema (Dict[str, str]): Schema defining field names and types:
            - 'name' - Person name
            - 'email' - Email address
            - 'integer' - Random integer
            - 'float' - Random float
            - 'boolean' - Random boolean
            - 'date' - Random date
            - 'uuid' - UUID
            - 'company' - Company name
            - 'phone' - Phone number
        count (int): Number of JSON objects to generate (default: 10, max: 1000)
    
    Returns:
        str: JSON string containing array of generated objects
    
    Example:
        schema = {"id": "uuid", "name": "name", "age": "integer", "active": "boolean"}
    """
    count = min(count, 1000)
    
    from faker import Faker
    import uuid
    fake = Faker()
    
    results = []
    
    for _ in range(count):
        obj = {}
        
        for field_name, field_type in schema.items():
            if field_type == "name":
                obj[field_name] = fake.name()
            elif field_type == "email":
                obj[field_name] = fake.email()
            elif field_type == "integer":
                obj[field_name] = random.randint(1, 1000)
            elif field_type == "float":
                obj[field_name] = round(random.uniform(0, 1000), 2)
            elif field_type == "boolean":
                obj[field_name] = random.choice([True, False])
            elif field_type == "date":
                obj[field_name] = fake.date()
            elif field_type == "uuid":
                obj[field_name] = str(uuid.uuid4())
            elif field_type == "company":
                obj[field_name] = fake.company()
            elif field_type == "phone":
                obj[field_name] = fake.phone_number()
            else:
                obj[field_name] = fake.word()
        
        results.append(obj)
    
    return json.dumps(results, indent=2)


def generate_csv_data(columns: List[str], column_types: List[str], count: int = 10) -> str:
    """
    Generate CSV formatted data.
    
    Args:
        columns (List[str]): List of column names
        column_types (List[str]): List of data types for each column (same types as generate_json_data)
        count (int): Number of rows to generate (default: 10, max: 1000)
    
    Returns:
        str: CSV formatted string
    
    Example:
        columns = ["id", "name", "email", "age"]
        column_types = ["uuid", "name", "email", "integer"]
    """
    count = min(count, 1000)
    
    from faker import Faker
    import uuid
    fake = Faker()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(columns)
    
    # Write data rows
    for _ in range(count):
        row = []
        
        for col_type in column_types:
            if col_type == "name":
                row.append(fake.name())
            elif col_type == "email":
                row.append(fake.email())
            elif col_type == "integer":
                row.append(random.randint(1, 1000))
            elif col_type == "float":
                row.append(round(random.uniform(0, 1000), 2))
            elif col_type == "boolean":
                row.append(random.choice([True, False]))
            elif col_type == "date":
                row.append(fake.date())
            elif col_type == "uuid":
                row.append(str(uuid.uuid4()))
            elif col_type == "company":
                row.append(fake.company())
            elif col_type == "phone":
                row.append(fake.phone_number())
            else:
                row.append(fake.word())
        
        writer.writerow(row)
    
    return output.getvalue()
