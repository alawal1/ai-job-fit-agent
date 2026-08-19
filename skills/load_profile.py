"""Load utilities for candidate profile markdown files.

This module provides helper functions to read profile markdown files from the
local data directory and combine them into a single profile string.
"""

import os


def load_file(filepath: str) -> str:
    """Read the contents of a file.

    Args:
        filepath: Path to the markdown file.

    Returns:
        The file contents as a string.
    """
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def load_full_profile() -> str:
    """Load the combined candidate profile from the data folder.

    This function reads all markdown files in the `data/` directory except
    `cv.md` and concatenates their contents with separator spacing.

    Returns:
        The combined profile text.
    """
    combined = ""
    data_dir = "data"

    if not os.path.isdir(data_dir):
        return combined

    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith(".md") and filename != "cv.md":
            filepath = os.path.join(data_dir, filename)
            combined += load_file(filepath) + "\\n\\n"

    return combined
