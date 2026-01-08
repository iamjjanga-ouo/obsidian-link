import {Notice, Plugin, TFile} from 'obsidian';
import {DEFAULT_SETTINGS, ObsidianLinkSettings, ObsidianLinkSettingTab} from "./settings";

export default class ObsidianLinkPlugin extends Plugin {
	settings: ObsidianLinkSettings;

	async onload() {
		await this.loadSettings();

		// Add command to copy Obsidian Link
		this.addCommand({
			id: 'copy-obsidian-link',
			name: 'Copy Link',
			callback: () => {
				void this.copyObsidianLink();
			}
		});

		// Add settings tab
		this.addSettingTab(new ObsidianLinkSettingTab(this.app, this));
	}

	onunload() {
		// Cleanup if needed
	}

	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData() as Partial<ObsidianLinkSettings>);
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}

	/**
	 * Generate Obsidian URI from active file
	 * Format: obsidian://open?vault=<vault-name>&file=<file-path>
	 */
	private generateObsidianUri(file: TFile): string {
		const vaultName = this.app.vault.getName();
		const filePath = file.path;

		// Security: Use encodeURIComponent() to prevent XSS/Injection attacks
		// This encoding ensures special characters (<, >, ", ', /, etc.) are safely escaped,
		// preventing malicious scripts from being injected into shared URLs
		const encodedVault = encodeURIComponent(vaultName);
		const encodedFile = encodeURIComponent(filePath);

		return `obsidian://open?vault=${encodedVault}&file=${encodedFile}`;
	}

	/**
	 * Transform Obsidian URI to HTTPS URL
	 * Formula: [Target URL] + [Query String of Obsidian URI]
	 *
	 * Security Note: Query string is already URL-encoded in generateObsidianUri(),
	 * so it's safe to concatenate directly without re-encoding.
	 */
	private transformToHttpsUrl(obsidianUri: string): string {
		const targetUrl = this.settings.targetUrl || DEFAULT_SETTINGS.targetUrl;

		// Extract query string from Obsidian URI
		const queryStringMatch = obsidianUri.match(/\?(.*)/);
		if (!queryStringMatch) {
			throw new Error('Invalid Obsidian URI format');
		}

		const queryString = queryStringMatch[1];

		// Extract path from Obsidian URI (e.g., "open" from "obsidian://open?...")
		const pathMatch = obsidianUri.match(/obsidian:\/\/([^?]+)/);
		const path = pathMatch ? pathMatch[1] : 'open';

		// Combine: Target URL + path + query string
		return `${targetUrl}/${path}?${queryString}`;
	}

	/**
	 * Copy Obsidian Link to clipboard
	 */
	async copyObsidianLink() {
		try {
			// Get active file
			const activeFile = this.app.workspace.getActiveFile();

			if (!activeFile) {
				new Notice('No active file found');
				return;
			}

			// Generate Obsidian URI
			const obsidianUri = this.generateObsidianUri(activeFile);

			// Transform to HTTPS URL
			const httpsUrl = this.transformToHttpsUrl(obsidianUri);

			// Copy to clipboard
			await navigator.clipboard.writeText(httpsUrl);

			// Show success notification
			new Notice('Obsidian Link copied to clipboard');

		} catch (error) {
			// Security: Avoid logging sensitive file paths or vault information in production
			console.error('Error copying Obsidian Link');
			new Notice('Failed to copy Obsidian Link');
		}
	}
}
