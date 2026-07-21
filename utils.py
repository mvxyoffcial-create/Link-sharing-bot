import random
import string
import math
from datetime import datetime
from typing import List, Tuple, Any


class Temp:
    """In-memory runtime state (per-process). Good enough for a single-worker bot;
    for multi-worker deployments swap this for a shared cache (Redis)."""
    START_TIME = None
    # user_id -> dict describing what step of a conversation they're in
    CONVERSATION = {}
    # user_id -> dict holding partially-filled "add channel" submissions
    PENDING_SUBMISSION = {}


temp = Temp()


def get_random_mix_id(k: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=k))


def get_welcome_image(pics_url_list) -> str:
    """Get a random welcome image from the provided URLs"""
    if not pics_url_list:
        return "https://telegra.ph/file/placeholder.jpg"
    base = random.choice(pics_url_list)
    return f"{base}?r={get_random_mix_id()}"


def human_bool(value: bool) -> str:
    return "Yes ✅" if value else "No ❌"


def paginate(items: List[Any], page: int, page_size: int) -> Tuple[List[Any], int, int]:
    """
    Paginate a list of items
    
    Args:
        items: List of items to paginate
        page: Current page number (1-indexed)
        page_size: Number of items per page
    
    Returns:
        Tuple of (page_items, total_pages, current_page)
    """
    total_pages = max(1, (len(items) + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], total_pages, page


def format_number(num: int) -> str:
    """
    Format a number with K, M, B suffixes
    
    Args:
        num: Number to format
    
    Returns:
        Formatted string
    """
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)


def time_until(dt) -> str:
    """
    Get time remaining until a datetime
    
    Args:
        dt: Datetime object or string
    
    Returns:
        String like "2 days, 3 hours"
    """
    if not dt:
        return "Never"
    
    # Convert string to datetime if needed
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return "Invalid date"
    
    now = datetime.utcnow()
    diff = dt - now
    
    if diff.total_seconds() <= 0:
        return "Expired"
    
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 and days == 0:
        parts.append(f"{minutes}m")
    
    return " ".join(parts) if parts else "<1m"


def format_datetime(dt) -> str:
    """
    Format a datetime object to a readable string
    
    Args:
        dt: Datetime object
    
    Returns:
        Formatted string
    """
    if not dt:
        return "N/A"
    
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return dt
    
    return dt.strftime("%Y-%m-%d %H:%M")


def is_expired(expires_at) -> bool:
    """
    Check if a datetime is expired
    
    Args:
        expires_at: Datetime object or string
    
    Returns:
        True if expired, False otherwise
    """
    if not expires_at:
        return False
    
    if isinstance(expires_at, str):
        try:
            expires_at = datetime.fromisoformat(expires_at)
        except:
            return False
    
    return datetime.utcnow() > expires_at


def get_status_badge(status: str) -> str:
    """
    Get emoji badge for status
    
    Args:
        status: Status string
    
    Returns:
        Emoji badge
    """
    status_map = {
        "verified": "✅",
        "pending": "⏳",
        "rejected": "❌",
        "approved": "✅",
        "expired": "⏰",
        "active": "🟢",
        "inactive": "🔴"
    }
    return status_map.get(status.lower(), "📌")


def get_user_type_badge(is_premium: bool) -> str:
    """
    Get emoji badge for user type
    
    Args:
        is_premium: True if premium user
    
    Returns:
        Emoji badge
    """
    return "⭐" if is_premium else "📊"


def truncate_text(text: str, length: int = 50) -> str:
    """
    Truncate text to a certain length
    
    Args:
        text: Text to truncate
        length: Maximum length
    
    Returns:
        Truncated text
    """
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length] + "..."
