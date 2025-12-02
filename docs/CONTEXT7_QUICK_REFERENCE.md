# Context7 MCP Quick Reference

## Quick Setup (2 minutes)

1. **Add API Key to .env** (optional but recommended)
   ```bash
   echo "CONTEXT7_API_KEY=your_key_here" >> .env
   ```
   Get key: https://context7.com/dashboard

2. **Verify Configuration**
   ```bash
   cat .qoder/mcp.json
   ```
   Should show Context7 server configured.

3. **Restart Qoder IDE**
   Close and reopen Qoder IDE to load MCP configuration.

4. **Test It**
   In a prompt, add "use context7":
   ```
   Create a Python requests function with error handling. use context7
   ```

## Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `.qoder/mcp.json` | MCP server configuration | Project root |
| `.env` | API key storage | Project root (not in git) |
| `.env.example` | Environment template | Project root (in git) |

## MCP Configuration (.qoder/mcp.json)

```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
      }
    }
  }
}
```

## Environment Variable (.env)

```bash
# MCP Server Configuration
CONTEXT7_API_KEY=your_api_key_here
```

## Usage

### With Explicit Invocation
Add "use context7" to any prompt:
```
Configure FastAPI with CORS middleware. use context7
```

### Auto-Invocation (Optional)
Add to `.qoder/.windsurfrules` (if using Windsurf) or equivalent:
```
Always use context7 when I need code generation, setup steps, 
or library documentation.
```

## Benefits

| Feature | Without API Key | With API Key |
|---------|----------------|--------------|
| Basic functionality | ✅ Yes | ✅ Yes |
| Rate limits | ⚠️ Low | ✅ High |
| Private repos | ❌ No | ✅ Yes |
| Priority support | ❌ No | ✅ Yes |

## Troubleshooting

### Context7 not responding?
- Check internet connection
- Verify `.qoder/mcp.json` exists
- Restart Qoder IDE
- Check MCP server status in IDE

### Invalid API key?
- Check `.env` for typos
- Ensure no extra spaces/quotes
- Regenerate key from dashboard
- Verify `.env` is in project root

### Rate limited?
- Get an API key for higher limits
- Wait for limit reset (hourly)
- Reduce request frequency

## More Information

Full documentation: [docs/CONTEXT7_MCP_INTEGRATION.md](CONTEXT7_MCP_INTEGRATION.md)

Context7 Docs: https://github.com/mcp/upstash/context7

Get API Key: https://context7.com/dashboard
