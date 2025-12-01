"""Numeric and temporal data generation tools for test data."""

from typing import List, Dict, Any, Optional
import random
import uuid
from datetime import datetime, timedelta


def generate_integers(count: int = 10, min_value: int = 0, max_value: int = 100) -> List[int]:
    """
    Generate random integers within a specified range.
    
    Args:
        count (int): Number of integers to generate (default: 10, max: 10000)
        min_value (int): Minimum value (default: 0)
        max_value (int): Maximum value (default: 100)
    
    Returns:
        List[int]: List of random integers
    """
    count = min(count, 10000)
    return [random.randint(min_value, max_value) for _ in range(count)]


def generate_floats(count: int = 10, min_value: float = 0.0, max_value: float = 100.0, 
                   precision: int = 2) -> List[float]:
    """
    Generate random floating-point numbers with specified precision.
    
    Args:
        count (int): Number of floats to generate (default: 10, max: 10000)
        min_value (float): Minimum value (default: 0.0)
        max_value (float): Maximum value (default: 100.0)
        precision (int): Number of decimal places (default: 2)
    
    Returns:
        List[float]: List of random floats
    """
    count = min(count, 10000)
    return [round(random.uniform(min_value, max_value), precision) for _ in range(count)]


def generate_dates(count: int = 10, start_date: Optional[str] = None, end_date: Optional[str] = None, 
                  format: str = "iso") -> List[str]:
    """
    Generate random dates within a specified range.
    
    Args:
        count (int): Number of dates to generate (default: 10, max: 10000)
        start_date (str): Start date in ISO format (YYYY-MM-DD). If not provided, uses 1 year ago.
        end_date (str): End date in ISO format (YYYY-MM-DD). If not provided, uses today.
        format (str): Output format - 'iso' (YYYY-MM-DD), 'us' (MM/DD/YYYY), or 'eu' (DD/MM/YYYY)
    
    Returns:
        List[str]: List of date strings
    """
    count = min(count, 10000)
    
    # Parse dates or use defaults
    if start_date:
        start = datetime.fromisoformat(start_date)
    else:
        start = datetime.now() - timedelta(days=365)
    
    if end_date:
        end = datetime.fromisoformat(end_date)
    else:
        end = datetime.now()
    
    # Generate random dates
    dates = []
    time_delta = (end - start).total_seconds()
    
    for _ in range(count):
        random_seconds = random.uniform(0, time_delta)
        random_date = start + timedelta(seconds=random_seconds)
        
        # Format based on requested format
        if format == "us":
            formatted = random_date.strftime("%m/%d/%Y")
        elif format == "eu":
            formatted = random_date.strftime("%d/%m/%Y")
        else:  # iso
            formatted = random_date.strftime("%Y-%m-%d")
        
        dates.append(formatted)
    
    return dates


def generate_timestamps(count: int = 10, start_date: Optional[str] = None, end_date: Optional[str] = None,
                       include_timezone: bool = False) -> List[str]:
    """
    Generate random timestamps.
    
    Args:
        count (int): Number of timestamps to generate (default: 10, max: 10000)
        start_date (str): Start date in ISO format. If not provided, uses 1 year ago.
        end_date (str): End date in ISO format. If not provided, uses now.
        include_timezone (bool): Whether to include timezone info (default: False)
    
    Returns:
        List[str]: List of ISO format timestamps
    """
    count = min(count, 10000)
    
    # Parse dates or use defaults
    if start_date:
        start = datetime.fromisoformat(start_date)
    else:
        start = datetime.now() - timedelta(days=365)
    
    if end_date:
        end = datetime.fromisoformat(end_date)
    else:
        end = datetime.now()
    
    # Generate random timestamps
    timestamps = []
    time_delta = (end - start).total_seconds()
    
    for _ in range(count):
        random_seconds = random.uniform(0, time_delta)
        random_timestamp = start + timedelta(seconds=random_seconds)
        
        if include_timezone:
            formatted = random_timestamp.isoformat() + "Z"
        else:
            formatted = random_timestamp.isoformat()
        
        timestamps.append(formatted)
    
    return timestamps


def generate_uuids(count: int = 10, version: int = 4) -> List[str]:
    """
    Generate UUIDs (Universally Unique Identifiers).
    
    Args:
        count (int): Number of UUIDs to generate (default: 10, max: 10000)
        version (int): UUID version - 1 (time-based) or 4 (random) (default: 4)
    
    Returns:
        List[str]: List of UUID strings
    """
    count = min(count, 10000)
    uuids = []
    
    for _ in range(count):
        if version == 1:
            generated_uuid = str(uuid.uuid1())
        else:  # version 4 (random)
            generated_uuid = str(uuid.uuid4())
        
        uuids.append(generated_uuid)
    
    return uuids
