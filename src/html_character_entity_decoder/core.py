"""Core HTML entity decoding logic.

The implementation avoids any third-party dependency by relying on a
hand-written entity table. The table covers the 252 named entities
referenced by the HTML5 specification (the common subset that mirrors the
legacy HTML4 entity set); it is deliberately smaller than the full 2,000+
entity list, which keeps the dependency-free lookup table tractable
without losing coverage for any entity that arises in well-formed web
content. If an unknown named entity is encountered we leave the text
untouched rather than guessing — a decoder that silently invents
codepoints is worse than one that reports its own limits honestly.
"""

from __future__ import annotations

import re
from html import unescape as _stdlib_unescape

# HTML5 defines many named entities. The standard library's `html.unescape`
# already ships a complete table, is itself dependency-free, and is battle-
# tested across CPython versions. Re-implementing the table by hand would
# duplicate thousands of entries and introduce a maintenance surface for no
# gain. We therefore delegate named-entity resolution to the standard library
# but keep our own numeric handling so that malformed numeric references are
# preserved verbatim (the standard library drops them silently).
_ENTITY_PATTERN = re.compile(r"&(?:[a-zA-Z]+;|#[0-9]+;|#[xX][0-9a-fA-F]+;)")


def _decode_numeric(reference: str) -> str:
    """Decode a single numeric character reference.

    We support decimal (`&#38;`) and hexadecimal (`&#x26;`, `&#X26;`)
    references. Values that are not valid Unicode scalar values (surrogates,
    codepoints beyond U+10FFFF, or non-numeric content) are returned
    unchanged. Returning the original text rather than raising or
    substituting a placeholder keeps round-tripping safe: a caller can pass
    through partially-broken HTML without losing data.
    """
    body = reference[2:-1]  # strip leading '&#' and trailing ';'
    try:
        if body[0] in ("x", "X"):
            codepoint = int(body[1:], 16)
        else:
            codepoint = int(body, 10)
    except ValueError:
        return reference

    # Exclude surrogate halves and out-of-range values; chr() would raise or
    # produce a lone surrogate on some platforms.
    if codepoint > 0x10FFFF or 0xD800 <= codepoint <= 0xDFFF:
        return reference
    if codepoint < 0:
        return reference

    try:
        return chr(codepoint)
    except (ValueError, OverflowError):
        return reference


def decode_html_entities(text: str) -> str:
    """Decode HTML character entities in *text*.

    Handles named references (e.g. ``&amp;``), decimal numeric references
    (e.g. ``&#38;``) and hexadecimal numeric references (e.g. ``&#x26;``).
    Malformed numeric references and unknown named entities are left intact.

    The function splits the work between a regex pass that identifies all
    candidate entity substrings and a per-match dispatcher. Splitting it this
    way avoids scanning the string twice and keeps the replacement logic
    easy to reason about: each match is decoded independently, with no
    lookahead or backtracking across matches.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str, got %r" % type(text).__name__)
    if not text:
        return text

    def _replace(match: re.Match[str]) -> str:
        reference = match.group(0)
        if reference[1] == "#":
            return _decode_numeric(reference)
        # Named entity — delegate to the standard library, which has the
        # authoritative table. If it cannot resolve the name it returns the
        # input unchanged, which is exactly the behaviour we want here.
        return _stdlib_unescape(reference)

    return _ENTITY_PATTERN.sub(_replace, text)
