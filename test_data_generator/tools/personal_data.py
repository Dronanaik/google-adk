"""Personal data generation tools for test data."""

from typing import List, Dict, Any, Optional
from faker import Faker
import random

fake = Faker()


def generate_names(count: int = 10, gender: str = "random") -> List[Dict[str, str]]:
    """
    Generate realistic first and last names.
    
    Args:
        count (int): Number of names to generate (default: 10, max: 1000)
        gender (str): Gender for names - 'male', 'female', or 'random' (default: 'random')
    
    Returns:
        List[Dict[str, str]]: List of dictionaries with 'first_name' and 'last_name' keys
    """
    count = min(count, 1000)  # Limit to prevent excessive generation
    names = []
    
    for _ in range(count):
        if gender == "male":
            first_name = fake.first_name_male()
        elif gender == "female":
            first_name = fake.first_name_female()
        else:
            first_name = fake.first_name()
        
        names.append({
            "first_name": first_name,
            "last_name": fake.last_name()
        })
    
    return names


def generate_emails(count: int = 10, domain: Optional[str] = None) -> List[str]:
    """
    Generate email addresses with various formats.
    
    Args:
        count (int): Number of emails to generate (default: 10, max: 1000)
        domain (str): Optional domain to use (e.g., 'example.com'). If not provided, random domains are used.
    
    Returns:
        List[str]: List of email addresses
    """
    count = min(count, 1000)
    emails = []
    
    for _ in range(count):
        if domain:
            username = fake.user_name()
            emails.append(f"{username}@{domain}")
        else:
            emails.append(fake.email())
    
    return emails


def generate_phone_numbers(count: int = 10, country_code: str = "US") -> List[str]:
    """
    Generate phone numbers with country codes.
    
    Args:
        count (int): Number of phone numbers to generate (default: 10, max: 1000)
        country_code (str): Country code for phone numbers (default: 'US')
    
    Returns:
        List[str]: List of phone numbers
    """
    count = min(count, 1000)
    
    # Set locale based on country code
    locale_map = {
        "US": "en_US",
        "UK": "en_GB",
        "CA": "en_CA",
        "AU": "en_AU",
        "IN": "en_IN",
        "DE": "de_DE",
        "FR": "fr_FR",
    }
    
    locale = locale_map.get(country_code, "en_US")
    localized_fake = Faker(locale)
    
    return [localized_fake.phone_number() for _ in range(count)]


def generate_addresses(count: int = 10, country: str = "US") -> List[Dict[str, str]]:
    """
    Generate street addresses with city, state, and zip code.
    
    Args:
        count (int): Number of addresses to generate (default: 10, max: 1000)
        country (str): Country for addresses (default: 'US')
    
    Returns:
        List[Dict[str, str]]: List of address dictionaries with street, city, state, zip, and country
    """
    count = min(count, 1000)
    
    locale_map = {
        "US": "en_US",
        "UK": "en_GB",
        "CA": "en_CA",
        "AU": "en_AU",
        "IN": "en_IN",
        "DE": "de_DE",
        "FR": "fr_FR",
    }
    
    locale = locale_map.get(country, "en_US")
    localized_fake = Faker(locale)
    
    addresses = []
    for _ in range(count):
        addresses.append({
            "street": localized_fake.street_address(),
            "city": localized_fake.city(),
            "state": localized_fake.state() if country == "US" else localized_fake.administrative_unit(),
            "zip": localized_fake.postcode(),
            "country": country
        })
    
    return addresses


def generate_user_profiles(count: int = 10) -> List[Dict[str, Any]]:
    """
    Generate complete user profiles with name, email, phone, address, and additional details.
    
    Args:
        count (int): Number of user profiles to generate (default: 10, max: 500)
    
    Returns:
        List[Dict[str, Any]]: List of complete user profile dictionaries
    """
    count = min(count, 500)
    profiles = []
    
    for _ in range(count):
        profile = {
            "id": fake.uuid4(),
            "username": fake.user_name(),
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone": fake.phone_number(),
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
            "address": {
                "street": fake.street_address(),
                "city": fake.city(),
                "state": fake.state(),
                "zip": fake.postcode(),
                "country": "US"
            },
            "job_title": fake.job(),
            "company": fake.company(),
            "created_at": fake.date_time_this_decade().isoformat(),
        }
        profiles.append(profile)
    
    return profiles
