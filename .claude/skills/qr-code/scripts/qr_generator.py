#!/usr/bin/env python3
"""
Pure Python QR Code Generator — No external dependencies.

Uses only Python stdlib (struct, zlib). Implements QR code
specification (ISO 18004) for versions 1-25, EC levels L and M, byte mode.

Usage:
    python3 qr_generator.py "https://example.com"
    python3 qr_generator.py --png output.png "Hello, world!"
    python3 qr_generator.py --ec M "some text"
"""

import struct
import zlib

# ---------------------------------------------------------------------------
# QR code specification tables
# ---------------------------------------------------------------------------

# (version, ec_level) -> (total_codewords, ec_codewords_per_block, num_blocks_group1,
#                          data_cw_per_block_group1, num_blocks_group2, data_cw_per_block_group2)
QR_PARAMS = {
    (1, "L"): (26, 7, 1, 19, 0, 0),
    (1, "M"): (26, 10, 1, 16, 0, 0),
    (2, "L"): (44, 10, 1, 34, 0, 0),
    (2, "M"): (44, 16, 1, 28, 0, 0),
    (3, "L"): (70, 15, 1, 55, 0, 0),
    (3, "M"): (70, 26, 1, 44, 0, 0),
    (4, "L"): (100, 20, 1, 80, 0, 0),
    (4, "M"): (100, 18, 2, 32, 0, 0),
    (5, "L"): (134, 26, 1, 108, 0, 0),
    (5, "M"): (134, 24, 2, 43, 0, 0),
    (6, "L"): (172, 18, 2, 68, 0, 0),
    (6, "M"): (172, 16, 4, 27, 0, 0),
    (7, "L"): (196, 20, 2, 78, 0, 0),
    (7, "M"): (196, 18, 4, 31, 0, 0),
    (8, "L"): (242, 24, 2, 97, 0, 0),
    (8, "M"): (242, 22, 2, 38, 2, 39),
    (9, "L"): (292, 30, 2, 116, 0, 0),
    (9, "M"): (292, 22, 3, 36, 2, 37),
    (10, "L"): (346, 18, 2, 68, 2, 69),
    (10, "M"): (346, 26, 4, 43, 1, 44),
    (11, "L"): (404, 20, 4, 81, 0, 0),
    (11, "M"): (404, 30, 1, 50, 4, 51),
    (12, "L"): (466, 24, 2, 92, 2, 93),
    (12, "M"): (466, 22, 6, 36, 2, 37),
    (13, "L"): (532, 26, 4, 107, 0, 0),
    (13, "M"): (532, 22, 8, 37, 1, 38),
    (14, "L"): (581, 30, 3, 115, 1, 116),
    (14, "M"): (581, 24, 4, 40, 5, 41),
    (15, "L"): (655, 22, 5, 87, 1, 88),
    (15, "M"): (655, 24, 5, 41, 5, 42),
    (16, "L"): (733, 24, 5, 98, 1, 99),
    (16, "M"): (733, 28, 7, 45, 3, 46),
    (17, "L"): (815, 28, 1, 107, 5, 108),
    (17, "M"): (815, 28, 10, 46, 1, 47),
    (18, "L"): (901, 30, 5, 120, 1, 121),
    (18, "M"): (901, 26, 9, 43, 4, 44),
    (19, "L"): (991, 28, 3, 113, 4, 114),
    (19, "M"): (991, 26, 3, 44, 11, 45),
    (20, "L"): (1085, 28, 3, 107, 5, 108),
    (20, "M"): (1085, 26, 3, 41, 13, 42),
    (21, "L"): (1156, 28, 4, 116, 4, 117),
    (21, "M"): (1156, 26, 17, 42, 0, 0),
    (22, "L"): (1258, 28, 2, 111, 7, 112),
    (22, "M"): (1258, 28, 17, 46, 0, 0),
    (23, "L"): (1364, 30, 4, 121, 5, 122),
    (23, "M"): (1364, 28, 4, 47, 14, 48),
    (24, "L"): (1474, 30, 6, 117, 4, 118),
    (24, "M"): (1474, 28, 6, 45, 14, 46),
    (25, "L"): (1588, 26, 8, 106, 4, 107),
    (25, "M"): (1588, 28, 8, 47, 13, 48),
}

# Alignment pattern center positions per version
ALIGNMENT_POSITIONS = {
    2: [6, 18],
    3: [6, 22],
    4: [6, 26],
    5: [6, 30],
    6: [6, 34],
    7: [6, 22, 38],
    8: [6, 24, 42],
    9: [6, 26, 46],
    10: [6, 28, 50],
    11: [6, 30, 54],
    12: [6, 32, 58],
    13: [6, 34, 62],
    14: [6, 26, 46, 66],
    15: [6, 26, 48, 70],
    16: [6, 26, 50, 74],
    17: [6, 30, 54, 78],
    18: [6, 30, 56, 82],
    19: [6, 30, 58, 86],
    20: [6, 34, 62, 90],
    21: [6, 28, 50, 72, 94],
    22: [6, 26, 50, 74, 98],
    23: [6, 30, 54, 78, 102],
    24: [6, 28, 54, 80, 106],
    25: [6, 32, 58, 84, 110],
}

# Remainder bits per version (bits that don't fill a complete codeword)
REMAINDER_BITS = {
    1: 0,
    2: 7,
    3: 7,
    4: 7,
    5: 7,
    6: 7,
    7: 0,
    8: 0,
    9: 0,
    10: 0,
    11: 0,
    12: 0,
    13: 0,
    14: 3,
    15: 3,
    16: 3,
    17: 3,
    18: 3,
    19: 3,
    20: 3,
    21: 4,
    22: 4,
    23: 4,
    24: 4,
    25: 4,
}

# Format info strings (15 bits each) for mask pattern 0-7
# Index: ec_level_bits << 3 | mask_pattern
# EC level indicator: L=01, M=00
FORMAT_INFO = {}  # populated below

# ---------------------------------------------------------------------------
# GF(256) arithmetic for Reed-Solomon
# ---------------------------------------------------------------------------

GF_EXP = [0] * 512
GF_LOG = [0] * 256


def _init_gf():
    """Initialize GF(256) exp and log tables with primitive polynomial 0x11D."""
    x = 1
    for i in range(255):
        GF_EXP[i] = x
        GF_LOG[x] = i
        x <<= 1
        if x >= 256:
            x ^= 0x11D
    for i in range(255, 512):
        GF_EXP[i] = GF_EXP[i - 255]


_init_gf()


def gf_mul(a, b):
    if a == 0 or b == 0:
        return 0
    return GF_EXP[GF_LOG[a] + GF_LOG[b]]


def gf_poly_mul(p, q):
    """Multiply two polynomials in GF(256)."""
    r = [0] * (len(p) + len(q) - 1)
    for i, pi in enumerate(p):
        for j, qj in enumerate(q):
            r[i + j] ^= gf_mul(pi, qj)
    return r


def rs_generator_poly(nsym):
    """Build Reed-Solomon generator polynomial for nsym error correction symbols."""
    g = [1]
    for i in range(nsym):
        g = gf_poly_mul(g, [1, GF_EXP[i]])
    return g


def rs_encode(data, nsym):
    """Encode data with Reed-Solomon, returning nsym EC codewords."""
    gen = rs_generator_poly(nsym)
    # Pad data with nsym zeros
    msg = list(data) + [0] * nsym
    for i in range(len(data)):
        coef = msg[i]
        if coef != 0:
            for j in range(len(gen)):
                msg[i + j] ^= gf_mul(gen[j], coef)
    return msg[len(data) :]


# ---------------------------------------------------------------------------
# Format information encoding (BCH)
# ---------------------------------------------------------------------------


def _encode_format_info(data_bits):
    """Encode 5-bit format info with BCH(15,5) and XOR mask."""
    # Generator polynomial for BCH(15,5): x^10 + x^8 + x^5 + x^4 + x^2 + x + 1 = 0x537
    g = 0x537
    fmt = data_bits << 10
    # Polynomial division
    for i in range(4, -1, -1):
        if fmt & (1 << (i + 10)):
            fmt ^= g << i
    fmt = (data_bits << 10) | fmt
    # XOR with mask pattern 101010000010010
    fmt ^= 0x5412
    return fmt


def _init_format_info():
    """Pre-compute all format info bit strings."""
    ec_indicators = {"L": 0b01, "M": 0b00}
    for ec_name, ec_bits in ec_indicators.items():
        for mask in range(8):
            data = (ec_bits << 3) | mask
            FORMAT_INFO[(ec_name, mask)] = _encode_format_info(data)


_init_format_info()


def _encode_version_info(version):
    """Encode 6-bit version info with BCH(18,6). Only for version >= 7."""
    g = 0x1F25  # Generator polynomial for BCH(18,6)
    info = version << 12
    for i in range(5, -1, -1):
        if info & (1 << (i + 12)):
            info ^= g << i
    return (version << 12) | info


# ---------------------------------------------------------------------------
# QR data encoding (byte mode)
# ---------------------------------------------------------------------------


def _select_version(data_len, ec_level):
    """Select the smallest QR version that fits the data."""
    for v in range(1, 26):
        params = QR_PARAMS.get((v, ec_level))
        if params is None:
            continue
        total_cw, ec_per_block, nb1, dcw1, nb2, dcw2 = params
        data_capacity = nb1 * dcw1 + nb2 * dcw2
        # 4 bits mode + char count bits + data
        char_count_bits = 8 if v <= 9 else 16
        overhead_bits = 4 + char_count_bits
        available_bits = data_capacity * 8
        if overhead_bits + data_len * 8 <= available_bits:
            return v
    return None


def _encode_data(data_bytes, version, ec_level):
    """Encode data into QR codewords (data + EC) with interleaving."""
    params = QR_PARAMS[(version, ec_level)]
    total_cw, ec_per_block, nb1, dcw1, nb2, dcw2 = params
    data_capacity = nb1 * dcw1 + nb2 * dcw2

    # Build bit stream
    bits = []

    def add_bits(val, length):
        for i in range(length - 1, -1, -1):
            bits.append((val >> i) & 1)

    # Mode indicator: 0100 = byte mode
    add_bits(0b0100, 4)
    # Character count
    char_count_bits = 8 if version <= 9 else 16
    add_bits(len(data_bytes), char_count_bits)
    # Data
    for b in data_bytes:
        add_bits(b, 8)
    # Terminator (up to 4 zeros)
    remaining = data_capacity * 8 - len(bits)
    term_len = min(4, remaining)
    add_bits(0, term_len)
    # Pad to byte boundary
    while len(bits) % 8 != 0:
        bits.append(0)
    # Pad bytes to fill capacity
    pad_bytes = [0b11101100, 0b00010001]
    pad_idx = 0
    while len(bits) < data_capacity * 8:
        add_bits(pad_bytes[pad_idx], 8)
        pad_idx = 1 - pad_idx

    # Convert bits to bytes
    data_codewords = []
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        data_codewords.append(byte)

    # Split into blocks and generate EC
    blocks_data = []
    blocks_ec = []
    offset = 0
    for group_count, group_dcw in [(nb1, dcw1), (nb2, dcw2)]:
        for _ in range(group_count):
            block = data_codewords[offset : offset + group_dcw]
            offset += group_dcw
            blocks_data.append(block)
            blocks_ec.append(rs_encode(block, ec_per_block))

    # Interleave data codewords
    result = []
    max_data_len = max(len(b) for b in blocks_data)
    for i in range(max_data_len):
        for block in blocks_data:
            if i < len(block):
                result.append(block[i])

    # Interleave EC codewords
    for i in range(ec_per_block):
        for block in blocks_ec:
            if i < len(block):
                result.append(block[i])

    return result


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _get_bit(byte_val, bit_pos):
    """Extract a single bit from a byte value. Returns bool."""
    return bool((byte_val >> bit_pos) & 1)


# ---------------------------------------------------------------------------
# QR Code class — matrix construction, data placement, masking
# ---------------------------------------------------------------------------


class QrCode:
    """Generates a QR code matrix following the nayuki reference structure."""

    # Mask functions: (row, col) -> bool
    _MASK_FNS = [
        lambda y, x: (y + x) % 2 == 0,
        lambda y, x: y % 2 == 0,
        lambda y, x: x % 3 == 0,
        lambda y, x: (y + x) % 3 == 0,
        lambda y, x: (y // 2 + x // 3) % 2 == 0,
        lambda y, x: y * x % 2 + y * x % 3 == 0,
        lambda y, x: (y * x % 2 + y * x % 3) % 2 == 0,
        lambda y, x: ((y + x) % 2 + y * x % 3) % 2 == 0,
    ]

    def __init__(self, version, ec_level, codewords):
        self._version = version
        self._size = 17 + 4 * version
        self._ec_level = ec_level

        # The QR modules (True = dark, False = light)
        self._modules = [[False] * self._size for _ in range(self._size)]
        # Tracks which modules are function patterns (not data)
        self._isfunction = [[False] * self._size for _ in range(self._size)]

        # Step 1: Draw all function patterns
        self._draw_function_patterns()

        # Step 2: Place data codewords
        self._draw_codewords(codewords)

        # Step 3: Find and apply the best mask
        self._mask = self._apply_best_mask()

    def get_module(self, row, col):
        """Get the color of a module. True = dark, False = light."""
        return self._modules[row][col]

    @property
    def size(self):
        return self._size

    # -- Function pattern drawing --

    def _set_function_module(self, row, col, is_dark):
        """Set a module as a function pattern (won't be masked or overwritten by data)."""
        self._modules[row][col] = is_dark
        self._isfunction[row][col] = True

    def _draw_function_patterns(self):
        """Draw all function patterns and reserve format/version info areas."""
        size = self._size
        ver = self._version

        # Finder patterns (3 corners) + separators
        self._draw_finder_pattern(3, 3)
        self._draw_finder_pattern(3, size - 4)
        self._draw_finder_pattern(size - 4, 3)

        # Timing patterns
        for i in range(8, size - 8):
            self._set_function_module(6, i, i % 2 == 0)
            self._set_function_module(i, 6, i % 2 == 0)

        # Alignment patterns
        if ver in ALIGNMENT_POSITIONS:
            positions = ALIGNMENT_POSITIONS[ver]
            num_pos = len(positions)
            for ii in range(num_pos):
                for jj in range(num_pos):
                    # Skip positions that overlap with finder patterns
                    if (
                        (ii == 0 and jj == 0)
                        or (ii == 0 and jj == num_pos - 1)
                        or (ii == num_pos - 1 and jj == 0)
                    ):
                        continue
                    self._draw_alignment_pattern(positions[ii], positions[jj])

        # Reserve format info areas (will be overwritten later with real values)
        # Must be done here so data placement skips these cells
        self._draw_format_bits(self._ec_level, 0)  # Dummy mask=0, will be overwritten

        # Reserve version info areas
        self._draw_version_info()

    def _draw_finder_pattern(self, center_row, center_col):
        """Draw a 7x7 finder pattern centered at (center_row, center_col) with separator."""
        size = self._size
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                r = center_row + dy
                c = center_col + dx
                if 0 <= r < size and 0 <= c < size:
                    # Chebyshev distance from center determines the pattern
                    dist = max(abs(dy), abs(dx))
                    # dist 0 = center (dark)
                    # dist 1 = inner 3x3 block (dark)
                    # dist 2 = light ring
                    # dist 3 = outer border (dark)
                    # dist 4 = separator (light)
                    self._set_function_module(r, c, dist not in (2, 4))

    def _draw_alignment_pattern(self, center_row, center_col):
        """Draw a 5x5 alignment pattern centered at (center_row, center_col)."""
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                self._set_function_module(
                    center_row + dy, center_col + dx, max(abs(dy), abs(dx)) != 1
                )

    def _draw_format_bits(self, ec_level, mask):
        """Draw format information bits around the finder patterns."""
        info = FORMAT_INFO[(ec_level, mask)]
        size = self._size

        # Draw first copy around top-left finder
        # Bits 0-6 go down column 8 (rows 0-5, 7), bit 7 at (8,8)
        for i in range(6):
            self._set_function_module(i, 8, _get_bit(info, i))
        self._set_function_module(7, 8, _get_bit(info, 6))
        self._set_function_module(8, 8, _get_bit(info, 7))
        # Bit 8 at (8,7), bits 9-14 along row 8 (cols 5-0)
        self._set_function_module(8, 7, _get_bit(info, 8))
        for i in range(9, 15):
            self._set_function_module(8, 14 - i, _get_bit(info, i))

        # Draw second copy — bits 0-7 along row 8 (cols size-1..size-8),
        # bits 8-14 down column 8 (rows size-7..size-1)
        for i in range(8):
            self._set_function_module(8, size - 1 - i, _get_bit(info, i))
        for i in range(8, 15):
            self._set_function_module(size - 15 + i, 8, _get_bit(info, i))

        # Always-dark module beside bottom-left finder
        self._set_function_module(size - 8, 8, True)

    def _draw_version_info(self):
        """Draw version information for versions >= 7."""
        if self._version < 7:
            return
        info = _encode_version_info(self._version)
        size = self._size
        for i in range(18):
            bit = _get_bit(info, i)
            r = size - 11 + i % 3
            c = i // 3
            self._set_function_module(r, c, bit)
            self._set_function_module(c, r, bit)

    # -- Data placement --

    def _draw_codewords(self, data):
        """Place data bits into the matrix using the QR zigzag pattern.

        Follows nayuki's exact traversal: column pairs from right to left,
        alternating upward/downward, skipping column 6 (timing).
        """
        size = self._size
        i = 0  # Bit index into data
        total_bits = len(data) * 8

        # Traverse column pairs from right to left
        for right in range(size - 1, 0, -2):
            if right <= 6:
                right -= 1
            for vert in range(size):
                for j in range(2):
                    x = right - j  # Actual column
                    upward = ((right + 1) & 2) == 0
                    y = (size - 1 - vert) if upward else vert  # Actual row
                    if not self._isfunction[y][x] and i < total_bits:
                        self._modules[y][x] = _get_bit(data[i >> 3], 7 - (i & 7))
                        i += 1
        # All data bits must be placed
        assert i == total_bits, f"Placed {i} bits but expected {total_bits}"

    # -- Masking --

    def _apply_best_mask(self):
        """Try all 8 mask patterns and apply the one with the lowest penalty score."""
        best_mask = 0
        best_score = float("inf")

        for mask_idx in range(8):
            # Apply this mask
            self._apply_mask(mask_idx)
            # Draw format info for this mask
            self._draw_format_bits(self._ec_level, mask_idx)
            # Compute penalty
            score = self._get_penalty_score()
            # Undo this mask
            self._apply_mask(mask_idx)

            if score < best_score:
                best_score = score
                best_mask = mask_idx

        # Apply the best mask permanently
        self._apply_mask(best_mask)
        self._draw_format_bits(self._ec_level, best_mask)
        return best_mask

    def _apply_mask(self, mask_idx):
        """Toggle data modules according to the mask function (XOR, so self-inverse)."""
        mask_fn = self._MASK_FNS[mask_idx]
        for y in range(self._size):
            for x in range(self._size):
                if not self._isfunction[y][x] and mask_fn(y, x):
                    self._modules[y][x] = not self._modules[y][x]

    def _get_penalty_score(self):
        """Calculate the penalty score for the current module configuration."""
        size = self._size
        score = 0

        # Rule 1: Groups of 5+ same-color modules in a row/column
        for y in range(size):
            color = self._modules[y][0]
            run_len = 1
            for x in range(1, size):
                if self._modules[y][x] == color:
                    run_len += 1
                else:
                    if run_len >= 5:
                        score += run_len - 2
                    color = self._modules[y][x]
                    run_len = 1
            if run_len >= 5:
                score += run_len - 2

        for x in range(size):
            color = self._modules[0][x]
            run_len = 1
            for y in range(1, size):
                if self._modules[y][x] == color:
                    run_len += 1
                else:
                    if run_len >= 5:
                        score += run_len - 2
                    color = self._modules[y][x]
                    run_len = 1
            if run_len >= 5:
                score += run_len - 2

        # Rule 2: 2x2 blocks of same color
        for y in range(size - 1):
            for x in range(size - 1):
                c = self._modules[y][x]
                if (
                    c
                    == self._modules[y][x + 1]
                    == self._modules[y + 1][x]
                    == self._modules[y + 1][x + 1]
                ):
                    score += 3

        # Rule 3: Finder-like patterns (1011101 with 4 light on either side)
        for y in range(size):
            bits = self._modules[y]
            for x in range(size - 10):
                if (
                    bits[x + 0]
                    and not bits[x + 1]
                    and bits[x + 2]
                    and bits[x + 3]
                    and bits[x + 4]
                    and not bits[x + 5]
                    and bits[x + 6]
                    and not bits[x + 7]
                    and not bits[x + 8]
                    and not bits[x + 9]
                    and not bits[x + 10]
                ):
                    score += 40
                if (
                    not bits[x + 0]
                    and not bits[x + 1]
                    and not bits[x + 2]
                    and not bits[x + 3]
                    and bits[x + 4]
                    and not bits[x + 5]
                    and bits[x + 6]
                    and bits[x + 7]
                    and bits[x + 8]
                    and not bits[x + 9]
                    and bits[x + 10]
                ):
                    score += 40

        for x in range(size):
            for y in range(size - 10):
                if (
                    self._modules[y + 0][x]
                    and not self._modules[y + 1][x]
                    and self._modules[y + 2][x]
                    and self._modules[y + 3][x]
                    and self._modules[y + 4][x]
                    and not self._modules[y + 5][x]
                    and self._modules[y + 6][x]
                    and not self._modules[y + 7][x]
                    and not self._modules[y + 8][x]
                    and not self._modules[y + 9][x]
                    and not self._modules[y + 10][x]
                ):
                    score += 40
                if (
                    not self._modules[y + 0][x]
                    and not self._modules[y + 1][x]
                    and not self._modules[y + 2][x]
                    and not self._modules[y + 3][x]
                    and self._modules[y + 4][x]
                    and not self._modules[y + 5][x]
                    and self._modules[y + 6][x]
                    and self._modules[y + 7][x]
                    and self._modules[y + 8][x]
                    and not self._modules[y + 9][x]
                    and self._modules[y + 10][x]
                ):
                    score += 40

        # Rule 4: Dark/light ratio deviation from 50%
        total = size * size
        dark = sum(1 for y in range(size) for x in range(size) if self._modules[y][x])
        # Find the closest multiple of 5% above and below
        pct = dark * 100 // total
        prev5 = abs(pct - pct % 5 - 50) // 5
        next5 = abs(pct - pct % 5 + 5 - 50) // 5
        score += min(prev5, next5) * 10

        return score


# ---------------------------------------------------------------------------
# QR code generation (main)
# ---------------------------------------------------------------------------


def generate_qr(text, ec_level="L"):
    """Generate QR code matrix for given text.

    Args:
        text: String to encode
        ec_level: Error correction level ('L' or 'M')

    Returns:
        2D list of booleans (True=dark, False=light)
    """
    data_bytes = text.encode("utf-8")

    version = _select_version(len(data_bytes), ec_level)
    if version is None:
        raise ValueError(
            f"Data too long ({len(data_bytes)} bytes). "
            f"Max ~1273 bytes for version 25, EC level L."
        )

    # Encode data into codewords
    codewords = _encode_data(data_bytes, version, ec_level)

    # Build QR code
    qr = QrCode(version, ec_level, codewords)

    # Extract matrix
    return [[qr.get_module(r, c) for c in range(qr.size)] for r in range(qr.size)]


# ---------------------------------------------------------------------------
# Terminal (Unicode) renderer
# ---------------------------------------------------------------------------


def render_terminal(matrix, quiet_zone=2):
    """Render QR code to terminal using Unicode half-block characters.

    Uses two rows per character line:
      - Upper half block: top dark, bottom light
      - Lower half block: top light, bottom dark
      - Full block: both dark
      - Space: both light
    """
    size = len(matrix)
    total = size + quiet_zone * 2
    lines = []

    # Build padded matrix with quiet zone
    padded = []
    for _ in range(quiet_zone):
        padded.append([False] * total)
    for row in matrix:
        padded.append([False] * quiet_zone + row + [False] * quiet_zone)
    for _ in range(quiet_zone):
        padded.append([False] * total)

    # Ensure even number of rows
    if len(padded) % 2 != 0:
        padded.append([False] * total)

    for r in range(0, len(padded), 2):
        line = []
        for c in range(total):
            top = padded[r][c]
            bot = padded[r + 1][c] if r + 1 < len(padded) else False
            if top and bot:
                line.append("\u2588")  # Full block
            elif top and not bot:
                line.append("\u2580")  # Upper half block
            elif not top and bot:
                line.append("\u2584")  # Lower half block
            else:
                line.append(" ")
        lines.append("".join(line))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# PNG writer (pure Python, no PIL)
# ---------------------------------------------------------------------------


def _make_png_chunk(chunk_type, data):
    """Create a PNG chunk with CRC."""
    chunk = chunk_type + data
    crc = zlib.crc32(chunk) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk + struct.pack(">I", crc)


def write_png(matrix, filepath, scale=10, quiet_zone=2):
    """Write QR code as PNG file.

    Args:
        matrix: 2D list of booleans
        filepath: Output file path
        scale: Pixels per QR module
        quiet_zone: Number of quiet zone modules
    """
    size = len(matrix)
    total = size + quiet_zone * 2
    img_size = total * scale

    # PNG signature
    signature = b"\x89PNG\r\n\x1a\n"

    # IHDR: width, height, bit depth (8), color type (0=grayscale)
    ihdr_data = struct.pack(">IIBBBBB", img_size, img_size, 8, 0, 0, 0, 0)
    ihdr = _make_png_chunk(b"IHDR", ihdr_data)

    # IDAT: image data
    raw_rows = []
    for r in range(img_size):
        row_data = bytearray()
        row_data.append(0)  # Filter: None
        qr_r = r // scale - quiet_zone
        for c in range(img_size):
            qr_c = c // scale - quiet_zone
            if 0 <= qr_r < size and 0 <= qr_c < size and matrix[qr_r][qr_c]:
                row_data.append(0)  # Black
            else:
                row_data.append(255)  # White
        raw_rows.append(bytes(row_data))

    raw_data = b"".join(raw_rows)
    compressed = zlib.compress(raw_data, 9)
    idat = _make_png_chunk(b"IDAT", compressed)

    # IEND
    iend = _make_png_chunk(b"IEND", b"")

    with open(filepath, "wb") as f:
        f.write(signature + ihdr + idat + iend)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def open_file(filepath):
    """Open a file with the OS default viewer (cross-platform)."""
    import subprocess
    import sys

    if sys.platform == "darwin":
        subprocess.run(["open", filepath])
    elif sys.platform == "win32":
        subprocess.run(["start", "", filepath], shell=True)
    else:
        subprocess.run(["xdg-open", filepath])


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate QR codes locally (pure Python, no dependencies)"
    )
    parser.add_argument("text", help="Text or URL to encode")
    parser.add_argument("--png", metavar="FILE", help="Save as PNG file")
    parser.add_argument(
        "--ec",
        choices=["L", "M"],
        default="L",
        help="Error correction level (default: L)",
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=10,
        help="PNG scale factor (pixels per module, default: 10)",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the PNG in the OS default image viewer after saving",
    )

    args = parser.parse_args()

    matrix = generate_qr(args.text, ec_level=args.ec)

    if args.png:
        write_png(matrix, args.png, scale=args.scale)
        print(f"QR code saved to {args.png}")
        if args.open:
            open_file(args.png)
    else:
        print(render_terminal(matrix))


if __name__ == "__main__":
    main()
