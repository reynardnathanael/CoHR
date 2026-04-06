# Preprocessing Module

This module handles resume cleaning and structuring.

## Responsibilities
- Text cleaning
- Section segmentation
- Normalization
- JSON conversion

## Input
Raw resume text (PDF/DOCX converted)

## Output
Structured JSON:
{
  "education": "...",
  "experience": "...",
  "skills": "..."
}

## Files
- cleaning.py → removes noise
- parsing.py → extracts sections
- pipeline.py → full pipeline