"""
Utility functions for the QA Lab project.
"""

import os


def get_screenshot_path(screenshot_name: str) -> str:
    """Get the path to the screenshot for a given test name."""
    screenshots_dir = "screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    return os.path.join(screenshots_dir, screenshot_name)
