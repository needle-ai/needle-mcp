# Build Agents with Needle MCP Server

[![smithery badge](https://smithery.ai/badge/needle-mcp)](https://smithery.ai/server/needle-mcp)

![Screenshot of Feature - Claude](https://github.com/user-attachments/assets/a7286901-e7be-4efe-afd9-72021dce03d4)

MCP (Model Context Protocol) server to manage documents and perform searches using [Needle](https://needle-ai.com) through Claude’s Desktop Application.

<a href="https://glama.ai/mcp/servers/5jw1t7hur2">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/5jw1t7hur2/badge" alt="Needle Server MCP server" />
</a>

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Usage](#usage)
  - [Commands in Claude Desktop](#commands-in-claude-desktop)
  - [Result in Needle](#result-in-needle)
- [Installation](#installation)
- [Video Explanation](#youtube-video-explanation)

---

## Overview

Needle MCP Server allows you to:

- Organize and store documents for quick retrieval.
- Perform powerful searches via Claude’s large language model.
- Integrate seamlessly with the Needle ecosystem for advanced document management.

---

## Features

- **Document Management:** Easily add and organize documents on the server.
- **Search & Retrieval:** Claude-based natural language search for quick answers.
- **Easy Integration:** Works with [Claude Desktop](#commands-in-claude-desktop) and Needle collections.

---

## Usage

### Commands in Claude Desktop

Below is an example of how the commands can be used in Claude Desktop to interact with the server:

![Using commands in Claude Desktop](https://github.com/user-attachments/assets/9e0ce522-6675-46d9-9bfb-3162d214625b)

1. **Open Claude Desktop** and connect to the Needle MCP Server.  
2. **Use simple text commands** to search, retrieve, or modify documents.  
3. **Review search results** returned by Claude in a user-friendly interface.

### Result in Needle

https://github.com/user-attachments/assets/0235e893-af96-4920-8364-1e86f73b3e6c

---

## Youtube Video Explanation

For a full walkthrough on using the Needle MCP Server with Claude and Claude Desktop, watch this [YouTube explanation video](https://youtu.be/nVrRYp9NZYg).

---

## Installation

### Installing via Smithery

To install Needle MCP for Claude Desktop automatically via [Smithery](https://smithery.ai/server/needle-mcp):

```bash
npx -y @smithery/cli install needle-mcp --client claude
```

### Manual Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/needle-mcp.git
```

2. Install UV globally using Homebrew in Terminal:
```bash
brew install uv
```

3. Create claude_desktop_config.json:
   - For MacOS: Open directory `~/Library/Application Support/Claude/` and create the file inside it
   - For Windows: Open directory `%APPDATA%/Claude/` and create the file inside it

4. Add this configuration to claude_desktop_config.json:
```json
{
  "mcpServers": {
    "needle_mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/needle-mcp",
        "run",
        "needle-mcp"
      ],
      "env": {
        "NEEDLE_API_KEY": "your_needle_api_key"
      }
    }
  }
}
```

5. Get your Needle API key from needle.xyz

6. Update the config file:
   - Replace `/path/to/needle-mcp` with your actual repository path
   - Add your Needle API key

7. Quit Claude completely and reopen it

## Usage Examples

* "Create a new collection called 'Technical Docs'"
* "Add this document to the collection, which is https://needle-ai.com"
* "Search the collection for information about AI"
* "List all my collections"

## Troubleshooting

If not working:
- Make sure UV is installed globally (if not, uninstall with `pip uninstall uv` and reinstall with `brew install uv`)
- Or find UV path with `which uv` and replace `"command": "uv"` with the full path
- Verify your Needle API key is correct
- Check if the needle-mcp path in config matches your actual repository location

### Reset Claude Desktop Configuration

If you're seeing old configurations or the integration isn't working:

1. Find all Claude Desktop config files:
```bash
find / -name "claude_desktop_config.json" 2>/dev/null
```

2. Remove all Claude Desktop data:
- On MacOS: `rm -rf ~/Library/Application\ Support/Claude/*`
- On Windows: Delete contents of `%APPDATA%/Claude/`

3. Create a fresh config with only Needle:
```
mkdir -p ~/Library/Application\ Support/Claude
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json
<< 'EOL'
{
  "mcpServers": {
    "needle_mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/needle-mcp",
        "run",
        "needle-mcp"
      ],
      "env": {
        "NEEDLE_API_KEY": "your_needle_api_key"
      }
    }
  }
}
EOL
```

4. Completely quit Claude Desktop (Command+Q on Mac) and relaunch it

5. If you still see old configurations:
- Check for additional config files in other locations
- Try clearing browser cache if using web version
- Verify the config file is being read from the correct location