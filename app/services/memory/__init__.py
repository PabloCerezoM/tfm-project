"""
Memory service package - exports legacy interface for backward compatibility.
"""
from services.memory.repository import interests_repository


def load_interests():
    """Load user interests - delegates to new repository."""
    return interests_repository.get_interests_list()


def add_interest(interest):
    """Add interest - delegates to new repository."""
    return interests_repository.add_interest(interest)


def remove_interest(interest):
    """Remove interest - delegates to new repository."""
    return interests_repository.remove_interest(interest)


# Export functions for backward compatibility
__all__ = ['load_interests', 'add_interest', 'remove_interest']