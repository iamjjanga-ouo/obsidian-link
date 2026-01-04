# Obsidian Link

Convert Obsidian's native `obsidian://` URIs to HTTPS redirect URLs for better compatibility with external platforms like Slack, Notion, and web forums.

## Overview

Many platforms (Slack, Notion, web forums) block or don't recognize Obsidian's custom `obsidian://` URI scheme. This plugin solves that problem by generating standard HTTPS URLs that redirect back to your Obsidian vault.

**How it works:**

1. Generates an `obsidian://` URI from your active file
2. Transforms it to an HTTPS URL using a configurable redirect service
3. Copies the shareable link to your clipboard

**Example transformation:**
```
Input:  obsidian://open?vault=my-vault&file=Project%2FMeeting
Output: https://go.obsidian-link.com/open?vault=my-vault&file=Project%2FMeeting
```

## Features

- **One-click link generation**: Use command palette to instantly copy shareable links
- **Customizable redirect URL**: Configure your own domain (e.g., using Cloudflare)
- **Cross-platform**: Works on both desktop and mobile
- **Proper URL encoding**: Handles special characters in vault and file names
- **Visual feedback**: Toast notifications confirm successful copy

## Installation

### From Obsidian Community Plugins (Coming Soon)

1. Open Settings → Community Plugins
2. Search for "Obsidian Link"
3. Click Install, then Enable

### Manual Installation

1. Download `main.js`, `manifest.json`, and `styles.css` from the [latest release](https://github.com/iamjjanga-ouo/obsidian-link/releases)
2. Create folder `VaultFolder/.obsidian/plugins/obsidian-link/`
3. Copy the downloaded files into this folder
4. Reload Obsidian and enable the plugin in Settings → Community Plugins

## Usage

### Copy Link to Active File

1. Open any note in Obsidian
2. Open Command Palette (`Cmd/Ctrl + P`)
3. Run command: **"Obsidian Link: Copy Link"**
4. The HTTPS redirect URL is now in your clipboard

### Configure Redirect Service

1. Go to Settings → Obsidian Link
2. Update the **Target URL** field (default: `https://go.obsidian-link.com`)
3. The plugin will automatically normalize URLs (remove trailing slashes, validate format)

**Important:** The target URL server must be configured to redirect HTTPS requests back to `obsidian://` URIs. See [Backend Setup](#backend-setup) below.

## Backend Setup

The plugin generates HTTPS URLs, but you need a redirect service to make them work. Here's how to set one up using Cloudflare:

### Using Cloudflare Single Redirects

1. Go to your Cloudflare Dashboard → Rules → Redirect Rules
2. Create a new Single Redirect with:
   - **When incoming requests match:** `(http.request.full_uri contains "vault=")`
   - **Then:** Dynamic
   - **Expression:** `regex_replace(http.request.full_uri, "^https://", "obsidian://")`
   - **Status code:** 302
3. Save and deploy

This will redirect all requests like `https://your-domain.com/open?vault=...` to `obsidian://open?vault=...`

### Using Your Own Domain

Set up a custom domain in Cloudflare (or any redirect service), then update the plugin settings to use your domain instead of the default.

## Development

### Prerequisites

- Node.js v16 or higher
- npm or yarn

### Setup

```bash
# Clone the repository
git clone https://github.com/iamjjanga-ouo/obsidian-link.git
cd obsidian-link

# Install dependencies
npm install

# Start development mode (watch for changes)
npm run dev
```

### Testing

1. Build the plugin with `npm run dev`
2. Copy `main.js`, `manifest.json`, and `styles.css` to your test vault's `.obsidian/plugins/obsidian-link/` folder
3. Reload Obsidian and enable the plugin
4. Test the command palette command
5. Verify the clipboard contains the correct HTTPS URL
6. Test with various file paths (spaces, special characters, nested folders)

### Project Structure

```
src/
  ├── main.ts       # Plugin entry point, core logic
  └── settings.ts   # Settings interface and settings tab UI
manifest.json       # Plugin metadata
esbuild.config.mjs  # Build configuration
```

### Key Implementation Details

**URL Transformation Logic:**
- Parses vault name and file path from active file
- Builds Obsidian URI with proper URL encoding
- Appends query string to configurable target URL
- Formula: `[Target URL]/[Path]?[Query String]`

**Obsidian API Usage:**
- `this.app.workspace.getActiveFile()` - Get current active file
- `this.app.vault.getName()` - Get vault name for URI generation
- `navigator.clipboard.writeText()` - Copy to clipboard
- `new Notice()` - Show toast notifications
- `this.addCommand()` - Register command palette commands

### Code Quality

```bash
# Run ESLint
npm run lint

# Build for production
npm run build
```

## Release Process

1. Update `minAppVersion` in `manifest.json` if needed
2. Run version bump: `npm version patch|minor|major`
   - Auto-updates `manifest.json`, `package.json`, and `versions.json`
3. Build for production: `npm run build`
4. Create GitHub release with tag matching version number (no "v" prefix)
5. Upload `manifest.json`, `main.js`, `styles.css` as release assets
6. For community plugin submission, follow the [plugin guidelines](https://docs.obsidian.md/Plugins/Releasing/Plugin+guidelines)

## Troubleshooting

**"No active file found" error:**
- Make sure you have a note open in the editor
- The plugin requires an active file to generate a link

**Link doesn't open Obsidian:**
- Verify your redirect service is properly configured
- Check that the target URL in settings matches your redirect service domain
- Test the redirect service directly in a browser

**Special characters in file names:**
- The plugin automatically handles URL encoding
- If issues persist, try renaming files to avoid special characters

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

- [Report issues](https://github.com/iamjjanga-ouo/obsidian-link/issues)
- [Feature requests](https://github.com/iamjjanga-ouo/obsidian-link/issues)

## Credits

Developed by [iamjjanga](https://github.com/iamjjanga-ouo)

## API Documentation

For more information about the Obsidian Plugin API, see [https://docs.obsidian.md](https://docs.obsidian.md)
