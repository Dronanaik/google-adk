"""Business data generation tools for test data."""

from typing import List, Dict, Any
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()


def generate_company_names(count: int = 10) -> List[str]:
    """
    Generate realistic company names.
    
    Args:
        count (int): Number of company names to generate (default: 10, max: 1000)
    
    Returns:
        List[str]: List of company names
    """
    count = min(count, 1000)
    return [fake.company() for _ in range(count)]


def generate_product_names(count: int = 10, include_description: bool = False) -> List[Dict[str, str]]:
    """
    Generate product names and optionally descriptions.
    
    Args:
        count (int): Number of products to generate (default: 10, max: 1000)
        include_description (bool): Whether to include product descriptions (default: False)
    
    Returns:
        List[Dict[str, str]]: List of product dictionaries with name and optional description
    """
    count = min(count, 1000)
    products = []
    
    # Product categories and adjectives for variety
    categories = ["Pro", "Ultra", "Max", "Plus", "Elite", "Premium", "Standard", "Basic"]
    product_types = ["Widget", "Gadget", "Device", "Tool", "System", "Platform", "Solution", "Suite"]
    
    for _ in range(count):
        # Mix of fake catch phrases and custom product names
        if random.choice([True, False]):
            name = f"{random.choice(categories)} {random.choice(product_types)}"
        else:
            name = fake.catch_phrase()
        
        product = {"name": name}
        
        if include_description:
            product["description"] = fake.text(max_nb_chars=200)
        
        products.append(product)
    
    return products


def generate_prices(count: int = 10, min_price: float = 1.0, max_price: float = 1000.0, 
                   currency: str = "USD") -> List[Dict[str, Any]]:
    """
    Generate realistic price values.
    
    Args:
        count (int): Number of prices to generate (default: 10, max: 1000)
        min_price (float): Minimum price value (default: 1.0)
        max_price (float): Maximum price value (default: 1000.0)
        currency (str): Currency code (default: 'USD')
    
    Returns:
        List[Dict[str, Any]]: List of price dictionaries with amount and currency
    """
    count = min(count, 1000)
    prices = []
    
    for _ in range(count):
        # Generate price with realistic decimal places
        price = round(random.uniform(min_price, max_price), 2)
        prices.append({
            "amount": price,
            "currency": currency,
            "formatted": f"{currency} {price:.2f}"
        })
    
    return prices


def generate_invoice_data(count: int = 10) -> List[Dict[str, Any]]:
    """
    Generate invoice/transaction data with items, amounts, and dates.
    
    Args:
        count (int): Number of invoices to generate (default: 10, max: 500)
    
    Returns:
        List[Dict[str, Any]]: List of invoice dictionaries with complete transaction details
    """
    count = min(count, 500)
    invoices = []
    
    for _ in range(count):
        # Generate invoice items
        num_items = random.randint(1, 10)
        items = []
        subtotal = 0.0
        
        for _ in range(num_items):
            quantity = random.randint(1, 20)
            unit_price = round(random.uniform(5.0, 500.0), 2)
            item_total = round(quantity * unit_price, 2)
            subtotal += item_total
            
            items.append({
                "description": fake.catch_phrase(),
                "quantity": quantity,
                "unit_price": unit_price,
                "total": item_total
            })
        
        # Calculate tax and total
        tax_rate = 0.08  # 8% tax
        tax = round(subtotal * tax_rate, 2)
        total = round(subtotal + tax, 2)
        
        # Generate invoice
        invoice_date = fake.date_time_between(start_date="-1y", end_date="now")
        due_date = invoice_date + timedelta(days=30)
        
        invoice = {
            "invoice_number": fake.bothify(text="INV-####-????").upper(),
            "invoice_date": invoice_date.isoformat(),
            "due_date": due_date.isoformat(),
            "customer": {
                "name": fake.company(),
                "email": fake.company_email(),
                "address": fake.address().replace("\n", ", ")
            },
            "items": items,
            "subtotal": subtotal,
            "tax": tax,
            "tax_rate": tax_rate,
            "total": total,
            "currency": "USD",
            "status": random.choice(["paid", "pending", "overdue", "draft"])
        }
        
        invoices.append(invoice)
    
    return invoices
