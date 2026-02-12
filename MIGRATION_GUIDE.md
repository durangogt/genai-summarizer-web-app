# Migration Guide: Azure OpenAI to GitHub Models

This guide explains how to migrate from Azure OpenAI to GitHub Models for the GenAI Summarizer Web App.

## What Changed?

The application now uses **GitHub Models** instead of Azure OpenAI. GitHub Models provides an OpenAI-compatible API that works with the same `openai` Python SDK.

### Key Differences

| Aspect | Azure OpenAI | GitHub Models |
|--------|--------------|---------------|
| **Python Import** | `from openai import AzureOpenAI` | `from openai import OpenAI` |
| **Authentication** | API Key + API Version | GitHub Token |
| **Endpoint** | Azure-specific endpoint | `https://models.inference.ai.azure.com` |
| **Model Name** | Deployment name (e.g., `gpt-4`) | Model name (e.g., `gpt-4o`) |

### Code Changes Summary

1. **Configuration** (`backend/app/config.py`):
   - Replaced `AZURE_OPENAI_API_KEY` → `GITHUB_TOKEN`
   - Replaced `AZURE_OPENAI_ENDPOINT` → `GITHUB_MODELS_ENDPOINT`
   - Replaced `AZURE_OPENAI_DEPLOYMENT` → `GITHUB_MODEL_NAME`
   - Removed `AZURE_OPENAI_API_VERSION` (not needed)

2. **Engine** (`backend/app/summarizer/engine.py`):
   - Changed from `AzureOpenAI` client to `OpenAI` client
   - Updated client initialization to use `base_url` instead of `azure_endpoint`
   - Chat completions API call remains **exactly the same**

## Migration Steps

### Step 1: Update Environment Variables

**Old `.env` file:**
```bash
AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**New `.env` file:**
```bash
GITHUB_TOKEN=your-github-token-here
GITHUB_MODELS_ENDPOINT=https://models.inference.ai.azure.com
GITHUB_MODEL_NAME=gpt-4o
```

### Step 2: Get Your GitHub Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Generate a new token (classic) or fine-grained token
3. For GitHub Models access, you may need specific permissions (check GitHub Models documentation)
4. Copy the token and set it as `GITHUB_TOKEN` in your `.env` file

### Step 3: Update Your Code (if you forked)

If you're using the latest code from this repository, no code changes are needed. The migration has already been completed.

If you've made custom modifications:
- Pull the latest changes from this branch
- Review the changes in the 4 files mentioned above
- Merge or apply changes to your custom code

### Step 4: Test the Migration

1. Update your `.env` file with GitHub credentials
2. Start the application: `python run.py`
3. Test a summarization to ensure everything works
4. Check logs to confirm "GitHub Models client initialized" message

## Functionality Preserved

✅ All functionality remains **exactly the same**:
- Text, PDF, DOCX, and URL summarization
- Configurable summary lengths (short, medium, long)
- Batch processing
- REST API endpoints
- Web UI
- Authentication and history

The only changes are:
- Backend provider (Azure OpenAI → GitHub Models)
- Environment variable names
- Initialization code

## Troubleshooting

### "GITHUB_TOKEN environment variable is required"

**Solution:** Make sure you've created a `.env` file (not `.env.template`) with your GitHub token.

### "Failed to initialize GitHub Models client"

**Possible causes:**
1. Invalid or expired GitHub token
2. Token doesn't have access to GitHub Models
3. Network connectivity issues

**Solution:** 
- Verify your token is correct
- Check token permissions
- Test the endpoint with a curl command

### "Authentication error" during summarization

**Solution:** Your GitHub token may not have access to the GitHub Models API. Check:
1. GitHub Models availability in your region
2. Token scopes and permissions
3. GitHub Models documentation for required access

## Rollback

If you need to rollback to Azure OpenAI:

1. Checkout the previous commit before this migration
2. Update your `.env` with Azure OpenAI credentials
3. Restart the application

Or manually revert the changes in:
- `backend/app/config.py`
- `backend/app/summarizer/engine.py`
- `.env.template`
- `run.py`

## Benefits of GitHub Models

- **OpenAI-compatible API**: Same interface, easier migration
- **Model variety**: Access to various models through GitHub
- **Integration**: Works with existing GitHub workflows
- **Simplicity**: Simpler authentication (just a token)

## Questions?

If you encounter issues during migration:
1. Check the logs in `app.log`
2. Verify all environment variables are set correctly
3. Ensure the `openai` Python package is up to date
4. Review the GitHub Models documentation

---

**Migration completed**: This branch contains all necessary changes to use GitHub Models instead of Azure OpenAI.
