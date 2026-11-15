# Install Golden Gate in Codex

Golden Gate is maintained by Varaahgroup-llc and installs as a local Codex plugin. Each user installs it in their own Codex environment and uses their own destination-service authentication. There is no shared maintainer API key or separate Golden Gate account.

## Ask Codex to install

Paste this non-secret request into Codex:

> I want to use Golden Gate from https://github.com/Varaahgroup-llc/codex-golden-gate. Explain what it downloads and the local permissions it needs, then ask for my approval before downloading or installing it. If I approve, register its marketplace and install golden-gate@varaahgroup-golden-gate using the supported Codex commands. Preserve my existing configuration and stop if my account or organization policy blocks installation. Never ask me to paste an API key into chat.

After the user accepts, Codex can run:

```bash
codex plugin marketplace add Varaahgroup-llc/codex-golden-gate
codex plugin add golden-gate@varaahgroup-golden-gate
```

These commands were checked against the available Codex CLI's built-in help. Older or restricted clients may require installation from the plugin browser. Start a fresh local chat or restart the desktop client afterward.

Once the marketplace is registered, supported desktop clients may offer [the native install dialog](codex://plugins/install/golden-gate?marketplace=varaahgroup-golden-gate). This link does not register a marketplace on its own and is not an OpenAI directory listing.

## Use it

Tell Codex what you are configuring, without the value:

> Set up my payment API key for this project's local development.

> Save a new SERVICE_API_KEY for this repository's staging GitHub Actions environment.

Codex selects a destination from the request and relevant non-secret project context. If routing is ambiguous, it asks for the missing project/service/environment. The private form displays the exact destination and signed-in identity. Paste the key in that form, review it and click Save. Only a receipt is returned to the assistant.

The form uses the chat host's native MCP Apps surface. A modal is offered only when the host exposes the documented modal extension. Do not open the HTML file directly: it needs the MCP host bridge. A standalone webpage fallback is not included in v0.2.0. Existing Secret Bridge users should follow [MIGRATION.md](MIGRATION.md).

## Updates and removal

```bash
codex plugin marketplace upgrade varaahgroup-golden-gate
codex plugin list
codex plugin remove golden-gate@varaahgroup-golden-gate
```

Follow the installed client's update/enable prompts and restart if needed. Removing the plugin does not delete values already saved to a destination service.

## Limits

- Preview: macOS/Linux, Node.js 22+, local execution and MCP Apps UI support required.
- Signing into Codex does not grant GitHub/AWS/Azure write access. Use your own authorized provider login, then review the identity shown in the form.
- No silent installation, global account injection, forced updates, or policy bypass. Organization administrators may restrict plugins.
- Native directory publication and proactive suggestions are controlled by OpenAI. Repository distribution is available independently; see PUBLISHING.md.
