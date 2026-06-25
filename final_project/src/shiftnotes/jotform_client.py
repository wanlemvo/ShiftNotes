from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


JOTFORM_API_BASE = "https://api.jotform.com"


def fetch_form_submissions(
    api_key: str,
    form_id: str,
    *,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """Fetch raw submissions for a JotForm form."""
    query = urlencode({"apiKey": api_key, "limit": limit, "offset": offset})
    url = f"{JOTFORM_API_BASE}/form/{form_id}/submissions?{query}"
    request = Request(url, headers={"User-Agent": "ShiftNotes/0.1"})

    with urlopen(request, timeout=30) as response:
        payload = response.read().decode("utf-8")

    return json.loads(payload)
