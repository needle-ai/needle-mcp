# Build Agents with Needle MCP Server

[![smithery badge](https://smithery.ai/badge/needle-mcp)](https://smithery.ai/server/needle-mcp)

![Screenshot of Feature - Claude](https://github.com/user-attachments/assets/a7286901-e7be-4efe-afd9-72021dce03d4)

MCP (Model Context Protocol) server to manage documents and perform searches using [Needle](https://needle.app) through Claude's Desktop Application.

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
- Perform powerful searches via Claude's large language model.
- Integrate seamlessly with the Needle ecosystem for advanced document management.

MCP (Model Context Protocol) standardizes the way LLMs connect to external data sources. You can use Needle MCP Server to easily enable semantic search tools in your AI applications, making data buried in PDFs, DOCX, XLSX, and other files instantly accessible by LLMs.

**We recommend using our remote MCP server** for the best experience - no local setup required.

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

### 1. Remote MCP Server (Recommended)

**Claude Desktop Config**

Create or update your config file:
- For MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- For Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "needle": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://mcp.needle.app/mcp",
        "--header",
        "Authorization:Bearer ${NEEDLE_API_KEY}"
      ],
      "env": {
        "NEEDLE_API_KEY": "<your-needle-api-key>"
      }
    }
  }
}
```

**Cursor Config**

Create or update `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "needle": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://mcp.needle.app/mcp",
        "--header",
        "Authorization:${NEEDLE_AUTH_HEADER}"
      ],
      "env": {
        "NEEDLE_AUTH_HEADER": "Bearer <your-needle-api-key>"
      }
    }
  }
}
```

Get your API key from [Needle Settings](https://needle.app).

We provide two endpoints:
- **Streamable HTTP**: `https://mcp.needle.app/mcp` (recommended)
- **SSE**: `https://mcp.needle.app/sse`

Note: MCP deprecated SSE endpoints in the latest specification, so newer clients should prefer the Streamable HTTP endpoint.

### 2. Local Installation

1. Clone the repository:
```bash
git clone https://github.com/needle-ai/needle-mcp.git
```

2. Install UV globally using Homebrew:
```bash
brew install uv
```

3. Create your config file:
   - For MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - For Windows: `%APPDATA%/Claude/claude_desktop_config.json`

**Claude Desktop Config**

```json
{
  "mcpServers": {
    "needle": {
      "command": "uv",
      "args": ["--directory", "/path/to/needle-mcp", "run", "needle-mcp"],
      "env": {
        "NEEDLE_API_KEY": "<your-needle-api-key>"
      }
    }
  }
}
```

**Cursor Config**

```json
{
  "mcpServers": {
    "needle": {
      "command": "uv",
      "args": ["--directory", "/path/to/needle-mcp", "run", "needle-mcp"],
      "env": {
        "NEEDLE_API_KEY": "<your-needle-api-key>"
      }
    }
  }
}
```

4. Replace `/path/to/needle-mcp` with your actual repository path
5. Add your Needle API key
6. Restart Claude Desktop

**Installing via Smithery**

```bash
npx -y @smithery/cli install needle-mcp --client claude
```

### 3. Docker Installation

1. Clone and build:
```bash
git clone https://github.com/needle-ai/needle-mcp.git
cd needle-mcp
docker build -t needle-mcp .
```

2. Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "needle": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "needle-mcp"],
      "env": {
        "NEEDLE_API_KEY": "<your-needle-api-key>"
      }
    }
  }
}
```

3. Restart Claude Desktop

## Usage Examples

* "Create a new collection called 'Technical Docs'"
* "Add this document to the collection, which is https://needle.app"
* "Search the collection for information about AI"
* "List all my collections"

## Troubleshooting

If not working:
- Make sure `uv` is installed globally (if not, uninstall with `pip uninstall uv` and reinstall with `brew install uv`)
- Or find `uv` path with `which uv` and replace `"command": "uv"` with the full path
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
    "needle": {
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
