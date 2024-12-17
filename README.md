# Needle MCP server

An MCP server to manage documents and perform semantic search through Claude chat using Needle.

## Examples

### How we use the commands in Claudie Desktop

<img width="592" alt="Screenshot 2024-12-17 at 12 25 03 PM" src="https://github.com/user-attachments/assets/9e0ce522-6675-46d9-9bfb-3162d214625b" />

### What the results are in Needle

<img width="1336" alt="Screenshot 2024-12-17 at 12 25 50 PM" src="https://github.com/user-attachments/assets/0b1860e8-d074-4eec-857d-7d57746b5fb2" />

### Demo 

https://github.com/user-attachments/assets/0235e893-af96-4920-8364-1e86f73b3e6c


## Quick Setup

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
