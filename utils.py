import random
import string


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
    base = random.choice(pics_url_list)
    return f"{base}?r={get_random_mix_id()}"


def human_bool(value: bool) -> str:
    return "Yes ✅" if value else "No ❌"


def paginate(items, page: int, page_size: int):
    """Return (page_items, total_pages) for a 1-indexed page."""
    total_pages = max(1, (len(items) + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], total_pages, page
