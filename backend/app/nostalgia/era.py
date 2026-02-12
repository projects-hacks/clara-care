"""
Nostalgia Mode - Era Calculation
Calculates patient's "golden years" (ages 15-25) for targeted content
"""


def calculate_golden_years(birth_year: int) -> tuple[int, int]:
    """
    Calculate patient's golden years (peak memory formation ages 15-25)
    
    Args:
        birth_year: Patient's birth year (e.g., 1951)
    
    Returns:
        Tuple of (start_year, end_year) e.g., (1966, 1976)
    
    Example:
        >>> calculate_golden_years(1951)
        (1966, 1976)
    """
    return (birth_year + 15, birth_year + 25)


def get_era_label(start_year: int, end_year: int) -> str:
    """
    Generate era label from year range
    
    Args:
        start_year: Start of era (e.g., 1966)
        end_year: End of era (e.g., 1976)
    
    Returns:
        Era label (e.g., "1960s-1970s")
    
    Example:
        >>> get_era_label(1966, 1976)
        '1960s-1970s'
    """
    start_decade = (start_year // 10) * 10
    end_decade = (end_year // 10) * 10
    
    if start_decade == end_decade:
        return f"{start_decade}s"
    else:
        return f"{start_decade}s-{end_decade}s"


def get_decade_from_year(year: int) -> str:
    """
    Get decade label from year
    
    Args:
        year: Year (e.g., 1963)
    
    Returns:
        Decade label (e.g., "1960s")
    
    Example:
        >>> get_decade_from_year(1963)
        '1960s'
    """
    decade = (year // 10) * 10
    return f"{decade}s"
