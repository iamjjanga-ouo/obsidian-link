import {App, PluginSettingTab, Setting} from "obsidian";
import ObsidianLinkPlugin from "./main";

export interface ObsidianLinkSettings {
	targetUrl: string;
}

export const DEFAULT_SETTINGS: ObsidianLinkSettings = {
	targetUrl: 'https://go.obsidian-link.com'
}

export class ObsidianLinkSettingTab extends PluginSettingTab {
	plugin: ObsidianLinkPlugin;

	constructor(app: App, plugin: ObsidianLinkPlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const {containerEl} = this;

		containerEl.empty();

		new Setting(containerEl)
			.setName('Obsidian link settings')
			.setHeading();

		// Security warning about changing target URL
		new Setting(containerEl)
			.setName('⚠️ Security notice')
			.setDesc('Changing the target URL may expose you to security risks. Only use redirect services you trust. The default URL (go.obsidian-link.com) is recommended.')
			.setClass('obsidian-link-security-warning');

		new Setting(containerEl)
			.setName('Target URL')
			.setDesc('Base URL for the redirection service. Ensure your server redirects to the obsidian:// URI scheme.')
			.addText(text => text
				.setPlaceholder('https://go.obsidian-link.com')
				.setValue(this.plugin.settings.targetUrl)
				.onChange(async (value) => {
					// Normalize URL: remove trailing slash
					const normalizedUrl = value.trim().replace(/\/$/, '');

					// Basic URL validation
					try {
						if (normalizedUrl) {
							new URL(normalizedUrl);
						}
						this.plugin.settings.targetUrl = normalizedUrl || DEFAULT_SETTINGS.targetUrl;
						await this.plugin.saveSettings();
					} catch (error) {
						// If invalid URL, revert to previous value
						console.error('Invalid URL:', error);
					}
				}));
	}
}
