"""Shared natural-sort utility for PDF and image file ordering."""

import re


def natural_sort_key(s: str) -> list[int | str]:
    """Return a key for natural sorting that handles numbers within text.

    Splits a string on digit boundaries so that numeric segments are compared
    as integers rather than lexicographically.

    Example:
        >>> sorted(["doc_1.pdf", "doc_10.pdf", "doc_2.pdf"], key=natural_sort_key)
        ['doc_1.pdf', 'doc_2.pdf', 'doc_10.pdf']
    """

    def _try_int(text: str) -> int | str:
        try:
            return int(text)
        except ValueError:
            return text.lower()

    return [_try_int(chunk) for chunk in re.split(r"(\d+)", s)]
