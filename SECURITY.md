# Security Guidelines

## ⚠️ CRITICAL: API Keys and Sensitive Data

**NEVER commit API keys, secrets, or personal data to git repositories.**

### Environment Setup

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env with your actual credentials:**
   ```bash
   # Your actual Alpaca API credentials
   APCA_API_KEY_ID="your_actual_api_key"
   APCA_API_SECRET_KEY="your_actual_secret_key"
   PAPER="true"  # Set to "false" for live trading
   ```

3. **Copy MCP configuration template:**
   ```bash
   cp .mcp.json.example .mcp.json
   ```

### Files That Must Never Be Committed

- `.env` - Contains API keys and secrets
- `.mcp.json` - May contain user-specific configuration
- Any file containing actual API keys or personal data
- Log files that might contain sensitive information

### What's Protected

The `.gitignore` file is configured to exclude:
- All environment files (`.env*`, `*.env`)
- Secret and credential files (`*.secret`, `*.key`, `*.pem`)
- User-specific configurations
- Log files and temporary data

### Best Practices

1. **Use environment variables** instead of hardcoding credentials
2. **Use paper trading** (`PAPER="true"`) for development and testing
3. **Regularly rotate API keys** for security
4. **Never share credentials** in chat, email, or other communications
5. **Use separate API keys** for development vs production

### If You Accidentally Commit Secrets

1. **Immediately rotate the exposed credentials** on your Alpaca account
2. **Remove from git history** using tools like `git filter-branch` or BFG Repo-Cleaner
3. **Verify the secrets are removed** from all branches and tags
4. **Force push** to overwrite remote history (if applicable)

### API Key Security

- Your Alpaca API keys provide access to your trading account
- Paper trading keys are safer for development but should still be protected
- Live trading keys can execute real trades with real money
- Always use the minimum permissions necessary