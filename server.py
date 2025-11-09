#!/usr/bin/env python3
"""
Tile Shop Demo - Backend API Server
Handles image overlay and AI enhancement for tile visualization demo
"""

from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import io
import base64
import os
import requests
from urllib.parse import urlparse
import re
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np

# Google GenAI imports (new library)
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠️ google-genai not installed. Install with: pip install --upgrade google-genai")

try:
    from google.cloud import aiplatform
    from google.oauth2 import service_account
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    print("⚠️ google-cloud-aiplatform not installed. Install with: pip install google-cloud-aiplatform")

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

# Configuration - Support both Azure OpenAI and regular OpenAI
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'dalle-3')
AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')

# Regular OpenAI API (simpler option)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Google Cloud Configuration
# Supports multiple env var names for flexibility
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_CLOUD_API_KEY') or os.getenv('NANO_BANANA_API_KEY')

# Vertex AI Configuration (requires service account or OAuth2)
VERTEX_AI_PROJECT_ID = os.getenv('VERTEX_AI_PROJECT_ID', '')
VERTEX_AI_LOCATION = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')  # Path to service account JSON

# Initialize Google GenAI client (new library)
# Use vertexai=False for API key authentication
genai_client = None
if GEMINI_API_KEY and GENAI_AVAILABLE:
    try:
        genai_client = genai.Client(
            vertexai=False,  # False = use API key (Generative Language API), True = use OAuth2 (Vertex AI)
            api_key=GEMINI_API_KEY,
        )
        print("✅ Google GenAI client initialized (Nano Banana ready!)")
    except Exception as e:
        print(f"⚠️ Failed to initialize GenAI client: {e}")

# Initialize Vertex AI (for Vertex AI API)
vertex_ai_initialized = False
if VERTEX_AI_PROJECT_ID and VERTEX_AI_AVAILABLE:
    try:
        if GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
            # Use service account
            credentials = service_account.Credentials.from_service_account_file(
                GOOGLE_APPLICATION_CREDENTIALS
            )
            aiplatform.init(project=VERTEX_AI_PROJECT_ID, location=VERTEX_AI_LOCATION, credentials=credentials)
        else:
            # Try default credentials (gcloud auth application-default login)
            aiplatform.init(project=VERTEX_AI_PROJECT_ID, location=VERTEX_AI_LOCATION)
        vertex_ai_initialized = True
        print(f"✅ Vertex AI initialized for project: {VERTEX_AI_PROJECT_ID}")
    except Exception as e:
        print(f"⚠️ Vertex AI initialization failed: {e}")
        print("   Note: Vertex AI requires service account or 'gcloud auth application-default login'")

# Initialize OpenAI client if available
openai_client = None
if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except:
        pass

def decode_svg_pattern(svg_data_url):
    """Extract SVG pattern from data URL and create a tile pattern image"""
    try:
        # Decode base64 SVG
        if ',' in svg_data_url:
            svg_data = base64.b64decode(svg_data_url.split(',')[1])
        else:
            svg_data = base64.b64decode(svg_data_url)
        
        # For demo purposes, create a simple tile pattern
        # In production, you'd parse the SVG or use actual tile images
        tile_size = 100
        pattern = Image.new('RGB', (tile_size, tile_size), color='white')
        draw = ImageDraw.Draw(pattern)
        
        # Draw grid lines
        for i in range(0, tile_size, 10):
            draw.line([(i, 0), (i, tile_size)], fill='#ddd', width=1)
            draw.line([(0, i), (tile_size, i)], fill='#ddd', width=1)
        
        return pattern
    except Exception as e:
        print(f"Error decoding pattern: {e}")
        # Return default pattern
        pattern = Image.new('RGB', (100, 100), color='#f0f0f0')
        return pattern

def create_tile_texture(tile_name, tile_sku):
    """Create a tile texture based on SKU/name"""
    size = 200
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    
    # Create different patterns based on tile name
    if 'white' in tile_name.lower():
        color = '#ffffff'
        grid_color = '#e0e0e0'
    elif 'gray' in tile_name.lower() or 'slate' in tile_name.lower():
        color = '#555555'
        grid_color = '#333333'
    elif 'blue' in tile_name.lower():
        color = '#17a2b8'
        grid_color = '#0f7995'
    elif 'marble' in tile_name.lower():
        color = '#f5f5f5'
        grid_color = '#e0e0e0'
    else:
        color = '#f8f9fa'
        grid_color = '#ddd'
    
    # Fill background
    draw.rectangle([(0, 0), (size, size)], fill=color)
    
    # Draw grid pattern
    for i in range(0, size, 20):
        draw.line([(i, 0), (i, size)], fill=grid_color, width=2)
        draw.line([(0, i), (size, i)], fill=grid_color, width=2)
    
    # Add texture variation
    for i in range(0, size, 40):
        for j in range(0, size, 40):
            if (i + j) % 80 == 0:
                draw.rectangle([(i, j), (i+20, j+20)], fill=grid_color, outline=None)
    
    return img

def detect_floor_area_with_ai(image_data):
    """
    Use AI vision to detect floor area in the image
    Returns a mask indicating where the floor is
    """
    if not openai_client:
        return None
    
    try:
        # Convert image to base64 for API
        img = Image.open(io.BytesIO(image_data))
        img = img.convert('RGB')
        
        # Resize if too large (OpenAI has size limits)
        max_size = 1024
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Use GPT-4 Vision to identify floor area
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4o" for better accuracy
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this room image and identify where the floor is. 
                            Respond with a JSON object containing:
                            - "floor_bottom_y": the Y coordinate where the floor starts (as percentage 0-100, from top)
                            - "floor_coverage": percentage of image that is floor (0-100)
                            - "has_walls": true/false if walls are visible
                            
                            Example: {"floor_bottom_y": 60, "floor_coverage": 40, "has_walls": true}
                            Only return the JSON, nothing else."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=150
        )
        
        result_text = response.choices[0].message.content.strip()
        # Extract JSON
        json_match = re.search(r'\{[^{}]*\}', result_text, re.DOTALL)
        if json_match:
            import json
            floor_data = json.loads(json_match.group(0))
            return floor_data
        
    except Exception as e:
        print(f"AI floor detection error: {e}")
    
    return None

def create_smart_floor_mask(room_img, floor_data=None):
    """
    Create a mask for floor area, using AI detection if available
    """
    mask = Image.new('L', room_img.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    
    if floor_data:
        # Use AI-detected floor area
        floor_start_y = int(room_img.height * (floor_data.get('floor_bottom_y', 60) / 100))
        floor_coverage = floor_data.get('floor_coverage', 40) / 100
        
        # Create gradient mask for more natural blending
        floor_height = int(room_img.height * floor_coverage)
        for y in range(room_img.height - floor_height, room_img.height):
            # Gradient from 0 to 255
            alpha = int(255 * ((y - (room_img.height - floor_height)) / floor_height))
            mask_draw.rectangle([(0, y), (room_img.width, y + 1)], fill=alpha)
    else:
        # Fallback: use bottom 40% with gradient
        floor_height = int(room_img.height * 0.4)
        for y in range(room_img.height - floor_height, room_img.height):
            alpha = int(255 * ((y - (room_img.height - floor_height)) / floor_height))
            mask_draw.rectangle([(0, y), (room_img.width, y + 1)], fill=alpha)
    
    return mask

def apply_tile_overlay(room_image, tile_texture, use_ai_detection=True):
    """
    Apply tile overlay using AI-powered floor detection for better results
    Keeps the rest of the image exactly the same
    """
    room_img = Image.open(io.BytesIO(room_image))
    room_img = room_img.convert('RGB')
    original_size = room_img.size
    
    # Detect floor area with AI if available
    floor_data = None
    if use_ai_detection and openai_client:
        floor_data = detect_floor_area_with_ai(room_image)
    
    # Create smart mask for floor area
    mask = create_smart_floor_mask(room_img, floor_data)
    
    # Create tile pattern that matches room perspective
    tile_resized = tile_texture.resize(room_img.size, Image.Resampling.LANCZOS)
    
    # Apply perspective-aware tiling (simple approach - can be enhanced)
    # For now, just tile it
    tile_pattern = Image.new('RGB', room_img.size)
    tile_size = 200
    for x in range(0, room_img.width, tile_size):
        for y in range(0, room_img.height, tile_size):
            tile_crop = tile_texture.resize((tile_size, tile_size), Image.Resampling.LANCZOS)
            tile_pattern.paste(tile_crop, (x, y))
    
    # Blend tile with original using the mask - this keeps everything else the same
    result = Image.composite(tile_pattern, room_img, mask)
    
    # Final blend for natural look (70% original, 30% tile in masked area)
    result = Image.blend(room_img, result, 0.3)
    
    return result

def apply_tile_with_gemini(image_data, tile_name, tile_sku):
    """
    Use Gemini 2.5 Flash Image to intelligently replace ALL tiles in the image
    Uses the new google-genai library
    """
    if not GEMINI_API_KEY or not GENAI_AVAILABLE or not genai_client:
        print("⚠️ Gemini not available")
        return None
    
    try:
        # Detect image format
        img = Image.open(io.BytesIO(image_data))
        img_format = img.format.lower() if img.format else 'jpeg'
        mime_type = f"image/{img_format}"
        
        # System instruction
        si_text = """I am going to give you a picture of a kitchen or some sort of room then send you a sku of a tile and I want the system to make the tile in the image match the sku that I send it. Only change the tiles, nothing else."""
        
        # User prompt
        user_prompt = f"""Replace all tiles in this room image with {tile_name} tiles (SKU: {tile_sku}).

Identify and replace ALL tiles (floor, wall, backsplash, etc.) with the new tile style.
Keep everything else exactly the same - only change the tiles."""
        
        print(f"🚀 Calling Nano Banana (Gemini 2.5 Flash Image) to replace tiles...")
        
        # Create image part
        msg1_image1 = types.Part.from_bytes(
            data=image_data,
            mime_type=mime_type,
        )
        
        # Create contents
        contents = [
            types.Content(
                role="user",
                parts=[
                    msg1_image1,
                    types.Part.from_text(text=user_prompt)
                ]
            ),
        ]
        
        # Generate content config
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            max_output_tokens=32768,
            response_modalities=["TEXT", "IMAGE"],  # Request image response
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="OFF"
                )
            ],
            system_instruction=[types.Part.from_text(text=si_text)],
        )
        
        # Generate content (streaming)
        model = "gemini-2.5-flash-image"
        image_parts = []
        text_parts = []
        
        for chunk in genai_client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            # Check for text
            if hasattr(chunk, 'text') and chunk.text:
                text_parts.append(chunk.text)
            
            # Check for image data in chunk
            if hasattr(chunk, 'parts') and chunk.parts:
                for part in chunk.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        if hasattr(part.inline_data, 'data'):
                            image_parts.append(part.inline_data.data)
            
            # Also check if chunk itself has inline_data
            if hasattr(chunk, 'inline_data') and chunk.inline_data:
                if hasattr(chunk.inline_data, 'data'):
                    image_parts.append(chunk.inline_data.data)
        
        # If we got an image, return it
        if image_parts:
            print(f"✅ Successfully got image from Nano Banana!")
            img_data = image_parts[0]  # Use first image
            edited_img = Image.open(io.BytesIO(img_data))
            return edited_img.convert('RGB')
        
        # If we only got text, log it
        if text_parts:
            print(f"⚠️ Nano Banana returned text instead of image: {''.join(text_parts)[:200]}...")
        
        print(f"⚠️ No image in response")
        return None
        
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.route('/api/apply-overlay', methods=['POST'])
def apply_overlay():
    """Apply tile overlay to uploaded room image using AI image editing"""
    try:
        # Debug logging
        print(f"🔍 DEBUG - Content-Type: {request.content_type}")
        print(f"🔍 DEBUG - Is JSON: {request.is_json}")
        print(f"🔍 DEBUG - Form keys: {list(request.form.keys())}")
        print(f"🔍 DEBUG - Files keys: {list(request.files.keys())}")
        
        # Handle both form data and JSON requests
        if request.is_json:
            json_data = request.json or {}
            tile_sku = json_data.get('tileSku', 'TS-001')
            tile_name = json_data.get('tileName', 'Classic White')
            image_url = json_data.get('image')
        else:
            tile_sku = request.form.get('tileSku', 'TS-001')
            tile_name = request.form.get('tileName', 'Classic White')
            image_url = request.form.get('image')
        
        image_data = None

        # 🔹 Case 1: File upload (multipart/form-data)
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                raw_bytes = file.read()
                print(f"🔍 DEBUG - File upload size: {len(raw_bytes)} bytes")
                try:
                    # Try direct bytes first
                    test_img = Image.open(io.BytesIO(raw_bytes))
                    image_data = raw_bytes
                    print(f"✅ Loaded image from multipart form upload (format: {test_img.format})")
                except Exception as e:
                    print(f"🔍 DEBUG - Direct bytes failed: {e}, trying base64 decode...")
                    try:
                        # If Pillow can't recognize, try base64 decoding
                        # Handle both string and bytes
                        if isinstance(raw_bytes, bytes):
                            try:
                                # Try decoding as UTF-8 string first, then base64
                                decoded = base64.b64decode(raw_bytes.decode('utf-8'))
                            except (UnicodeDecodeError, ValueError):
                                # If not UTF-8, try direct base64 decode
                                decoded = base64.b64decode(raw_bytes)
                        else:
                            decoded = base64.b64decode(raw_bytes)
                        test_img = Image.open(io.BytesIO(decoded))
                        image_data = decoded
                        print(f"✅ Decoded Power Automate base64-to-binary upload (format: {test_img.format})")
                    except Exception as e2:
                        print(f"❌ Failed to identify uploaded image data: {e2}")
                        return jsonify({'error': f'Invalid image file uploaded: {str(e2)}'}), 400

        # 🔹 Case 2: Form field or JSON with image data (URL, base64 string, or data URI)
        if not image_data and image_url:
            print(f"🔍 DEBUG - Processing image_url (length: {len(image_url) if image_url else 0})")
            
            # Check if it's a data URI (data:image/...)
            if image_url.startswith('data:image'):
                try:
                    header, encoded = image_url.split(',', 1)
                    image_data = base64.b64decode(encoded)
                    test_img = Image.open(io.BytesIO(image_data))
                    print(f"✅ Decoded base64 data URI (format: {test_img.format})")
                except Exception as e:
                    return jsonify({'error': f'Failed to decode base64 data URI: {str(e)}'}), 400
            
            # Check if it's a URL
            elif image_url.startswith('http://') or image_url.startswith('https://'):
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    response = requests.get(image_url, headers=headers, timeout=30)
                    response.raise_for_status()
                    image_data = response.content
                    test_img = Image.open(io.BytesIO(image_data))
                    print(f"✅ Downloaded image from URL (format: {test_img.format})")
                except Exception as e:
                    return jsonify({'error': f'Failed to download image: {str(e)}'}), 400
            
            # Check if it's a plain base64 string (Power Automate might send this)
            else:
                try:
                    # Try to decode as base64
                    decoded = base64.b64decode(image_url)
                    test_img = Image.open(io.BytesIO(decoded))
                    image_data = decoded
                    print(f"✅ Decoded plain base64 string from form field (format: {test_img.format})")
                except Exception as e:
                    # If it's not base64, log for debugging but don't fail yet
                    print(f"🔍 DEBUG - Not a valid base64 string: {e}")
                    print(f"🔍 DEBUG - First 100 chars of image_url: {image_url[:100] if image_url else None}")

        # Final validation - ensure we have valid image data
        if not image_data:
            return jsonify({
                'error': 'No image provided. Send a file upload, base64 data URI, base64 string, or image URL',
                'debug': {
                    'content_type': request.content_type,
                    'is_json': request.is_json,
                    'form_keys': list(request.form.keys()),
                    'files_keys': list(request.files.keys()),
                    'image_url_length': len(image_url) if image_url else 0,
                    'image_url_preview': image_url[:100] if image_url else None
                }
            }), 400
        
        # Validate image data is actually a valid image before processing
        try:
            test_img = Image.open(io.BytesIO(image_data))
            print(f"✅ Image validated successfully (format: {test_img.format}, size: {test_img.size})")
        except Exception as e:
            return jsonify({
                'error': f'Invalid image data: {str(e)}',
                'debug': {
                    'data_length': len(image_data),
                    'data_preview_hex': image_data[:50].hex() if len(image_data) > 50 else image_data.hex()
                }
            }), 400

        # 🔹 Try Gemini first
        if GEMINI_API_KEY:
            print(f"🎯 Attempting Nano Banana tile replacement for {tile_name} (SKU: {tile_sku})")
            try:
                result_image = apply_tile_with_gemini(image_data, tile_name, tile_sku)
                if result_image:
                    output = io.BytesIO()
                    result_image.save(output, format='JPEG', quality=90)
                    output.seek(0)
                    print("✅ Gemini output sent back to client")
                    return send_file(output, mimetype='image/jpeg')
                else:
                    print("⚠️ Gemini returned None, falling back to overlay")
            except Exception as e:
                print(f"❌ Gemini error: {e}")
                import traceback; traceback.print_exc()

        # 🔹 Fallback to local overlay if Gemini fails
        tile_texture = create_tile_texture(tile_name, tile_sku)
        use_ai = bool(openai_client)
        result_image = apply_tile_overlay(image_data, tile_texture, use_ai_detection=use_ai)

        output = io.BytesIO()
        result_image.save(output, format='JPEG', quality=90)
        output.seek(0)
        print("✅ Fallback overlay applied successfully")

        return send_file(output, mimetype='image/jpeg')

    except Exception as e:
        print(f"❌ Error applying overlay: {e}")
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-enhance', methods=['POST'])
def ai_enhance():
    """
    Use AI inpainting to make the tile overlay look more realistic
    This keeps the image the same but makes the tile integration better
    """
    try:
        if not openai_client:
            # Fallback: just return the image with better blending
            if 'image' not in request.files:
                return jsonify({'error': 'No image provided'}), 400
            
            file = request.files['image']
            image_data = file.read()
            img = Image.open(io.BytesIO(image_data))
            img = img.convert('RGB')
            
            # Apply subtle enhancements
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.05)
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.1)
            
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=95)
            output.seek(0)
            return send_file(output, mimetype='image/jpeg')
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        image_data = file.read()
        img = Image.open(io.BytesIO(image_data))
        img = img.convert('RGB')
        
        # Resize if needed (OpenAI has size limits)
        max_size = 1024
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert to PNG for better quality
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Use GPT-4 Vision to improve the tile integration
        # This is a workaround since DALL-E 3 doesn't support inpainting
        # We use vision to analyze and suggest improvements, then apply them
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """This image has a tile overlay applied. Analyze it and suggest improvements for:
                            1. Better lighting integration
                            2. More realistic shadows
                            3. Better perspective matching
                            
                            Respond with JSON: {"improvements": ["suggestion1", "suggestion2"]}
                            Only return JSON."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=200
        )
        
        # For now, apply enhanced blending and lighting adjustments
        # In production, you'd use DALL-E 2 edit API or Stable Diffusion inpainting
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.05)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.98)  # Slightly darker for realism
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.1)
        
        # Apply subtle blur to edges for better integration
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=95)
        output.seek(0)
        
        return send_file(output, mimetype='image/jpeg')
    
    except Exception as e:
        print(f"Error in AI enhancement: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to simple enhancement
        if 'image' in request.files:
            file = request.files['image']
            image_data = file.read()
            img = Image.open(io.BytesIO(image_data))
            img = img.convert('RGB')
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=95)
            output.seek(0)
            return send_file(output, mimetype='image/jpeg')
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """Generate image using OpenAI DALL-E (since Gemini doesn't generate images)"""
    try:
        # Use OpenAI DALL-E since Gemini doesn't generate images
        if not OPENAI_API_KEY:
            return jsonify({'error': 'OpenAI API key not configured. Add OPENAI_API_KEY to .env file'}), 503
        
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Use OpenAI DALL-E for image generation
        # Gemini models analyze images but don't generate them
        if not openai_client:
            return jsonify({'error': 'OpenAI client not initialized'}), 500
        
        try:
            # Use DALL-E 3 for image generation
            response = openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            return jsonify({'image_url': image_url})
            
        except Exception as e:
            import sys
            sys.stdout.write(f"OpenAI DALL-E error: {e}\n")
            sys.stdout.flush()
            return jsonify({
                'error': f'DALL-E image generation failed: {str(e)}',
                'hint': 'Make sure your OpenAI API key has access to DALL-E 3'
            }), 500
        
        # Old code for trying multiple endpoints - keeping as fallback
        endpoints_to_try = []
        
        for endpoint_config in endpoints_to_try:
            try:
                url = endpoint_config['url']
                payload = endpoint_config.get('payload', {"prompt": prompt})
                req_headers = endpoint_config.get('headers', headers)
                
                import sys
                sys.stdout.write(f"Trying endpoint: {url}\n")
                sys.stdout.flush()
                
                response = requests.post(
                    url,
                    headers=req_headers,
                    json=payload,
                    timeout=30
                )
                
                sys.stdout.write(f"Response status: {response.status_code}\n")
                sys.stdout.write(f"Response body: {response.text[:500]}\n")
                sys.stdout.flush()
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Try different response formats
                    if 'images' in result and len(result['images']) > 0:
                        image_data = result['images'][0]
                        if 'imageUrl' in image_data:
                            return jsonify({'image_url': image_data['imageUrl']})
                        elif 'base64' in image_data:
                            return jsonify({'image': f"data:image/png;base64,{image_data['base64']}"})
                        elif 'bytesBase64Encoded' in image_data:
                            return jsonify({'image': f"data:image/png;base64,{image_data['bytesBase64Encoded']}"})
                    
                    # Check for direct image data
                    if 'image' in result:
                        return jsonify({'image': result['image']})
                    if 'imageUrl' in result:
                        return jsonify({'image_url': result['imageUrl']})
                    
                    # Vertex AI / Gemini content format
                    if 'candidates' in result:
                        for candidate in result['candidates']:
                            if 'content' in candidate and 'parts' in candidate['content']:
                                for part in candidate['content']['parts']:
                                    if 'inlineData' in part:
                                        base64_data = part['inlineData']['data']
                                        mime_type = part['inlineData'].get('mimeType', 'image/png')
                                        return jsonify({'image': f"data:{mime_type};base64,{base64_data}"})
                    
                    # Vertex AI Imagen response format
                    if 'predictions' in result and len(result['predictions']) > 0:
                        prediction = result['predictions'][0]
                        if 'bytesBase64Encoded' in prediction:
                            return jsonify({'image': f"data:image/png;base64,{prediction['bytesBase64Encoded']}"})
                        elif 'image' in prediction:
                            return jsonify({'image': prediction['image']})
                
                elif response.status_code == 400:
                    # Bad request - try next endpoint
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    import sys
                    sys.stdout.write(f"400 Error: {error_data}\n")
                    sys.stdout.flush()
                    continue
                else:
                    # Log but try next endpoint
                    import sys
                    sys.stdout.write(f"Error {response.status_code}: {response.text[:200]}\n")
                    sys.stdout.flush()
                    continue
                    
            except requests.exceptions.RequestException as e:
                import sys
                sys.stdout.write(f"Request error for {endpoint_config.get('url', 'unknown')}: {e}\n")
                sys.stdout.flush()
                continue
            except Exception as e:
                import sys
                sys.stdout.write(f"Unexpected error: {e}\n")
                sys.stdout.flush()
                import traceback
                traceback.print_exc()
                continue
        
        # If all endpoints fail, return detailed error with helpful instructions
        return jsonify({
            'error': 'Image generation failed. Google Gemini models analyze images but do not generate them.',
            'hint': 'For image generation with Google, you need: 1) Enable Generative Language API at https://console.developers.google.com/apis/api/generativelanguage.googleapis.com/overview, 2) Use Imagen API (requires different setup), OR 3) Use a different image generation service like DALL-E or Stable Diffusion',
            'alternative': 'Consider using OpenAI DALL-E API for image generation, or enable Google Imagen API in your GCP project'
        }), 500
        
    except Exception as e:
        print(f"Error generating image: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/test-nano-banana', methods=['POST'])
def test_nano_banana():
    """Simple test endpoint to verify Nano Banana (Gemini) is working"""
    try:
        if not GEMINI_API_KEY:
            return jsonify({'error': 'GEMINI_API_KEY or GOOGLE_CLOUD_API_KEY not configured'}), 400
        
        data = request.get_json() or {}
        test_prompt = data.get('prompt', 'Say hello and confirm you are working!')
        
        print(f"🧪 Testing Nano Banana with prompt: {test_prompt}")
        
        # Simple test: Use the new google-genai library
        if not GENAI_AVAILABLE or not genai_client:
            return jsonify({
                'error': 'google-genai library not installed or client not initialized',
                'hint': 'Run: pip install --upgrade google-genai'
            }), 500
        
        try:
            print(f"📡 Calling Gemini API...")
            
            # Simple text generation test
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=test_prompt)]
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1024,
            )
            
            text_response = ""
            for chunk in genai_client.models.generate_content_stream(
                model="gemini-2.0-flash-exp",
                contents=contents,
                config=generate_content_config,
            ):
                if hasattr(chunk, 'text') and chunk.text:
                    text_response += chunk.text
            
            if text_response:
                print(f"✅ Success! Response: {text_response[:100]}...")
                return jsonify({
                    'success': True,
                    'prompt': test_prompt,
                    'response': text_response,
                    'message': 'Nano Banana is working! ✅'
                })
            
            return jsonify({
                'success': False,
                'error': 'No text response from Gemini'
            }), 500
            
        except Exception as e:
            print(f"❌ Error calling Gemini: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e),
                'hint': 'Check your GEMINI_API_KEY (or GOOGLE_CLOUD_API_KEY) and that Generative Language API is enabled'
            }), 500
            
    except Exception as e:
        print(f"Error in test endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'openai_configured': bool(OPENAI_API_KEY),
        'azure_openai_configured': bool(AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY),
        'gemini_configured': bool(GEMINI_API_KEY)
    })

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('.', path)

if __name__ == '__main__':
    # Render.com sets PORT environment variable, default to 5001 for local
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"""
    🏠 Tile Shop Demo Server
    ========================
    Server running on http://localhost:{port}
    
    Endpoints:
    - POST /api/apply-overlay - Apply tile overlay
    - POST /api/ai-enhance - AI enhancement (optional)
    - POST /api/generate-image - Generate image with Nano Banana/Gemini
    - GET  /api/health - Health check
    
    OpenAI API: {'✅ Configured' if OPENAI_API_KEY else '❌ Not configured (add OPENAI_API_KEY to .env)'}
    Azure OpenAI: {'✅ Configured' if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY else '❌ Not configured'}
    Gemini/Nano Banana: {'✅ Configured' if GEMINI_API_KEY else '❌ Not configured (add GEMINI_API_KEY to .env)'}
    """)
    
    # Only run Flask dev server if not using gunicorn (local development)
    # Gunicorn will handle production on Render
    app.run(host='0.0.0.0', port=port, debug=debug)

