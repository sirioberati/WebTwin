#!/usr/bin/env fbpython
# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.

"""
Pure Python favicon (PNG) generator — no external dependencies.

Renders a 128x128 RGBA PNG from a small JSON spec describing the icon.
Uses only the Python stdlib (struct, zlib, json, math, argparse).

The renderer supports a small palette of primitives intentionally suited
to favicon-scale art: a background fill (solid or vertical gradient), an
optional rounded-square plate, and one or more shape layers stacked on
top — circle, ring, rounded-rectangle, polygon (regular n-gon), and a
single-character glyph drawn from a built-in 5x7 bitmap font.

Spec format (JSON):
{
  "size": 128,                              # optional, default 128
  "background": {
    "type": "solid" | "gradient",
    "color": "#1C1E21",                    # for solid
    "from": "#1C1E21", "to": "#0A0B0C"     # for gradient (top -> bottom)
  },
  "plate": {                                # optional rounded square plate
    "color": "#2A2D31",
    "radius": 24,
    "inset": 8
  },
  "layers": [
    {"type": "circle",  "cx": 64, "cy": 64, "r": 36, "color": "#FF6B35"},
    {"type": "ring",    "cx": 64, "cy": 64, "r": 36, "width": 6, "color": "#FFFFFF"},
    {"type": "rrect",   "x": 32, "y": 32, "w": 64, "h": 64, "radius": 12, "color": "#1877F2"},
    {"type": "polygon", "cx": 64, "cy": 64, "r": 40, "sides": 5, "rotation": -90, "color": "#FFD23F"},
    {"type": "glyph",   "char": "N", "cx": 64, "cy": 64, "scale": 8, "color": "#FFFFFF"}
  ]
}

Usage:
  python3 favicon_generator.py --spec spec.json --out favicon.png
  python3 favicon_generator.py --spec - --out favicon.png   # read JSON from stdin

Coordinate system: origin at top-left, +x right, +y down.
All coordinates are in pixels at the spec's `size`.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import sys
import zlib

# ---------------------------------------------------------------------------
# PNG encoding (RGBA, 8-bit)
# ---------------------------------------------------------------------------


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def encode_png_rgba(pixels: bytearray, width: int, height: int) -> bytes:
    """Encode an RGBA pixel buffer (row-major, 4 bytes/pixel) as a PNG."""
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)  # filter: None
        raw.extend(pixels[y * stride : (y + 1) * stride])
    idat = zlib.compress(bytes(raw), 9)
    return (
        sig
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", idat)
        + _png_chunk(b"IEND", b"")
    )


# ---------------------------------------------------------------------------
# Canvas with alpha blending
# ---------------------------------------------------------------------------


class Canvas:
    def __init__(self, size: int):
        self.size = size
        self.buf = bytearray(size * size * 4)  # transparent

    def _idx(self, x: int, y: int) -> int:
        return (y * self.size + x) * 4

    def put(self, x: int, y: int, r: int, g: int, b: int, a: int) -> None:
        if x < 0 or y < 0 or x >= self.size or y >= self.size or a == 0:
            return
        i = self._idx(x, y)
        dr, dg, db, da = self.buf[i], self.buf[i + 1], self.buf[i + 2], self.buf[i + 3]
        # source-over compositing on premultiplied math
        sa = a / 255.0
        inv = 1.0 - sa
        out_a = a + int(da * inv)
        if out_a == 0:
            return
        out_r = int((r * sa * 255 + dr * da * inv) / out_a)
        out_g = int((g * sa * 255 + dg * da * inv) / out_a)
        out_b = int((b * sa * 255 + db * da * inv) / out_a)
        self.buf[i] = max(0, min(255, out_r))
        self.buf[i + 1] = max(0, min(255, out_g))
        self.buf[i + 2] = max(0, min(255, out_b))
        self.buf[i + 3] = max(0, min(255, out_a))

    def to_png(self) -> bytes:
        return encode_png_rgba(self.buf, self.size, self.size)


# ---------------------------------------------------------------------------
# Color parsing
# ---------------------------------------------------------------------------


def parse_color(value):
    """Accept '#RRGGBB', '#RRGGBBAA', or [r,g,b] / [r,g,b,a]."""
    if isinstance(value, (list, tuple)):
        if len(value) == 3:
            r, g, b = value
            return int(r), int(g), int(b), 255
        r, g, b, a = value
        return int(r), int(g), int(b), int(a)
    if isinstance(value, str):
        s = value.lstrip("#")
        if len(s) == 6:
            return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255
        if len(s) == 8:
            return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), int(s[6:8], 16)
    raise ValueError(f"Unrecognized color: {value!r}")


# ---------------------------------------------------------------------------
# Coverage-based antialiasing helpers
# ---------------------------------------------------------------------------


def _coverage(distance: float) -> float:
    """Map a signed distance (in pixels) from an edge to an alpha coverage in [0, 1].

    distance < -0.5 -> fully inside (1.0)
    distance >  0.5 -> fully outside (0.0)
    """
    if distance <= -0.5:
        return 1.0
    if distance >= 0.5:
        return 0.0
    return 0.5 - distance


def fill_circle(canvas: Canvas, cx: float, cy: float, r: float, color):
    cr, cg, cb, ca = color
    x0 = max(0, int(math.floor(cx - r - 1)))
    x1 = min(canvas.size - 1, int(math.ceil(cx + r + 1)))
    y0 = max(0, int(math.floor(cy - r - 1)))
    y1 = min(canvas.size - 1, int(math.ceil(cy + r + 1)))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) - r
            cov = _coverage(d)
            if cov > 0:
                canvas.put(x, y, cr, cg, cb, int(ca * cov))


def fill_ring(
    canvas: Canvas, cx: float, cy: float, r_outer: float, width: float, color
):
    cr, cg, cb, ca = color
    r_inner = r_outer - width
    x0 = max(0, int(math.floor(cx - r_outer - 1)))
    x1 = min(canvas.size - 1, int(math.ceil(cx + r_outer + 1)))
    y0 = max(0, int(math.floor(cy - r_outer - 1)))
    y1 = min(canvas.size - 1, int(math.ceil(cy + r_outer + 1)))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            outer = _coverage(d - r_outer)
            inner = _coverage(r_inner - d)
            cov = min(outer, inner)
            if cov > 0:
                canvas.put(x, y, cr, cg, cb, int(ca * cov))


def fill_rrect(
    canvas: Canvas, x: float, y: float, w: float, h: float, radius: float, color
):
    cr, cg, cb, ca = color
    radius = max(0.0, min(radius, min(w, h) / 2.0))
    x0 = max(0, int(math.floor(x - 1)))
    x1 = min(canvas.size - 1, int(math.ceil(x + w + 1)))
    y0 = max(0, int(math.floor(y - 1)))
    y1 = min(canvas.size - 1, int(math.ceil(y + h + 1)))
    for py in range(y0, y1 + 1):
        for px in range(x0, x1 + 1):
            sx = px + 0.5
            sy = py + 0.5
            # distance to corner-rounded rect (signed)
            dx = max(x + radius - sx, sx - (x + w - radius), 0.0)
            dy = max(y + radius - sy, sy - (y + h - radius), 0.0)
            corner_dist = math.hypot(dx, dy) - radius
            # also clamp by axis-aligned outside
            outside_x = max(x - sx, sx - (x + w))
            outside_y = max(y - sy, sy - (y + h))
            if outside_x > 0 or outside_y > 0:
                d = max(corner_dist, outside_x, outside_y)
            else:
                d = corner_dist
            cov = _coverage(d)
            if cov > 0:
                canvas.put(px, py, cr, cg, cb, int(ca * cov))


def fill_polygon(canvas: Canvas, points, color):
    """Fill a convex/concave polygon using signed-distance estimate per pixel.

    Accurate for convex polygons (all our regular n-gons) and good enough
    for simple concave shapes at favicon resolutions.
    """
    cr, cg, cb, ca = color
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0 = max(0, int(math.floor(min(xs) - 1)))
    x1 = min(canvas.size - 1, int(math.ceil(max(xs) + 1)))
    y0 = max(0, int(math.floor(min(ys) - 1)))
    y1 = min(canvas.size - 1, int(math.ceil(max(ys) + 1)))
    n = len(points)
    for py in range(y0, y1 + 1):
        for px in range(x0, x1 + 1):
            sx = px + 0.5
            sy = py + 0.5
            inside = _point_in_polygon(sx, sy, points)
            min_d = float("inf")
            for i in range(n):
                ax, ay = points[i]
                bx, by = points[(i + 1) % n]
                min_d = min(min_d, _segment_distance(sx, sy, ax, ay, bx, by))
            d = -min_d if inside else min_d
            cov = _coverage(d)
            if cov > 0:
                canvas.put(px, py, cr, cg, cb, int(ca * cov))


def _point_in_polygon(x: float, y: float, points) -> bool:
    inside = False
    n = len(points)
    j = n - 1
    for i in range(n):
        xi, yi = points[i]
        xj, yj = points[j]
        if ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi
        ):
            inside = not inside
        j = i
    return inside


def _segment_distance(
    px: float, py: float, ax: float, ay: float, bx: float, by: float
) -> float:
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def regular_polygon_points(
    cx: float, cy: float, r: float, sides: int, rotation_deg: float = -90.0
):
    pts = []
    for i in range(sides):
        theta = math.radians(rotation_deg + i * 360.0 / sides)
        pts.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
    return pts


# ---------------------------------------------------------------------------
# 5x7 bitmap font (uppercase A-Z, 0-9, plus a few symbols).
# Each glyph is 5 columns x 7 rows, MSB = left.
# ---------------------------------------------------------------------------

FONT_5x7 = {
    "A": [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "B": [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    "C": [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
    "D": [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
    "E": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
    "F": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    "G": [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0E],
    "H": [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "I": [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "J": [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
    "K": [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    "L": [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    "M": [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
    "N": [0x11, 0x11, 0x19, 0x15, 0x13, 0x11, 0x11],
    "O": [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "P": [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    "Q": [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
    "R": [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    "S": [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
    "T": [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    "U": [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "V": [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    "W": [0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A],
    "X": [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
    "Y": [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
    "Z": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    "0": [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
    "1": [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "2": [0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F],
    "3": [0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E],
    "4": [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
    "5": [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    "6": [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
    "7": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    "8": [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
    "9": [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
    "?": [0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04],
    "!": [0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04],
    "+": [0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00],
    "-": [0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00],
    ".": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04],
}


def draw_glyph(canvas: Canvas, char: str, cx: float, cy: float, scale: int, color):
    glyph = FONT_5x7.get(char.upper())
    if glyph is None:
        return
    w = 5 * scale
    h = 7 * scale
    x0 = int(round(cx - w / 2.0))
    y0 = int(round(cy - h / 2.0))
    cr, cg, cb, ca = color
    for row, bits in enumerate(glyph):
        for col in range(5):
            if bits & (1 << (4 - col)):
                # filled cell -> rounded square block for slight softening
                px = x0 + col * scale
                py = y0 + row * scale
                fill_rrect(
                    canvas,
                    px,
                    py,
                    scale,
                    scale,
                    max(0.0, scale * 0.15),
                    (cr, cg, cb, ca),
                )


# ---------------------------------------------------------------------------
# Spec rendering
# ---------------------------------------------------------------------------


def render_spec(spec: dict) -> bytes:
    size = int(spec.get("size", 128))
    canvas = Canvas(size)

    bg = spec.get("background")
    if bg:
        if bg.get("type") == "gradient":
            top = parse_color(bg["from"])
            bottom = parse_color(bg["to"])
            for y in range(size):
                t = y / max(1, size - 1)
                r = int(top[0] + (bottom[0] - top[0]) * t)
                g = int(top[1] + (bottom[1] - top[1]) * t)
                b = int(top[2] + (bottom[2] - top[2]) * t)
                a = int(top[3] + (bottom[3] - top[3]) * t)
                for x in range(size):
                    canvas.put(x, y, r, g, b, a)
        else:
            r, g, b, a = parse_color(bg.get("color", "#1C1E21"))
            for y in range(size):
                for x in range(size):
                    canvas.put(x, y, r, g, b, a)

    plate = spec.get("plate")
    if plate:
        inset = float(plate.get("inset", 8))
        radius = float(plate.get("radius", 24))
        color = parse_color(plate.get("color", "#2A2D31"))
        fill_rrect(
            canvas, inset, inset, size - 2 * inset, size - 2 * inset, radius, color
        )

    for layer in spec.get("layers", []):
        kind = layer.get("type")
        color = parse_color(layer.get("color", "#FFFFFF"))
        if kind == "circle":
            fill_circle(
                canvas, float(layer["cx"]), float(layer["cy"]), float(layer["r"]), color
            )
        elif kind == "ring":
            fill_ring(
                canvas,
                float(layer["cx"]),
                float(layer["cy"]),
                float(layer["r"]),
                float(layer.get("width", 4)),
                color,
            )
        elif kind == "rrect":
            fill_rrect(
                canvas,
                float(layer["x"]),
                float(layer["y"]),
                float(layer["w"]),
                float(layer["h"]),
                float(layer.get("radius", 0)),
                color,
            )
        elif kind == "polygon":
            pts = regular_polygon_points(
                float(layer["cx"]),
                float(layer["cy"]),
                float(layer["r"]),
                int(layer["sides"]),
                float(layer.get("rotation", -90)),
            )
            fill_polygon(canvas, pts, color)
        elif kind == "points":
            fill_polygon(
                canvas, [(float(p[0]), float(p[1])) for p in layer["points"]], color
            )
        elif kind == "glyph":
            draw_glyph(
                canvas,
                str(layer["char"]),
                float(layer["cx"]),
                float(layer["cy"]),
                int(layer.get("scale", 8)),
                color,
            )
        else:
            print(f"warning: unknown layer type {kind!r}", file=sys.stderr)

    return canvas.to_png()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Generate a favicon PNG from a JSON spec.")
    p.add_argument("--spec", required=True, help="Path to spec JSON, or '-' for stdin.")
    p.add_argument("--out", required=True, help="Output PNG path.")
    args = p.parse_args(argv)

    if args.spec == "-":
        spec = json.load(sys.stdin)
    else:
        with open(args.spec, "r", encoding="utf-8") as f:
            spec = json.load(f)

    png = render_spec(spec)
    with open(args.out, "wb") as f:
        f.write(png)
    print(
        f"wrote {args.out} ({len(png)} bytes, {spec.get('size', 128)}x{spec.get('size', 128)})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
