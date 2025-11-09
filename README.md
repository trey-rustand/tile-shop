# Tile Shop - AI Design Visualization Demo

A quick demo application for Tile Shop showing AI-powered tile overlay on customer room photos. Built for Salesfloor AI Image Generation demonstration.

## 🎯 Purpose

This demo allows customers to:
1. Upload a photo of their room (kitchen, bathroom, etc.)
2. Select a tile SKU from available options
3. See a visual preview of how the tile would look in their space
4. Optionally enhance the visualization with AI

## 🚀 Quick Start (5 minutes)

### Option 1: Simple Demo (No Backend Required - Frontend Only)

1. Open `index.html` in a browser
2. Upload a photo and select a tile
3. Note: Overlay won't work without backend, but UI is fully functional

### Option 2: Full Demo (With Backend)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   python server.py
   ```

3. **Open the frontend:**
   - Option A: Open `index.html` directly in browser (CORS may block API calls)
   - Option B: Use a simple HTTP server:
     ```bash
     # Python 3
     python -m http.server 8000
     # Then open http://localhost:8000/index.html
     ```

4. **Test the demo:**
   - Upload a room photo
   - Select a tile SKU
   - Click "Apply Tile Overlay"
   - See the result!

## 🔧 Configuration

### Azure OpenAI (Optional - for AI Enhancement)

If you want to use AI enhancement features, create a `.env` file:

```bash
cp .env.example .env
```

Then edit `.env` with your Azure OpenAI credentials:

```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=dalle-3
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**Note:** The basic overlay works without Azure OpenAI. AI enhancement is optional.

## 📁 Project Structure

```
tile-shop/
├── index.html          # Vue.js frontend (single file)
├── server.py           # Flask backend API
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md          # This file
```

## 🎨 Features

### Current Implementation

- ✅ Photo upload (drag & drop or click)
- ✅ Tile SKU selection with visual previews
- ✅ Image overlay processing (applies tile pattern to floor area)
- ✅ Real-time preview (before/after comparison)
- ✅ Mobile-friendly responsive design
- ✅ Error handling and loading states

### Optional Features (Require Azure OpenAI)

- 🔄 AI-powered image enhancement
- 🔄 Better floor/wall segmentation
- 🔄 Realistic lighting adjustments

## 🔌 API Endpoints

### `POST /api/apply-overlay`

Applies tile overlay to uploaded image.

**Request:**
- `image` (file): Room photo
- `tileSku` (form): Tile SKU code
- `tileName` (form): Tile name

**Response:**
- JPEG image with tile overlay applied

### `POST /api/ai-enhance`

Enhances processed image using AI (optional).

**Request:**
- `image` (file): Processed image

**Response:**
- Enhanced JPEG image

### `GET /api/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "azure_openai_configured": true
}
```

## 🎯 Demo Flow

1. **Upload Photo**: Customer takes/uploads photo of their room
2. **Select Tile**: Browse and select from available tile SKUs
3. **Preview**: See instant preview of tile overlay
4. **Enhance** (Optional): Use AI to refine the visualization
5. **Share**: Customer can save/share the result

## 🛠️ Customization

### Adding More Tiles

Edit the `tiles` array in `index.html`:

```javascript
tiles: [
    {
        sku: 'TS-XXX',
        name: 'Your Tile Name',
        patternUrl: 'data:image/svg+xml;base64,...' // or URL to image
    },
    // ... more tiles
]
```

### Adjusting Overlay Area

Edit the `apply_tile_overlay` function in `server.py`:

```python
# Change floor_height percentage
floor_height = int(room_img.height * 0.4)  # 40% of image height

# Enable wall overlays
# Uncomment wall masking code
```

## 🚨 Troubleshooting

### CORS Errors

If you see CORS errors when opening `index.html` directly:
- Use a local HTTP server (see Quick Start)
- Or configure CORS in `server.py` for your domain

### Backend Not Responding

1. Check server is running: `python server.py`
2. Check port 5000 is available
3. Verify dependencies: `pip install -r requirements.txt`

### Images Not Processing

1. Check browser console for errors
2. Verify backend is accessible: `curl http://localhost:5000/api/health`
3. Check image file size (keep under 10MB for demo)

## 📝 Notes for Demo

- **Keep it simple**: Focus on the core overlay feature
- **Have sample photos ready**: Kitchen, bathroom, entryway photos work best
- **Test beforehand**: Make sure backend is running
- **Backup plan**: If backend fails, show the UI and explain the flow

## 🔐 Security Notes

- API keys should NEVER be committed to git
- Use `.env` file (already in `.gitignore`)
- For production, add authentication and rate limiting

## 📞 Support

For issues or questions, contact the PRR team.

---

**Built for Tile Shop Salesfloor AI Image Generation Demo** 🏠✨

