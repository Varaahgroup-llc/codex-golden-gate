# Privacy

Golden Gate is open-source software maintained by Varaahgroup-llc. This document describes the prepared 0.2.0 rename version's behavior.

The plugin executes on the user's computer. It has no operator-hosted backend, analytics, advertising, telemetry, user database, or secret storage service. The maintainers do not receive values entered in the form through the plugin's normal operation.

The form encrypts a value before submitting it through the MCP bridge. The local server decrypts it in process memory and writes it to the exact destination reviewed by the user. Destination names, provider identities and save receipts are visible to the chat host and assistant. Encrypted submissions may remain in the host's tool history. The host also renders the form and must be trusted.

Local dotenv destinations store plaintext on the user's disk. Cloud destinations receive the value through the user's installed provider CLI and existing authentication. GitHub, AWS, Azure, Codex and the operating system have their own policies and logging behavior. The plugin does not read the saved secret back.

Temporary in-memory form keys expire after five minutes and are discarded after saving or cancellation. Local atomic writes may leave private temporary files after an abrupt system or process crash. JavaScript memory, browser extensions, swap and compromised systems can expose data; encryption does not remove those risks.

Request metadata and receipts remain in the local server's memory until later session cleanup or process exit; their deletion is not guaranteed at the five-minute key-expiry time. Host conversation/tool history and provider/CLI logs follow those services' retention settings. Saved dotenv files and cloud secrets remain at the selected destination until the user changes or deletes them through that destination. Cancelling a pending form clears that form's value and capability; it does not delete a value already saved. Stopping or uninstalling the plugin does not delete destination data or host history.

GitHub downloads, releases and support interactions are governed by GitHub's policies. Never attach real secrets, full dotenv files, private form captures, or unredacted provider logs to a bug report. For security issues, use the private reporting process in SECURITY.md.

Changes to data handling require review, a changelog entry and an updated policy before release.
