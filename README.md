# Landing page catalog

Evidence-backed landing page references for coding agents, independent of their harness.

## First 50 references

The first pass contains 50 recognizable brands across 12 industries, with 168 visually checked copy examples, archived full-page screenshots, opening-page crops, and searchable facets for audience, style, and intended action.

- Open [`datasets/first-50/review.html`](datasets/first-50/review.html) locally for the filterable visual gallery. Its image paths are relative; keep the dataset folder together.
- Use [`search-index.json`](datasets/first-50/search-index.json) for compact discovery, then load the matching [`packets/`](datasets/first-50/packets/) record for checked copy and image evidence.
- Use [`records/`](datasets/first-50/records/) for detailed records, including explicitly unreviewed OCR. [`reference-records.json`](datasets/first-50/reference-records.json) contains the same records as one array.
- See [`methodology.json`](datasets/first-50/methodology.json), [`coverage.json`](datasets/first-50/coverage.json), and [`selection-manifest.json`](datasets/first-50/selection-manifest.json) for scope, coverage, and provenance.

This is a partial first pass. Checked copy covers headlines, selected actions, and selected supporting text. Detailed body-section annotation remains pending. Full-page OCR is unreviewed and can contain errors, UI mockup text, legal copy, and logos. Intended actions describe visible requests such as signup or booking a demo; conversion performance is unknown. Brand prominence is an editorial selection, not a traffic ranking.

The first 1,000 screenshot pixels form a fixed evidence window, not an exact hero boundary or browser viewport. Mobile behavior, interactions, CSS values, source code, and screenshot capture dates are not established. Gallery download dates are recorded separately. This repository does not yet implement an MCP server.

## Validate

Run `python3 scripts/validate_dataset.py` from the repository root. The script uses the Python standard library and checks the schema keywords used by these records, hashes, image dimensions, evidence links, OCR bounds, portable paths, and gallery data. It does not assess transcription accuracy or render the gallery in a browser.
