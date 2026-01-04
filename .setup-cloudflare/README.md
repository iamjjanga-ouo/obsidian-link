# Cloudflare Setup Script

Cloudflare automation script for the Obsidian Link project.

## Features

1. **Add DNS CNAME Record**
   - Name: `go`
   - Type: CNAME
   - Content: `@` (root domain)
   - Proxy: Enabled
   - TTL: Auto

2. **Create Single Page Redirect Rule**
   - Rule name: `obsidian-web-link-redirect`
   - Match condition: `https://go.obsidian-link.com/open*`
   - Redirect target: `obsidian://open/${1}`
   - Status code: 302
   - Preserve query string: Enabled
   - Priority: First

## Requirements

- Python 3.8+
- uv (Python package manager)
- Cloudflare API Token (requires Zone:Edit permission)
- Cloudflare Zone ID

## Installation

```bash
# Install dependencies (already completed)
uv sync
```

## Usage

### 1. Set Environment Variables

```bash
export CF_API_TOKEN="your-cloudflare-api-token"
export CF_ZONE_ID="your-zone-id"
```

Or create a `.env` file:

```bash
# Copy .env.example
cp .env.example .env

# Edit .env file
# CF_API_TOKEN=your-cloudflare-api-token
# CF_ZONE_ID=your-zone-id
```

### 2. Run Script

```bash
# Run with uv
uv run python setup_cloudflare.py
```

Or

```bash
# Activate virtual environment and run
source .venv/bin/activate
python setup_cloudflare.py
```

## How to Create Cloudflare API Token

1. Log in to Cloudflare Dashboard
2. Go to My Profile > API Tokens
3. Click "Create Token"
4. Use "Edit zone DNS" template or create custom token
5. Required permissions:
   - Zone - Zone Settings - Read
   - Zone - DNS - Edit
   - Zone - Dynamic Redirect - Edit
6. Select the domain in Zone Resources
7. "Continue to summary" > "Create Token"

## How to Find Zone ID

1. Select domain in Cloudflare Dashboard
2. Check "Zone ID" in the "API" section on the right sidebar

## Testing

After setup, test with the following URL:

```
https://go.obsidian-link.com/open?vault=my-vault&file=test.md
```

Browser should redirect to:

```
obsidian://open?vault=my-vault&file=test.md
```

## Troubleshooting

### If DNS Record Already Exists

The script checks for existing records and skips if already present.

### If Redirect Rule Doesn't Work

1. Check rule in Cloudflare Dashboard > Rules > Redirect Rules
2. Verify rule is enabled
3. Verify rule priority is correct (First)
4. Wait for DNS propagation (up to 24 hours, usually a few minutes)

## Important Notes

- Never share your API Token
- `.env` file should be added to `.gitignore`
- DNS CNAME record points to root domain (`@`)
  - The original requirement was `https://github.com/iamjjanga-ouo/obsidian-link`, but CNAME only accepts hostnames, not URLs
  - If not using root domain redirect, modify the `content` value in `setup_cloudflare.py` to the appropriate hostname
  - For GitHub Pages, you can use `iamjjanga-ouo.github.io` instead of `@`

## Quick Run

```bash
# Use run.sh script (recommended)
./run.sh
```

This script automatically:
- Loads environment variables from `.env` file
- Checks and installs dependencies
- Runs setup_cloudflare.py
