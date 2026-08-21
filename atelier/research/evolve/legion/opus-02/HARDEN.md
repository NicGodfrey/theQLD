# Opus-02 · R4 download (conductor fill — agent slot full)

**Pass.** `GET /api/artifacts/:id` serves inline so `<img src>` renders. `?download=1` sets `Content-Disposition: attachment` with `ext_for_mime` (`.svg`/`.png`/…).

## Remaining
- Filename is the artifact hex, not the brief slug.
- No `HEAD` / Range.
- SVG served as `image/svg+xml` (correct); consider `X-Content-Type-Options: nosniff`.

## Suggested (unapplied)
Add `nosniff` on `_send_file`. Optional `download_name` from first 24 slug chars of `prompt`.
