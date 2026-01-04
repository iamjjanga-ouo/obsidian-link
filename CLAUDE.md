# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**obsidian-link** is an Obsidian plugin that converts native `obsidian://` URIs to HTTPS redirect URLs for better compatibility with platforms like Slack, Notion, and web forums that block or don't recognize the custom URI scheme.

**Core Functionality:**
- Generates `obsidian://` URIs from active vault files
- Transforms them to HTTPS URLs by appending query parameters to a configurable target domain
- Example transformation:
  - Input: `obsidian://open?vault=my-vault&file=Project%2FMeeting`
  - Output: `https://go.obsidian-link.com/open?vault=my-vault&file=Project%2FMeeting`

## Development Commands

```bash
# Install dependencies
npm i

# Development mode with auto-reload (watch mode)
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Version bump (after manually updating minAppVersion in manifest.json)
npm version patch   # or minor/major
```

## Architecture

### File Structure
- `src/main.ts` - Plugin entry point, command registration, core logic
- `src/settings.ts` - Settings interface and settings tab UI
- `manifest.json` - Plugin metadata (id, name, version, minAppVersion)
- `esbuild.config.mjs` - Build configuration using esbuild

### Key Components

**Plugin Lifecycle:**
1. `onload()` - Initialize plugin, load settings, register commands
2. `onunload()` - Cleanup when plugin is disabled
3. Settings are persisted via `loadSettings()` and `saveSettings()`

**Obsidian API Usage:**
- `this.app.workspace.getActiveFile()` - Get current active file
- `this.app.vault.getName()` - Get vault name for URI generation
- `navigator.clipboard.writeText()` - Copy transformed URL to clipboard
- `new Notice()` - Show toast notifications to user
- `this.addCommand()` - Register command palette commands
- `this.addRibbonIcon()` - Add optional ribbon icon (settings configurable)

### URL Transformation Logic

The plugin does NOT simply replace `obsidian://` with `https://`. Instead:

1. Parse vault name and file path from active file
2. Build Obsidian URI query string with proper URL encoding
3. Append query string to configurable target URL
4. Formula: `[Target URL] + [Query String of Obsidian URI]`

**Important:** The target URL server (e.g., Cloudflare) must be configured separately to redirect `https://[domain]/open?...` back to `obsidian://open?...`

### Settings Configuration

**MyPluginSettings Interface:**
- `targetUrl: string` - Base URL for redirect service
- Default: `https://go.obsidian-link.com`
- Must validate URL format and normalize (remove trailing slashes)

### Error Handling

Required error cases:
- No active file open → Show "No active file found" notice
- Empty or invalid target URL → Fallback to default or prompt user
- URI encoding must handle special characters in vault/file names

## Testing

**Manual Testing Workflow:**
1. Build plugin with `npm run dev`
2. Copy `main.js`, `manifest.json`, `styles.css` to test vault's `.obsidian/plugins/obsidian-link/`
3. Reload Obsidian and enable plugin in settings
4. Test command: "Obsidian Link: Copy Link" from command palette
5. Verify clipboard contains correct HTTPS URL
6. Test with various file paths (spaces, special chars, nested folders)
7. Test on both desktop and mobile (plugin is not desktop-only)

## Build Output

The build process (esbuild) compiles TypeScript to JavaScript:
- Input: `src/**/*.ts`
- Output: `main.js` (bundled)
- TypeScript config: ES6 target, strict null checks, isolated modules
- Base URL for imports: `src/`

## Release Process

1. Update `minAppVersion` in `manifest.json` if needed
2. Run `npm version patch|minor|major` (auto-updates manifest.json, package.json, versions.json)
3. Build production: `npm run build`
4. Create GitHub release with tag matching version number (no "v" prefix)
5. Upload `manifest.json`, `main.js`, `styles.css` as release assets
6. For community plugin submission, ensure README.md is complete and follow [plugin guidelines](https://docs.obsidian.md/Plugins/Releasing/Plugin+guidelines)

## API Documentation

Official Obsidian Plugin API: https://docs.obsidian.md
