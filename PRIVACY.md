# Privacy

Secret Bridge is open-source software maintained by Varaahgroup-llc. This document describes version 0.1.0's behavior.

The plugin executes on the user's computer. It has no operator-hosted backend, analytics, advertising, telemetry, user database, or secret storage service. The maintainers do not receive values entered in the form through the plugin's normal operation.

The form encrypts a value before submitting it through the MCP bridge. The local server decrypts it in process memory and writes it to the exact destination reviewed by the user. Destination names, provider identities and save receipts are visible to the chat host and assistant. Encrypted submissions may remain in the host's tool history. The host also renders the form and must be trusted.

Local dotenv destinations store plaintext on the user's disk. Cloud destinations receive the value through the user's installed provider CLI and existing authentication. GitHub, AWS, Azure, Codex and the operating system have their own policies and logging behavior. The plugin does not read the saved secret back.

Temporary in-memory form keys expire after five minutes and are discarded after saving or cancellation. Local atomic writes may leave private temporary files after an abrupt system or process crash. JavaScript memory, browser extensions, swap and compromised systems can expose data; encryption does not remove those risks.

GitHub downloads, releases and support interactions are governed by GitHub's policies. Never attach real secrets, full dotenv files, private form captures, or unredacted provider logs to a bug report. For security issues, use the private reporting process in SECURITY.md.

Changes to data handling require review, a changelog entry and an updated policy before release.
