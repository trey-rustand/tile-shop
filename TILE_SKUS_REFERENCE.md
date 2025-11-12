# Tile Shop SKU Reference Guide

This document contains all available tile SKUs for the Tile Shop AI Visualization API.

## Available Tile SKUs

| SKU | Name | Description |
|-----|------|-------------|
| TS-001 | Classic White | Clean white tiles with subtle grid pattern |
| TS-002 | Slate Gray | Dark gray slate tiles with modern aesthetic |
| TS-003 | Marble Elegance | Elegant marble pattern with gradient effect |
| TS-004 | Herringbone | Classic herringbone pattern in light gray |
| TS-005 | Subway Tile | Traditional subway tile pattern in soft blue-gray |
| TS-006 | Mosaic Blue | Vibrant blue mosaic tiles with geometric pattern |
| TS-007 | Cream Beige | Warm cream beige tiles with subtle texture |
| TS-008 | Charcoal Black | Deep charcoal black tiles with minimal pattern |
| TS-009 | Terracotta | Warm terracotta tiles with rustic appeal |
| TS-010 | Sage Green | Calming sage green tiles with natural look |
| TS-011 | Carrara Marble | Premium Carrara marble with elegant veining |
| TS-012 | Navy Blue | Rich navy blue tiles with sophisticated finish |
| TS-013 | Brick Red | Classic brick red tiles with traditional charm |
| TS-014 | Ivory | Soft ivory tiles with clean, bright appearance |
| TS-015 | Travertine | Natural travertine tiles with warm tones |

## Usage in API

When calling the `/api/apply-overlay` endpoint, use the SKU code and name as follows:

**Example Request:**
```json
{
  "tileSku": "TS-009",
  "tileName": "Terracotta",
  "image": "<base64_image_data_or_url>"
}
```

**Form Data Example:**
- `tileSku`: TS-009
- `tileName`: Terracotta
- `image`: <base64_image_data_or_url>

## Quick Reference List

For quick lookup, here are all SKUs in a simple list format:

- TS-001: Classic White
- TS-002: Slate Gray
- TS-003: Marble Elegance
- TS-004: Herringbone
- TS-005: Subway Tile
- TS-006: Mosaic Blue
- TS-007: Cream Beige
- TS-008: Charcoal Black
- TS-009: Terracotta
- TS-010: Sage Green
- TS-011: Carrara Marble
- TS-012: Navy Blue
- TS-013: Brick Red
- TS-014: Ivory
- TS-015: Travertine

## Notes

- All SKUs are case-sensitive (use uppercase: TS-XXX)
- SKU format: TS- followed by three digits (001-015)
- The tileName must match exactly as shown above
- Both tileSku and tileName are required parameters for the API

