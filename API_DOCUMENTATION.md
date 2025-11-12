# Tile Shop AI Image Generation API

## Generate Image Endpoint

Generate images using Nano Banana (Gemini AI) and get a publicly accessible URL.

### Endpoint
```
POST /api/generate-image
```

### Full URL
```
https://your-render-domain.onrender.com/api/generate-image
```
*(Replace `your-render-domain` with your actual Render domain)*

---

## Request Format

### Option 1: FormData (Recommended)

**cURL:**
```bash
curl -X POST https://your-render-domain.onrender.com/api/generate-image \
  -F "prompt=Generate a beautiful modern kitchen with white cabinets"
```

**JavaScript/Fetch:**
```javascript
const formData = new FormData();
formData.append('prompt', 'Generate a beautiful modern kitchen with white cabinets');

const response = await fetch('https://your-render-domain.onrender.com/api/generate-image', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log('Public URL:', data.public_url);
```

**Python:**
```python
import requests

url = "https://your-render-domain.onrender.com/api/generate-image"
files = {}
data = {"prompt": "Generate a beautiful modern kitchen with white cabinets"}

response = requests.post(url, files=files, data=data)
result = response.json()
print("Public URL:", result['public_url'])
```

### Option 2: JSON

**cURL:**
```bash
curl -X POST https://your-render-domain.onrender.com/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Generate a beautiful modern kitchen with white cabinets"}'
```

**JavaScript/Fetch:**
```javascript
const response = await fetch('https://your-render-domain.onrender.com/api/generate-image', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    prompt: 'Generate a beautiful modern kitchen with white cabinets'
  })
});

const data = await response.json();
console.log('Public URL:', data.public_url);
```

**Python:**
```python
import requests

url = "https://your-render-domain.onrender.com/api/generate-image"
headers = {"Content-Type": "application/json"}
payload = {"prompt": "Generate a beautiful modern kitchen with white cabinets"}

response = requests.post(url, json=payload, headers=headers)
result = response.json()
print("Public URL:", result['public_url'])
```

---

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Description of the image you want to generate |

**Example Prompts:**
- `"Generate a beautiful modern kitchen with white cabinets and natural lighting"`
- `"Create an image of a cozy living room with hardwood floors"`
- `"Show me a modern bathroom with subway tile backsplash"`

---

## Response

### Success Response (200 OK)

```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "image_url": "https://your-render-domain.onrender.com/api/images/generated_20241220_143022_abc12345.png",
  "public_url": "https://your-render-domain.onrender.com/api/images/generated_20241220_143022_abc12345.png"
}
```

**Response Fields:**
- `image` - Base64 data URL for immediate display in browsers
- `image_url` - Public URL to the generated image (same as `public_url`)
- `public_url` - **Publicly accessible URL** - Use this to share or embed the image anywhere

### Error Responses

**400 Bad Request:**
```json
{
  "error": "No prompt provided"
}
```

**503 Service Unavailable:**
```json
{
  "error": "Nano Banana (Gemini) not configured. Add GEMINI_API_KEY to .env file",
  "hint": "Nano Banana is required for image generation"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Nano Banana image generation failed: [error details]",
  "hint": "Make sure GEMINI_API_KEY is configured and has access to gemini-2.5-flash-image"
}
```

---

## Using the Public URL

The `public_url` field contains a publicly accessible URL that you can:

- **Share directly** - Send the URL to anyone
- **Use in HTML** - `<img src="https://your-render-domain.onrender.com/api/images/generated_20241220_143022_abc12345.png">`
- **Embed in applications** - Use in any app that accepts image URLs
- **Download** - Open in browser to view/download

**Example:**
```html
<img src="https://your-render-domain.onrender.com/api/images/generated_20241220_143022_abc12345.png" alt="Generated kitchen">
```

---

## Example: Complete Workflow

```javascript
async function generateImage(prompt) {
  try {
    const formData = new FormData();
    formData.append('prompt', prompt);
    
    const response = await fetch('https://your-render-domain.onrender.com/api/generate-image', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to generate image');
    }
    
    const data = await response.json();
    
    // Use the public URL
    console.log('Generated image URL:', data.public_url);
    
    // Display in an img tag
    const img = document.createElement('img');
    img.src = data.public_url;
    document.body.appendChild(img);
    
    return data.public_url;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Usage
generateImage('Generate a beautiful modern kitchen with white cabinets')
  .then(url => console.log('Image ready at:', url))
  .catch(err => console.error('Failed:', err));
```

---

## Notes

- **Image Format:** All generated images are PNG format
- **File Naming:** Images are saved with unique filenames: `generated_YYYYMMDD_HHMMSS_UUID.png`
- **Storage:** Images are stored on the Render server (ephemeral - may be lost on restart)
- **Rate Limits:** Subject to Nano Banana (Gemini) API rate limits
- **Processing Time:** Typically 5-15 seconds depending on prompt complexity

---

## Testing

You can test the endpoint using the web UI at:
```
https://your-render-domain.onrender.com
```

Or use any HTTP client (Postman, Insomnia, cURL, etc.) with the examples above.

