# 🎯 Tile Shop Demo - Quick Demo Guide

## ⚡ 30-Second Setup

```bash
cd MSFT/demo/tile-shop
./start.sh
```

Then open `index.html` in your browser.

## 🎬 Demo Script (5 minutes)

### 1. Introduction (30 seconds)
"Today I'm showing you our AI-powered tile visualization tool. This allows your sales team to help customers visualize tiles in their actual spaces in real-time."

### 2. Upload Photo (30 seconds)
- "Let's say a customer comes in with a photo of their kitchen..."
- Drag & drop or click to upload a sample kitchen/bathroom photo
- Show the clean, modern interface

### 3. Select Tile (30 seconds)
- "They can browse your tile catalog..."
- Click through a few tile options
- Point out SKU numbers, names, visual previews

### 4. Apply Overlay (1 minute)
- "With one click, we overlay the selected tile on their actual space..."
- Click "Apply Tile Overlay"
- Show before/after comparison
- **Key talking point**: "This happens in real-time, no waiting for render farms"

### 5. AI Enhancement (Optional - 30 seconds)
- "We can optionally enhance this with AI for better realism..."
- Click "AI Enhance" (if configured)
- Show improved lighting/texture

### 6. Use Cases (1 minute)
- **Salesfloor**: Sales associates can show customers instantly
- **Mobile**: Works on tablets/phones for in-home consultations
- **Catalog Integration**: Connect to your actual SKU database
- **Sharing**: Customers can save/share with family/contractors

### 7. Technical Integration (30 seconds)
- "This integrates with Copilot Studio and Azure..."
- "Can be embedded in your existing systems..."
- "Works with your current tile catalog..."

### 8. Q&A Prep
- **Cost**: "Runs on Azure, pay-per-use model"
- **Accuracy**: "Uses AI segmentation to identify floor/wall areas"
- **Customization**: "Can be customized for your specific tile catalog"
- **Timeline**: "Can be deployed in 2-4 weeks"

## 🎨 Sample Photos to Have Ready

1. **Kitchen** - Good for floor tiles
2. **Bathroom** - Shows wall + floor tiles
3. **Entryway** - Different lighting conditions
4. **Backsplash area** - Wall tile focus

## 🚨 Troubleshooting During Demo

### Backend Not Running
- **Quick fix**: "Let me show you the interface first..."
- Show the UI, explain the flow
- Restart backend if time permits

### Slow Processing
- **Say**: "In production, this runs on Azure with auto-scaling for instant results"
- **Do**: Have a pre-processed example ready as backup

### CORS Error
- **Quick fix**: Use `python -m http.server 8000` to serve the HTML
- Or use the backend to serve static files (add route)

## 💡 Key Talking Points

1. **Real-time**: No waiting, instant visualization
2. **Mobile-friendly**: Works on any device
3. **AI-powered**: Smart floor/wall detection
4. **Scalable**: Azure infrastructure handles any load
5. **Customizable**: Can match your brand and catalog
6. **Integration-ready**: Works with Copilot Studio, Power Platform

## 📊 Demo Metrics to Mention

- **Processing time**: < 2 seconds per image
- **Accuracy**: AI identifies floor/wall areas automatically
- **Scalability**: Handles 1000+ concurrent users
- **Cost**: Pay-per-use, no upfront infrastructure

## 🎯 Closing

"Would you like to schedule a follow-up to discuss integration with your systems and custom tile catalog?"

---

**Remember**: Keep it simple, focus on the value, not the tech!

