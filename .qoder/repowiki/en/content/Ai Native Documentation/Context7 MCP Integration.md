# Context7 MCP Integration

<cite>
**Referenced Files in This Document**   
- [CONTEXT7_MCP_INTEGRATION.md](file://docs/CONTEXT7_MCP_INTEGRATION.md)
- [CONTEXT7_QUICK_REFERENCE.md](file://docs/CONTEXT7_QUICK_REFERENCE.md)
- [README.md](file://README.md)
- [.qoder/mcp.json](file://.qoder/mcp.json)
- [setup.py](file://packages/cli/src/llmhub_cli/commands/setup.py)
- [generator_hook.py](file://packages/cli/src/llmhub_cli/generator_hook.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Configuration Files](#configuration-files)
3. [Setup and Initialization](#setup-and-initialization)
4. [Usage Guidelines](#usage-guidelines)
5. [API Key Management](#api-key-management)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)
8. [Examples](#examples)
9. [Support and Resources](#support-and-resources)
10. [Frequently Asked Questions](#frequently-asked-questions)

## Introduction

The Context7 MCP (Model Context Protocol) server integration enhances the LLM Hub development experience by providing up-to-date, version-specific documentation and code examples directly within Qoder IDE. This integration eliminates common issues such as outdated code examples, hallucinated APIs, and generic answers for deprecated package versions by fetching current library documentation from source repositories.

Context7 operates as an MCP server that connects to Qoder IDE through a configuration file, enabling developers to access accurate API references and best practices for modern libraries. The integration supports both explicit and automatic invocation, making it seamless to retrieve documentation during code generation, setup, or configuration tasks.

The system is designed to work with minimal setup, requiring only the configuration of environment variables and IDE restart to become operational. It supports both public and private repository access, with enhanced features available through API key authentication.

**Section sources**
- [README.md](file://README.md#L148-L157)
- [CONTEXT7_MCP_INTEGRATION.md](file://docs/CONTEXT7_MCP_INTEGRATION.md#L1-L27)

## Configuration Files

The Context7 MCP integration relies on two primary configuration files that work together to establish the connection between Qoder IDE and the Context7 server.

### MCP Configuration File

The `.qoder/mcp.json` file contains the server configuration for the MCP integration. This JSON file specifies the remote server endpoint and authentication headers:

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

The configuration includes the server URL and uses environment variable substitution (`${CONTEXT7_API_KEY}`) to securely pass the API key without hardcoding it in the configuration file.

### Environment Variables

The `.env` file stores the Context7 API key as an environment variable. This approach follows security best practices by keeping sensitive credentials out of version control:

```bash
CONTEXT7_API_KEY=your_api_key_here
```

The `.env.example` file serves as a template for developers to create their own `.env` file with the required environment variables.

**Diagram sources**
- [.qoder/mcp.json](file://.qoder/mcp.json)
- [.env](file://.env)

**Section sources**
- [CONTEXT7_MCP_INTEGRATION.md](file://docs/CONTEXT7_MCP_INTEGRATION.md#L88-L111)
- [CONTEXT7_QUICK_REFERENCE.md](file://docs/CONTEXT7_QUICK_REFERENCE.md#L28-L54)

## Setup and Initialization

### Quick Start

The integration can be set up in four simple steps:

1. **Set Up Environment Variable**: Add the Context7 API key to the `.env` file (optional but recommended for enhanced features)
2. **Verify MCP Configuration**: Confirm that the `.qoder/mcp.json` file exists and contains the correct server configuration
3. **Restart Qoder IDE**: Close and reopen the IDE to load the MCP configuration
4. **Test the Integration**: Use a prompt with "use context7" to verify the connection

The `llmhub setup` command automatically creates the necessary configuration files, including the MCP server configuration in the `.qoder` directory.

### Environment Setup

The initialization process begins with copying the `.env.example` file to `.env` and adding the Context7 API key. This can be done manually or through command-line operations. The system is designed to work without an API key, but with rate limits and access restricted to public repositories only.

**Section sources**
- [CONTEXT7_MCP_INTEGRATION.md](file://docs/CONTEXT7_MCP_INTEGRATION.md#L28-L73)
- [setup.py](file://packages/cli/src/llmhub_cli/commands/setup.py#L34-L42)

## Usage Guidelines

### When to Use Context7

Context7 should be used when developers need:
- Current library documentation
- Up-to-date code examples
- Version-specific API references
- Best practices for modern libraries
- Configuration steps for tools and frameworks

### How to Invoke Context7

The integration can be invoked in two ways:

#### Explicit Invocation
Add "use context7" to any prompt to explicitly request documentation:

```
Create a Python function that uses the requests library to fetch JSON data from an API with proper error handling. use context7
```

#### Auto-Invocation (Optional)
Configure Qoder IDE to automatically use Context7 for code-related queries by adding a rule to the `.qoder/.windsurfrules` file:

```
Always use context7 when I need code generation, setup or configuration steps, 
or library/API documentation. This means you should automatically use the Context7 
MCP tools to resolve library id and get library docs without me having to explicitly ask.
```

**Section sources**
- [CONTEXT7_MCP_INTEGRATION.md](file://docs/CONTEXT7_MCP_INTEGRATION.md#L114-L140)

## API Key Management

### Getting an API Key

To obtain an API key:
1. Visit the [Context7 Dashboard](https://context7.com/dashboard)
2. Sign up or log in
3. Navigate to the API Keys section
4. Generate a new API key
5. Copy the key to the `.env` file

### Benefits With API Key

Using an API key provides several advantages:
- Higher rate limits (more requests per hour)
- Access to private repository documentation
- Priority support
- Advanced features

### Security Best Practices

To ensure secure API key management:
- Store the API key in the `.env` file only
- Never commit `.env` to version control (already in `.gitignore`)
- Use HTTPS for all communications (automatic with remote server)
- Rotate API keys periodically
- Never hardcode API keys in configuration files
- Never share API keys in public channels

**Section sources**
- [CONTEXT7_MCP_INTEGRATION.md](file://docs/CONTEXT7_MCP_INTEGRATION.md#L143-L172)

## Troubleshooting

### Common Issues and Solutions

#### Context7 Not Responding
**Issue**: Context7 doesn't return documentation when invoked
**Solutions**:
1. Check internet connection
2. Verify `.qoder/mcp.json` file exists and is valid JSON
3. Restart Qoder IDE
4. Check Qoder IDE MCP server status

#### Invalid API Key Error
**Issue**: Authentication fails with API key
**Solutions**:
1. Verify `CONTEXT7_API_KEY` is set in `.env`
2. Check for extra spaces or quotes in the API key
3. Regenerate API key from Context7 Dashboard
4. Ensure `.env` file is in the workspace root directory

#### Rate Limit Exceeded
**Issue**: "Rate limit exceeded" error
**Solutions**:
1. Get an API key for higher limits
2. Wait for rate limit to reset (typically hourly)
3. Reduce frequency of Context7 requests

#### MCP Server Connection Failed
**Issue**: Cannot connect to Context7 server
**Solutions**:
1. Check internet connectivity
2. Verify firewall/proxy settings
3. Test access to `https://mcp.context7.com/mcp`
4. Check Qoder IDE logs for detailed error messages

#### Environment Variable Not Loaded
**Issue**: API key from `.env` not being used
**Solutions**:
1. Ensure `.env` file is in workspace root
2. Verify variable name is exactly `CONTEXT7_API_KEY`
3. Restart Qoder IDE after modifying `.env`
4. Check that `.env` file has no syntax errors

**Section sources**
- [CONTEXT7_MCP_INTEGRATION.md](file://docs/CONTEXT7_MCP_INTEGRATION.md#L175-L224)

## Advanced Configuration

### Multiple MCP Servers

Additional MCP servers can be added to the `.qoder/mcp.json` file:

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

To configure a local server in the future, modify the `.qoder/mcp.json` file:

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

If timeout issues occur, adjust Qoder IDE's timeout settings as documented in the IDE's documentation.

**Section sources**
- [CONTEXT7_MCP_INTEGRATION.md](file://docs/CONTEXT7_MCP_INTEGRATION.md#L226-L272)

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

**Section sources**
- [CONTEXT7_MCP_INTEGRATION.md](file://docs/CONTEXT7_MCP_INTEGRATION.md#L274-L300)

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

**Section sources**
- [CONTEXT7_MCP_INTEGRATION.md](file://docs/CONTEXT7_MCP_INTEGRATION.md#L303-L322)

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

**Section sources**
- [CONTEXT7_MCP_INTEGRATION.md](file://docs/CONTEXT7_MCP_INTEGRATION.md#L324-L352)