"""Shared models and utilities for categorization modules."""

from .models import Category
from .report import generate_html_report

__all__ = ["Category", "generate_html_report"]
