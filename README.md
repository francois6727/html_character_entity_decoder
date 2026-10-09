# HTML Character Entity Decoder

Decodes HTML character entities — named (`&amp;`), decimal numeric (`&#38;`) and hexadecimal numeric (`&#x26;`) — to their corresponding Unicode characters. Zero third-party dependencies; standard library only.

```python
from html_character_entity_decoder import decode_html_entities

assert decode_html_entities("&amp;&#65;&#x42;") == "&AB"
```

## Why this exists

The standard library's `html.unescape` handles named entities but silently drops malformed numeric references. This library fills that gap: numeric references that are not valid Unicode scalar values (surrogates, codepoints beyond U+10FFFF) are left intact so that partially-broken HTML survives a round trip without data loss. Named-entity resolution is delegated to `html.unescape`, which already carries the authoritative HTML5 entity table — re-implementing that table by hand would add thousands of lines for no benefit.

## Edge case you will hit

A reference like `&#xD800;` (a surrogate codepoint) is returned unchanged, not as a lone surrogate character. If you need to emit raw surrogates into a CESU-8 byte stream, decode *after* this function using your own logic — this library intentionally refuses to produce them.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

