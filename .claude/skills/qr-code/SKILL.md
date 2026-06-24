---
name: qr-code
description: >
  Generate QR codes locally without third-party services or dependencies.
  Uses a self-contained pure Python script (stdlib only). Data never leaves
  the machine. Supports PNG file output.
apply_to_user_prompt: 'qr.?code|generate.*qr|create.*qr|make.*qr|qr.*png'
---

# QR Code Generator

Generate QR codes locally using a pure Python script with zero external dependencies.
All data stays on the local machine — nothing is sent to any third-party service.

## When This Skill Activates

- User wants to generate a QR code for a URL, text, or any data
- User asks to create a scannable QR code image (PNG)

## How to Use

The QR generator script is at:
```
.claude/skills/qr-code/scripts/qr_generator.py
```

Run it with `python3` (macOS/Linux) or `python` (Windows).

### PNG File Output

Save the QR code as a PNG image file:

```bash
python3 .claude/skills/qr-code/scripts/qr_generator.py --png /tmp/qr_output.png "https://example.com"
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--png FILE` | Save as PNG to FILE | (required) |
| `--scale N` | PNG pixels per QR module | `10` |
| `--open` | Open the PNG in the OS default image viewer after saving | off |

## Workflow

1. Determine what the user wants to encode (URL, text, etc.)
2. Run the script via Bash tool with `--png <path> --open` to save as PNG and open it for scanning
3. Inform the user of the saved file path

## Limitations

- Supports QR versions 1-10 (up to ~271 characters)
- Only byte mode encoding (handles all UTF-8 text, URLs, etc.)

## Examples

Generate QR for a URL:
```bash
python3 .claude/skills/qr-code/scripts/qr_generator.py --png /tmp/link_qr.png --open "https://meta.com"
```

Generate QR for plain text:
```bash
python3 .claude/skills/qr-code/scripts/qr_generator.py --png /tmp/message_qr.png --open "Thank god it's Friday!"
```
