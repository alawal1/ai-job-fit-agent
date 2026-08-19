"""Fetch utilities for job postings.

This module provides a reusable helper to download a job posting URL,
clean the HTML, and return the visible text content.
"""

from bs4 import BeautifulSoup
from requests import RequestException, get


def fetch_job_posting(url: str) -> str:
    """Fetch a job posting page and return the cleaned text content.

    Args:
        url: The URL of the job posting to fetch.

    Returns:
        The cleaned visible text from the page, truncated to 6000 characters.

    Raises:
        RuntimeError: If the network request fails or the page returns a bad status.
    """
    try:
        response = get(url, timeout=10)
        response.raise_for_status()
    except RequestException as exc:
        raise RuntimeError(f"Failed to fetch job posting: {exc}") from exc

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    return soup.get_text(separator="\n", strip=True)[:6000]
