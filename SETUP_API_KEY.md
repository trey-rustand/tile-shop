# 🔑 How to Configure Your OpenAI API Key

## Two Options:

### Option 1: Azure OpenAI (Recommended for Microsoft/Azure projects)

If you have **Azure OpenAI** credentials (from Microsoft/Azure portal), add these to your `.env` file:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-api-key-here
AZURE_OPENAI_DEPLOYMENT=dalle-3
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**Where to find these:**
- **Endpoint**: Your Azure OpenAI resource URL (e.g., `https://myresource.openai.azure.com/`)
- **API Key**: Found in Azure Portal → Your OpenAI Resource → Keys and Endpoint
- **Deployment**: The name of your DALL-E deployment (usually `dalle-3` or `dalle-2`)

### Option 2: Regular OpenAI API

If you have a regular **OpenAI API key** (from platform.openai.com), add this to your `.env` file:

```bash
# Regular OpenAI API
OPENAI_API_KEY=sk-...
```

## 📝 Steps to Configure:

1. **Open the `.env` file** in the `tile-shop` directory:
   ```bash
   cd MSFT/demo/tile-shop
   nano .env
   # or use your preferred editor
   ```

2. **Add your credentials** - Replace the placeholder with your actual key:
   ```bash
   # For Azure OpenAI:
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-actual-key-here
   
   # OR for regular OpenAI:
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

3. **Save the file** and restart the server

4. **Verify it's working** - When you start the server, you should see:
   ```
   OpenAI API: ✅ Configured
   Azure OpenAI: ✅ Configured  (if using Azure)
   ```

## 🔍 Which one do you have?

- **Azure OpenAI**: Key starts with something like `a1b2c3d4...` and you have an endpoint URL
- **Regular OpenAI**: Key starts with `sk-` and you got it from platform.openai.com

## ⚠️ Important:

- **Never commit the `.env` file to git** (it's already in .gitignore)
- **Keep your API keys secret** - don't share them
- The demo works **without** API keys for basic overlay - AI enhancement is optional

