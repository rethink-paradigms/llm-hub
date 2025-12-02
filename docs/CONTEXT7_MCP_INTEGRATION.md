# Context7 MCP Server Integration Guide

## Overview

This guide explains how to configure and use the Context7 MCP (Model Context Protocol) server with Qoder IDE in the LLMHub project. Context7 provides up-to-date, version-specific documentation and code examples directly within your AI-assisted development workflow.

## What is Context7?

Context7 is an MCP server that fetches current library documentation and code examples from source repositories. It eliminates common issues like:

- ❌ Outdated code examples from old training data
- ❌ Hallucinated APIs that don't exist
- ❌ Generic answers for deprecated package versions

With Context7, you get:

- ✅ Up-to-date, version-specific documentation
- ✅ Working code examples from current library versions
- ✅ Accurate API references

## Prerequisites

- Qoder IDE (version 0.2.18 or higher)
- LLMHub project workspace
- Internet connection for remote MCP server
- (Optional) Context7 API key for enhanced features

## Quick Start

### Step 1: Set Up Environment Variable (Optional)

For enhanced features (higher rate limits, private repositories), add your Context7 API key:

1. Copy `.env.example` to `.env` if you haven't already:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and add your Context7 API key:
   ```bash
   CONTEXT7_API_KEY=your_api_key_here
   ```

3. Get your API key from [Context7 Dashboard](https://context7.com/dashboard)

**Note**: Context7 works without an API key, but with rate limits and public repositories only.

### Step 2: Verify MCP Configuration

The MCP configuration file has been created at `.qoder/mcp.json`. It contains:

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

### Step 3: Restart Qoder IDE

For the MCP configuration to take effect:

1. Save all your work
2. Close Qoder IDE
3. Reopen Qoder IDE
4. The Context7 MCP server will connect automatically

### Step 4: Test the Integration

Try using Context7 in your prompts by including "use context7":

**Example Prompt**:
```
Create a Python function that uses the requests library to fetch JSON data 
from an API with proper error handling. use context7
```

Context7 will fetch the latest documentation for the requests library and provide accurate, up-to-date examples.

## Configuration Details

### MCP Configuration File Location

- **File Path**: `.qoder/mcp.json`
- **Format**: JSON
- **Scope**: Project-specific (applies to this workspace only)

### Configuration Schema

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `mcpServers` | Object | Container for all MCP server definitions | Yes |
| `mcpServers.context7` | Object | Context7-specific configuration | Yes |
| `mcpServers.context7.url` | String | Remote MCP server endpoint | Yes |
| `mcpServers.context7.headers` | Object | HTTP headers for authentication | No |
| `mcpServers.context7.headers.CONTEXT7_API_KEY` | String | API key (from environment variable) | No |

### Environment Variables

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `CONTEXT7_API_KEY` | Authentication for Context7 service | No | (none) |

**Environment Variable Substitution**: The `${CONTEXT7_API_KEY}` syntax in the configuration file automatically reads from your `.env` file.

## Usage Guidelines

### When to Use Context7

Use Context7 when you need:

- Current library documentation
- Up-to-date code examples
- Version-specific API references
- Best practices for modern libraries
- Configuration steps for tools/frameworks

### How to Invoke Context7

Simply add "use context7" to your prompt:

```
Configure a FastAPI application with CORS middleware. use context7
```

### Auto-Invocation (Optional)

You can configure Qoder IDE to automatically use Context7 for code-related queries by adding a rule to your Qoder settings. Add this to your `.qoder/.windsurfrules` file (if it exists):

```
Always use context7 when I need code generation, setup or configuration steps, 
or library/API documentation. This means you should automatically use the Context7 
MCP tools to resolve library id and get library docs without me having to explicitly ask.
```

## API Key Management

### Getting an API Key

1. Visit [Context7 Dashboard](https://context7.com/dashboard)
2. Sign up or log in
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key to your `.env` file

### Benefits With API Key

- ✅ Higher rate limits (more requests per hour)
- ✅ Access to private repository documentation
- ✅ Priority support
- ✅ Advanced features

### Without API Key

- ✅ Basic functionality works
- ⚠️ Rate limiting applies
- ⚠️ Public repositories only

### Security Best Practices

- ✅ Store API key in `.env` file only
- ✅ Never commit `.env` to version control (already in `.gitignore`)
- ✅ Use HTTPS for all communications (automatic with remote server)
- ✅ Rotate API keys periodically
- ❌ Never hardcode API keys in configuration files
- ❌ Never share API keys in public channels

## Troubleshooting

### Context7 Not Responding

**Issue**: Context7 doesn't return documentation when invoked

**Solutions**:
1. Check your internet connection
2. Verify `.qoder/mcp.json` file exists and is valid JSON
3. Restart Qoder IDE
4. Check Qoder IDE MCP server status

### Invalid API Key Error

**Issue**: Authentication fails with API key

**Solutions**:
1. Verify `CONTEXT7_API_KEY` is set in `.env`
2. Check for extra spaces or quotes in the API key
3. Regenerate API key from Context7 Dashboard
4. Ensure `.env` file is in the workspace root directory

### Rate Limit Exceeded

**Issue**: "Rate limit exceeded" error

**Solutions**:
1. Get an API key for higher limits
2. Wait for rate limit to reset (typically hourly)
3. Reduce frequency of Context7 requests

### MCP Server Connection Failed

**Issue**: Cannot connect to Context7 server

**Solutions**:
1. Check internet connectivity
2. Verify firewall/proxy settings
3. Test access to `https://mcp.context7.com/mcp`
4. Check Qoder IDE logs for detailed error messages

### Environment Variable Not Loaded

**Issue**: API key from `.env` not being used

**Solutions**:
1. Ensure `.env` file is in workspace root
2. Verify variable name is exactly `CONTEXT7_API_KEY`
3. Restart Qoder IDE after modifying `.env`
4. Check that `.env` file has no syntax errors

## Advanced Configuration

### Multiple MCP Servers

You can add additional MCP servers to `.qoder/mcp.json`:

```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
      }
    },
    "another-mcp-server": {
      "url": "https://example.com/mcp",
      "headers": {}
    }
  }
}
```

### Local Server Option (Future)

While the current setup uses a remote server, Context7 also supports local installation via npx:

```bash
npx -y @upstash/context7-mcp --api-key YOUR_API_KEY
```

To configure local server in the future, modify `.qoder/mcp.json`:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp", "--api-key", "${CONTEXT7_API_KEY}"]
    }
  }
}
```

### Connection Timeout Configuration

If you experience timeout issues, you may need to adjust Qoder IDE's timeout settings (refer to Qoder IDE documentation).

## Examples

### Example 1: Python Requests Library

**Prompt**:
```
Write a Python function to make a POST request with JSON data and handle timeouts. use context7
```

**Result**: Context7 fetches current `requests` library documentation and provides up-to-date examples.

### Example 2: FastAPI Configuration

**Prompt**:
```
Set up a FastAPI application with dependency injection for database connections. use context7
```

**Result**: Current FastAPI patterns and best practices.

### Example 3: React Hooks

**Prompt**:
```
Create a custom React hook for managing form state with validation. use context7
```

**Result**: Latest React hooks API and patterns.

## Support and Resources

### Official Documentation

- **Context7 Documentation**: [https://github.com/mcp/upstash/context7](https://github.com/mcp/upstash/context7)
- **Context7 Dashboard**: [https://context7.com/dashboard](https://context7.com/dashboard)
- **MCP Protocol**: Standard Model Context Protocol

### LLMHub Resources

- **Project README**: See main README.md for LLMHub overview
- **Environment Setup**: See .env.example for all configuration options
- **Issue Tracking**: Report issues via project issue tracker

### Getting Help

1. Check this documentation first
2. Review troubleshooting section
3. Check Context7 GitHub repository for known issues
4. Contact project maintainers for LLMHub-specific questions

## Frequently Asked Questions

### Q: Do I need an API key to use Context7?

**A**: No, Context7 works without an API key, but with rate limits and access to public repositories only. An API key provides higher limits and private repository access.

### Q: Will Context7 work offline?

**A**: No, the remote server configuration requires internet connectivity. For offline usage, consider the local server option (future enhancement).

### Q: How much does Context7 cost?

**A**: Check the [Context7 Dashboard](https://context7.com/dashboard) for current pricing. Basic usage may be free with rate limits.

### Q: Can I use Context7 with other projects?

**A**: Yes, Context7 can be configured for any project. The `.qoder/mcp.json` file is project-specific, so each project can have its own configuration.

### Q: What happens if Context7 is unavailable?

**A**: Qoder IDE will continue to function normally using the LLM's training data. Context7 is an enhancement, not a requirement.

### Q: How do I disable Context7?

**A**: Remove or rename `.qoder/mcp.json`, or remove the Context7 entry from the file, then restart Qoder IDE.

### Q: Can I use Context7 for private company libraries?

**A**: With an API key and proper permissions, Context7 can access private repositories. Contact Context7 support for enterprise features.

## Version History

### Version 1.0 (December 2024)

- Initial Context7 MCP integration
- Remote server configuration
- Environment-based API key management
- Basic documentation and troubleshooting guide

## Next Steps

After setting up Context7:

1. ✅ Test with a few prompts including "use context7"
2. ✅ Monitor usage and rate limits
3. ✅ Consider getting an API key for enhanced features
4. ✅ Set up auto-invocation rules if desired
5. ✅ Explore other MCP servers for additional capabilities

## Feedback

We welcome feedback on the Context7 integration:

- Report issues or suggest improvements
- Share successful use cases
- Contribute to documentation improvements

---

**Last Updated**: December 1, 2024  
**Maintained By**: LLMHub Project Team
