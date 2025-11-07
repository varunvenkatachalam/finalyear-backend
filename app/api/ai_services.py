import os
import requests
import base64
from io import BytesIO
from groq import Groq #type:ignore
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import qrcode #type:ignore
import time
import random
import math
from datetime import datetime
from ..core.config import settings

class AIService:
    def __init__(self):
        print("🤖 Initializing AI Service...")
        print(f"🔍 Settings GROQ_API_KEY: {settings.GROQ_API_KEY}")
        print(f"🔍 GROQ_API_KEY exists: {bool(settings.GROQ_API_KEY)}")
        print(f"🔍 HF_API_TOKEN exists: {bool(settings.HF_API_TOKEN)}")
        
        # Initialize Groq client
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY.startswith('gsk_'):
            try:
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                print("✅ Groq client initialized successfully!")
            except Exception as e:
                print(f"❌ Failed to initialize Groq client: {e}")
                self.groq_client = None
        else:
            print("❌ Invalid or missing GROQ_API_KEY")
            self.groq_client = None
            
        # **FIXED: Updated Hugging Face API endpoint and models**
        self.HF_API_BASE = "https://router.huggingface.co/hf-inference"
        
        # Updated and verified working models with new endpoint
        self.poster_models = {
            "flux": "black-forest-labs/FLUX.1-schnell",
            "dreamshaper": "lykon/dreamshaper-8",
            "sd21": "stabilityai/stable-diffusion-2-1", 
            "openjourney": "prompthero/openjourney-v4",
            "sdxl": "stabilityai/stable-diffusion-xl-base-1.0",
            "realistic": "runwayml/stable-diffusion-v1-5",
            "animestyle": "wavymulder/Analog-Diffusion",
            "midjourney": "prompthero/openjourney",  # Alternative
            "anything": "Linaqruf/anything-v3.0"    # Alternative
        }
        
        # **ADDED: Model status tracking**
        self.model_status = {}

    def _check_model_availability(self, model_name: str) -> bool:
        """Check if a Hugging Face model is available and loaded"""
        try:
            # **FIXED: Updated API endpoint**
            API_URL = f"{self.HF_API_BASE}/models/{model_name}"
            headers = {}
            
            if settings.HF_API_TOKEN:
                headers["Authorization"] = f"Bearer {settings.HF_API_TOKEN}"
            
            # Quick status check
            response = requests.get(API_URL, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Model {model_name} is available")
                return True
            elif response.status_code == 404:
                print(f"❌ Model {model_name} not found")
                return False
            else:
                print(f"⚠️ Model {model_name} status: {response.status_code}")
                return True  # Assume it might work with generation
                
        except Exception as e:
            print(f"❌ Error checking model {model_name}: {e}")
            return False

    # ============================================================================
    # POSTER GENERATION - DUAL APPROACH (BACKGROUND ONLY vs FULL POSTER)
    # ============================================================================

    def generate_poster(self, request_data: dict) -> dict:
        """Generate poster with dual approach: background-only or full poster"""
        try:
            generation_type = request_data.get('generation_type', 'background')
            print(f"🎨 Generating poster - Type: {generation_type}")
            
            if generation_type == 'background':
                return self.generate_poster_background(request_data)
            else:
                return self.generate_full_poster(request_data)
                
        except Exception as e:
            print(f"❌ Poster generation error: {e}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            return self._professional_fallback_poster(request_data)

    def generate_full_poster(self, request_data: dict) -> dict:
        """Generate complete poster with text and design"""
        try:
            print("🖼️ Generating full poster with text overlay...")
            
            # Stage 1: Generate background
            background_result = self.generate_poster_background(request_data)
            background_image = self._base64_to_image(background_result['background_url'])
            
            # Stage 2: Add text overlay
            poster_with_text = self._add_text_overlay_to_poster(background_image, request_data)
            
            # Convert to base64
            buffered = BytesIO()
            poster_with_text.save(buffered, format="PNG", quality=100, optimize=True)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Extract text components for editor
            text_components = self._extract_poster_text_components(request_data)
            
            return {
                "poster_url": f"data:image/png;base64,{img_str}",
                "background_url": background_result['background_url'],  # Keep background for editing
                "text_components": text_components,
                "prompt_used": background_result['prompt_used'],
                "status": "success",
                "model_used": f"{background_result['model_used']}+text_overlay",
                "dimensions": f"{poster_with_text.width}x{poster_with_text.height}",
                "file_size": f"{len(buffered.getvalue()) // 1024}KB",
                "stage": "full_poster",
                "generation_type": "full_poster"
            }
            
        except Exception as e:
            print(f"❌ Full poster generation error: {e}")
            return self._professional_fallback_poster(request_data)

    def _add_text_overlay_to_poster(self, background_image: Image.Image, data: dict) -> Image.Image:
        """Add professional text overlay to poster background"""
        try:
            # Create a copy to work with
            poster = background_image.copy()
            draw = ImageDraw.Draw(poster)
            
            # Get dimensions
            width, height = poster.size
            
            # Load fonts (you'll need to provide font files or use default)
            try:
                # Try to load professional fonts
                title_font = ImageFont.truetype("arialbd.ttf", 72)  # Bold for title
                subtitle_font = ImageFont.truetype("arial.ttf", 36)
                detail_font = ImageFont.truetype("arial.ttf", 24)
            except:
                # Fallback to default fonts
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                detail_font = ImageFont.load_default()
            
            # Extract text components
            text_components = self._extract_poster_text_components(data)
            
            # Define text positions and styles based on theme
            theme_config = self._get_theme_text_config(data['theme'])
            
            # Add title
            title = text_components['title']['text']
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            title_y = height // 4
            
            # Add text with shadow effect for better readability
            shadow_color = theme_config['shadow_color']
            text_color = theme_config['text_color']
            
            # Draw shadow
            draw.text((title_x + 2, title_y + 2), title, font=title_font, fill=shadow_color)
            # Draw main text
            draw.text((title_x, title_y), title, font=title_font, fill=text_color)
            
            # Add subtitle/date
            subtitle = text_components['date']['text']
            subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (width - subtitle_width) // 2
            subtitle_y = title_y + 100
            
            draw.text((subtitle_x + 1, subtitle_y + 1), subtitle, font=subtitle_font, fill=shadow_color)
            draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=text_color)
            
            # Add venue
            venue = text_components['venue']['text']
            venue_bbox = draw.textbbox((0, 0), venue, font=detail_font)
            venue_width = venue_bbox[2] - venue_bbox[0]
            venue_x = (width - venue_width) // 2
            venue_y = subtitle_y + 60
            
            draw.text((venue_x + 1, venue_y + 1), venue, font=detail_font, fill=shadow_color)
            draw.text((venue_x, venue_y), venue, font=detail_font, fill=text_color)
            
            # Add time (if available)
            if text_components['time']['text']:
                time_text = text_components['time']['text']
                time_bbox = draw.textbbox((0, 0), time_text, font=detail_font)
                time_width = time_bbox[2] - time_bbox[0]
                time_x = (width - time_width) // 2
                time_y = venue_y + 40
                
                draw.text((time_x + 1, time_y + 1), time_text, font=detail_font, fill=shadow_color)
                draw.text((time_x, time_y), time_text, font=detail_font, fill=text_color)
            
            return poster
            
        except Exception as e:
            print(f"⚠️ Text overlay error: {e}")
            return background_image  # Return original if text overlay fails

    def _extract_poster_text_components(self, data: dict) -> dict:
        """Extract structured text components for poster"""
        return {
            "title": {
                "text": data.get('event_name', 'Event Title'),
                "type": "title",
                "editable": True,
                "font_size": 72,
                "position": {"x": "center", "y": "25%"}
            },
            "date": {
                "text": f"Date: {data.get('date', 'TBD')}",
                "type": "subtitle", 
                "editable": True,
                "font_size": 36,
                "position": {"x": "center", "y": "40%"}
            },
            "time": {
                "text": f"Time: {data.get('time', '')}",
                "type": "detail",
                "editable": True,
                "font_size": 24,
                "position": {"x": "center", "y": "50%"}
            },
            "venue": {
                "text": f"Venue: {data.get('venue', 'TBD')}",
                "type": "detail",
                "editable": True,
                "font_size": 24,
                "position": {"x": "center", "y": "45%"}
            },
            "organizer": {
                "text": f"Organized by: {data.get('organizer_name', '')}",
                "type": "footer",
                "editable": True,
                "font_size": 18,
                "position": {"x": "center", "y": "85%"}
            }
        }

    def _get_theme_text_config(self, theme: str) -> dict:
        """Get text styling configuration based on theme"""
        configs = {
            "cyberpunk": {
                "text_color": (0, 255, 255),  # Cyan
                "shadow_color": (0, 0, 0, 180),  # Black with alpha
                "font_style": "modern"
            },
            "elegant": {
                "text_color": (255, 255, 255),  # White
                "shadow_color": (0, 0, 0, 150),
                "font_style": "serif"
            },
            "professional": {
                "text_color": (255, 255, 255),  # White
                "shadow_color": (0, 0, 0, 150), 
                "font_style": "sans-serif"
            },
            "tech": {
                "text_color": (255, 255, 255),  # White
                "shadow_color": (0, 100, 255, 150),  # Blue shadow
                "font_style": "modern"
            },
            "vibrant": {
                "text_color": (255, 255, 255),  # White
                "shadow_color": (0, 0, 0, 180),
                "font_style": "bold"
            }
        }
        return configs.get(theme.lower(), configs["professional"])

    def _base64_to_image(self, base64_string: str) -> Image.Image:
        """Convert base64 string to PIL Image"""
        try:
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            
            image_data = base64.b64decode(base64_string)
            return Image.open(BytesIO(image_data))
        except Exception as e:
            print(f"❌ Base64 to image conversion error: {e}")
            # Return a default image
            return Image.new('RGB', (1024, 1024), color=(50, 50, 50))

    def _professional_fallback_poster(self, data: dict) -> dict:
        """Professional fallback for poster generation"""
        background_image = self._generate_template_background(data)
        
        # Add basic text overlay
        try:
            poster_with_text = self._add_text_overlay_to_poster(background_image, data)
        except:
            poster_with_text = background_image
        
        buffered = BytesIO()
        poster_with_text.save(buffered, format="PNG", quality=100)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        text_components = self._extract_poster_text_components(data)
        
        return {
            "poster_url": f"data:image/png;base64,{img_str}",
            "background_url": f"data:image/png;base64,{img_str}",
            "text_components": text_components,
            "prompt_used": "professional-poster-fallback",
            "status": "success",
            "model_used": "premium-template-fallback",
            "dimensions": "1024x1024",
            "file_size": f"{len(buffered.getvalue()) // 1024}KB",
            "stage": "full_poster",
            "generation_type": "full_poster"
        }

    # ============================================================================
    # POSTER BACKGROUND GENERATION (STAGE 1) - UPDATED WITH NEW HF ENDPOINT
    # ============================================================================

    def generate_poster_background(self, request_data: dict) -> dict:
        """Generate poster background only (Stage 1) - No text overlay"""
        try:
            print("🎨 Generating professional poster background...")
            
            # Choose the best model based on theme
            model_choice = self._select_poster_model(request_data['theme'])
            print(f"🤖 Selected model: {model_choice}")
            
            # **FIXED: Model availability check**
            model_name = self.poster_models[model_choice]
            if not self._check_model_availability(model_name):
                print(f"🔄 Model {model_name} not available, trying fallback...")
                # Try alternative models
                for alt_model in ["flux", "dreamshaper", "sd21", "realistic"]:
                    if alt_model != model_choice and self._check_model_availability(self.poster_models[alt_model]):
                        model_choice = alt_model
                        model_name = self.poster_models[model_choice]
                        print(f"🔄 Switching to alternative model: {model_name}")
                        break
            
            # Generate background-only image
            image = None
            model_used = "ultimate-fallback"
            
            # **FIXED: Updated SD generation with new endpoint**
            image = self._generate_with_sd_background(request_data, model_choice)
            if image:
                model_used = f"stable-diffusion-{model_choice}"
            else:
                # Fallback to template
                image = self._generate_template_background(request_data)
                model_used = "premium-template"
            
            # Apply professional enhancements
            image = self._apply_background_enhancements(image, request_data)
            
            # Convert to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG", quality=100, optimize=True)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            prompt_used = self._build_background_prompt(request_data)
            
            return {
                "background_url": f"data:image/png;base64,{img_str}",
                "prompt_used": prompt_used,
                "status": "success",
                "model_used": model_used,
                "dimensions": f"{image.width}x{image.height}",
                "file_size": f"{len(buffered.getvalue()) // 1024}KB",
                "stage": "background_only",
                "generation_type": "background"
            }
            
        except Exception as e:
            print(f"❌ Poster background generation error: {e}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            return self._professional_fallback_background(request_data)

    def _select_poster_model(self, theme: str) -> str:
        """Select the best model based on theme and use case - prioritize reliable models"""
        model_mapping = {
            "cyberpunk": "flux",  # FLUX is most reliable
            "tech": "flux",       # FLUX for tech themes
            "elegant": "dreamshaper",  # Dreamshaper for elegant visuals
            "professional": "flux", # FLUX for professional
            "minimalistic": "sd21",      # SD 2.1 is stable
            "vibrant": "dreamshaper",    # Great colors
            "artistic": "openjourney",   # Artistic style
            "nature": "flux",     # FLUX for natural themes
            "royal": "openjourney",      # Artistic royal themes
            "classic": "flux",    # FLUX for classic
            "festive": "dreamshaper"     # Vibrant celebrations
        }
        return model_mapping.get(theme.lower(), "flux")  # Default to FLUX for reliability

    def _generate_with_sd_background(self, request_data: dict, model_choice: str) -> Image.Image:
        """Generate background with Stable Diffusion models - UPDATED ENDPOINT"""
        try:
            model_name = self.poster_models[model_choice]
            prompt = self._build_sd_background_prompt(request_data)
            
            print(f"   🤖 Attempting Stable Diffusion with model: {model_name}")
            print(f"   📝 Prompt: {prompt[:200]}...")
            
            # **FIXED: Updated Hugging Face API endpoint**
            API_URL = f"{self.HF_API_BASE}/models/{model_name}"
            headers = {
                "Content-Type": "application/json"
            }
            
            if settings.HF_API_TOKEN:
                headers["Authorization"] = f"Bearer {settings.HF_API_TOKEN}"
                print(f"   🔑 HF API Token: Available ({settings.HF_API_TOKEN[:10]}...)")
            else:
                print("   ⚠️  No HF_API_TOKEN found - using public access")
            
            # **FIXED: Updated parameters for new endpoint**
            parameters = {
                "inputs": prompt,
                "parameters": {
                    "num_inference_steps": 20,
                    "guidance_scale": 7.5,
                    "width": 512,
                    "height": 512,
                    "negative_prompt": self._build_background_negative_prompt()
                },
                "options": {
                    "wait_for_model": True,
                    "use_cache": True
                }
            }
            
            print(f"   📡 Sending request to Hugging Face API...")
            print(f"   🔗 Endpoint: {API_URL}")
            start_time = time.time()
            
            # **FIXED: Better request handling with retry logic**
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = requests.post(API_URL, headers=headers, json=parameters, timeout=60)
                    
                    response_time = time.time() - start_time
                    print(f"   📊 Response status: {response.status_code}")
                    print(f"   ⏱️  Response time: {response_time:.2f}s")
                    
                    if response.status_code == 200:
                        image = Image.open(BytesIO(response.content))
                        print(f"   ✅ Successfully generated background with {model_name}")
                        return image
                    
                    elif response.status_code == 503:
                        # Model is loading
                        if attempt < max_retries - 1:
                            wait_time = (attempt + 1) * 15
                            print(f"   ⏳ Model loading, waiting {wait_time}s...")
                            time.sleep(wait_time)
                            continue
                        else:
                            print(f"   ❌ Model still loading after retries")
                            return None
                    
                    elif response.status_code == 429:
                        # Rate limited
                        print(f"   ⚠️  Rate limited, waiting 30s...")
                        time.sleep(30)
                        continue
                    
                    else:
                        print(f"   ❌ API error {response.status_code}: {response.text[:200]}")
                        # Try with a simpler request
                        if attempt == 0:
                            print("   🔄 Trying with simplified parameters...")
                            parameters["parameters"]["num_inference_steps"] = 15
                            continue
                        break
                        
                except requests.exceptions.Timeout:
                    print(f"   ⏰ Request timeout (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        time.sleep(10)
                        continue
                    else:
                        return None
                except Exception as e:
                    print(f"   ❌ Request failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(10)
                        continue
                    else:
                        return None
            
            # Try fallback model if primary fails
            if model_choice != "realistic":
                print("   🔄 Trying fallback model: realistic")
                return self._generate_with_sd_background(request_data, "realistic")
                
            return None
                
        except Exception as e:
            print(f"   ❌ SD background generation failed: {e}")
            import traceback
            print(f"   📋 Traceback: {traceback.format_exc()}")
            return None

    def _build_sd_background_prompt(self, data: dict) -> str:
        """Build Stable Diffusion prompt for poster backgrounds - IMPROVED"""
        
        # **IMPROVED: Better theme descriptions**
        theme_prompts = {
            "cyberpunk": """
            cyberpunk poster background, futuristic cityscape with neon lights, 
            holographic elements, dark atmosphere with vibrant neon accents,
            cinematic lighting, depth of field, space for text overlay,
            professional graphic design background, no text, no words,
            masterpiece, 8k resolution, ultra detailed
            """,
            
            "elegant": """
            elegant luxury poster background, minimalist design with gold accents,
            marble texture with subtle patterns, sophisticated color scheme,
            ample negative space for text, professional layout,
            premium event background, no text, clean design,
            high quality, professional graphic design
            """,
            
            "professional": """
            professional corporate event background, modern business aesthetic,
            clean geometric patterns, sophisticated color palette,
            well-organized layout with text space, executive premium design,
            conference background, no text, professional graphic design,
            clean, sharp, professional
            """,
            
            "tech": """
            modern technology background, digital circuit patterns,
            glowing data streams, futuristic tech elements,
            dark background with blue accents, space for text,
            innovation theme, no text, professional tech design,
            cybernetic patterns, data visualization
            """,
            
            "vibrant": """
            vibrant festival background, colorful abstract patterns,
            dynamic shapes and forms, energetic color scheme,
            celebration atmosphere with confetti elements,
            space for event text, no text, lively design,
            colorful, energetic, festive
            """,
            
            "minimalistic": """
            minimalist poster background, clean simple design,
            ample white space, subtle geometric elements,
            modern typography-friendly layout, sophisticated simplicity,
            space for text, no text, clean background,
            minimalist, elegant, clean
            """,
            
            "artistic": """
            artistic creative background, painterly style with texture,
            abstract artistic elements, creative composition,
            gallery exhibition style, space for text overlay,
            artistic integrity, no text, masterpiece
            """,
            
            "nature": """
            natural organic background, botanical elements with leaves,
            earthy color palette, sustainable eco-friendly design,
            natural textures, space for text, environmental theme,
            no text, organic composition
            """
        }
        
        theme = data['theme'].lower()
        theme_desc = theme_prompts.get(theme, theme_prompts["professional"])
        
        prompt = f"""
        {theme_desc}
        professional poster background for {data['event_name']} {data['event_type']},
        clean design with space for text, no text or letters,
        ultra detailed, 8k resolution, professional graphic design,
        perfect composition, background only, trending on artstation
        """
        
        return ' '.join(prompt.split())

    def _build_background_prompt(self, data: dict) -> str:
        """Generic background prompt builder"""
        return self._build_sd_background_prompt(data)

    def _build_background_negative_prompt(self) -> str:
        """Negative prompt optimized for background generation - IMPROVED"""
        return """
        text, words, letters, watermark, signature, username, logo,
        blurry, low quality, worst quality, bad quality, lowres,
        deformed, ugly, bad anatomy, poorly drawn, amateur,
        oversaturated, compression artifacts, human, person, face,
        body, limbs, crowded, busy, cluttered, messy, disorganized,
        oversaturated, underexposed, dark, bright, overexposed,
        bad art, poorly drawn, childish, cartoon, 3d render
        """

    def _generate_template_background(self, data: dict) -> Image.Image:
        """Generate template-based background as fallback - IMPROVED"""
        width, height = 1024, 1024
        
        # **IMPROVED: Better color schemes and patterns**
        color_schemes = {
            "cyberpunk": {
                "bg": (8, 12, 28), 
                "primary": (0, 255, 255), 
                "secondary": (255, 0, 255),
                "accent": (0, 200, 200)
            },
            "elegant": {
                "bg": (248, 248, 255), 
                "primary": (180, 140, 80), 
                "secondary": (200, 200, 200),
                "accent": (160, 120, 60)
            },
            "professional": {
                "bg": (240, 245, 250), 
                "primary": (0, 100, 200), 
                "secondary": (150, 150, 150),
                "accent": (0, 80, 160)
            },
            "tech": {
                "bg": (12, 20, 35), 
                "primary": (0, 200, 255), 
                "secondary": (100, 100, 255),
                "accent": (0, 150, 200)
            },
            "vibrant": {
                "bg": (255, 255, 255), 
                "primary": (255, 50, 100), 
                "secondary": (255, 200, 0),
                "accent": (200, 40, 80)
            },
            "minimalistic": {
                "bg": (255, 255, 255), 
                "primary": (100, 100, 100), 
                "secondary": (200, 200, 200),
                "accent": (150, 150, 150)
            },
            "artistic": {
                "bg": (245, 240, 230), 
                "primary": (150, 100, 200), 
                "secondary": (255, 150, 50),
                "accent": (120, 80, 160)
            },
            "nature": {
                "bg": (240, 250, 240), 
                "primary": (60, 180, 75), 
                "secondary": (139, 69, 19),
                "accent": (40, 160, 55)
            }
        }
        
        scheme = color_schemes.get(data['theme'].lower(), color_schemes["professional"])
        
        image = Image.new('RGB', (width, height), color=scheme["bg"])
        draw = ImageDraw.Draw(image)
        
        # **IMPROVED: Better geometric patterns**
        # Create subtle grid pattern
        for i in range(0, width, 80):
            alpha = 20
            line_color = tuple(max(0, c - alpha) for c in scheme["bg"])
            draw.line([(i, 0), (i, height)], fill=line_color, width=1)
        
        for j in range(0, height, 80):
            alpha = 20
            line_color = tuple(max(0, c - alpha) for c in scheme["bg"])
            draw.line([(0, j), (width, j)], fill=line_color, width=1)
        
        # Add decorative elements
        elements_count = random.randint(8, 15)
        for _ in range(elements_count):
            x = random.randint(100, width - 100)
            y = random.randint(100, height - 100)
            size = random.randint(30, 100)
            
            # Choose random shape
            shape_type = random.choice(['circle', 'square', 'triangle'])
            color = random.choice([scheme["primary"], scheme["secondary"]])
            
            if shape_type == 'circle':
                draw.ellipse([x, y, x + size, y + size], fill=color, width=0)
            elif shape_type == 'square':
                draw.rectangle([x, y, x + size, y + size], fill=color, width=0)
            elif shape_type == 'triangle':
                points = [(x, y + size), (x + size, y + size), (x + size//2, y)]
                draw.polygon(points, fill=color, width=0)
        
        # Add gradient overlay for depth
        for i in range(height):
            alpha = int(30 * (i / height))
            overlay_color = tuple(max(0, c - alpha) for c in scheme["bg"])
            draw.line([(0, i), (width, i)], fill=overlay_color, width=1)
        
        return image

    def _apply_background_enhancements(self, image: Image.Image, request_data: dict) -> Image.Image:
        """Apply enhancements optimized for poster backgrounds - IMPROVED"""
        try:
            # Ensure proper size
            if image.size[0] < 1024 or image.size[1] < 1024:
                image = image.resize((1024, 1024), Image.Resampling.LANCZOS)
            
            # **IMPROVED: Theme-specific enhancements**
            theme = request_data['theme'].lower()
            
            if theme in ['cyberpunk', 'tech']:
                # Enhance contrast and saturation for tech themes
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.15)
                
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(1.10)
                
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.2)
                
            elif theme in ['elegant', 'professional', 'minimalistic']:
                # Subtle enhancements for professional themes
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.08)
                
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(1.05)
                
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.1)
                
            else:
                # Default enhancements
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.10)
                
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(1.05)
                
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.1)
            
            # Apply subtle noise reduction
            image = image.filter(ImageFilter.SMOOTH)
            
        except Exception as e:
            print(f"⚠️ Background enhancement failed: {e}")
            
        return image

    def _professional_fallback_background(self, data: dict) -> dict:
        """Professional fallback for background generation"""
        image = self._generate_template_background(data)
        buffered = BytesIO()
        image.save(buffered, format="PNG", quality=100)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "background_url": f"data:image/png;base64,{img_str}",
            "prompt_used": "professional-poster-background-fallback",
            "status": "success", 
            "model_used": "premium-template-fallback",
            "dimensions": "1024x1024",
            "file_size": f"{len(buffered.getvalue()) // 1024}KB",
            "stage": "background_only",
            "generation_type": "background"
        }

    # ============================================================================
    # EMAIL GENERATION
    # ============================================================================

    def generate_email_content(self, request_data: dict) -> dict:
        """Generate professional email content with advanced AI"""
        print("=" * 60)
        print("📧 EMAIL GENERATION STARTED")
        print(f"   Event: {request_data.get('event_name')}")
        print(f"   Groq client available: {self.groq_client is not None}")
        
        if not self.groq_client:
            print("❌ FALLBACK: Groq client not available")
            result = self._professional_fallback_email_generation(request_data)
            result["model_used"] = "fallback-no-groq-client"
            return result
        
        print("🚀 USING GROQ AI: Attempting generation...")
        
        try:
            prompt = self._build_professional_email_prompt(request_data)
            print(f"   ✅ Prompt built ({len(prompt)} chars)")
            
            print("   📡 Sending request to Groq API...")
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are a senior event marketing strategist and professional copywriter with 15+ years of experience.
                        You specialize in creating compelling, conversion-optimized email content for college events.
                        
                        CRITICAL FORMATTING RULES:
                        - ALWAYS format your response EXACTLY as: SUBJECT: [catchy subject line] BODY: [professional email body]
                        - The email body should be properly structured with clear sections
                        - Use professional formatting with appropriate spacing
                        - Include a strong call-to-action
                        - Make it engaging and persuasive
                        - Maintain the specified tone throughout"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.1-8b-instant",
                temperature=0.8,
                max_tokens=1500,
                top_p=0.9
            )
            
            print("   ✅ GROQ API CALL SUCCESSFUL!")
            response_text = chat_completion.choices[0].message.content
            print(f"   📨 Raw AI response received ({len(response_text)} chars)")
            
            # Parse the response
            result = self._parse_professional_email_response(response_text, request_data)
            
            print(f"   ✅ FINAL RESULT:")
            print(f"   - Model: {result.get('model_used', 'unknown')}")
            print(f"   - Subject: {result.get('subject', 'N/A')}")
            print(f"   - Status: {result.get('status', 'unknown')}")
            print("=" * 60)
            
            return result
            
        except Exception as e:
            print(f"   ❌ GROQ GENERATION FAILED: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            
            result = self._professional_fallback_email_generation(request_data)
            result["model_used"] = f"fallback-groq-error"
            return result

    def _build_professional_email_prompt(self, data: dict) -> str:
        """Build professional-grade prompt for email generation"""
        
        # Advanced tone descriptions
        tone_guides = {
            "formal": "highly professional, corporate tone, formal language, respectful, business-appropriate",
            "casual": "friendly, conversational tone, approachable language, warm and inviting", 
            "enthusiastic": "energetic, exciting tone, persuasive language, creates urgency and excitement",
            "informative": "clear, detailed, educational tone, focuses on value and benefits, professional yet accessible",
            "fun": "playful, engaging tone, creative language, entertaining and memorable"
        }
        
        tone_guide = tone_guides.get(data['tone'].lower(), "professional and engaging")
        
        # Event type specific language
        event_language = {
            "workshop": "hands-on learning experience, practical skills, interactive session, expert guidance",
            "conference": "premier gathering, industry insights, networking opportunities, thought leadership",
            "social": "memorable gathering, community building, fun activities, social connection",
            "sports": "competitive spirit, athletic excellence, team camaraderie, sportsmanship", 
            "cultural": "cultural celebration, diverse perspectives, artistic expression, community heritage",
            "tech": "cutting-edge technology, innovation showcase, future trends, technical excellence",
            "seminar": "educational opportunity, expert knowledge, professional development, learning growth",
            "competition": "competitive challenge, skill demonstration, achievement recognition, excellence pursuit"
        }
        
        event_lang = event_language.get(data['event_type'].lower(), "professional gathering")
        
        key_points_text = ""
        if data['key_points']:
            key_points_text = "KEY HIGHLIGHTS & BENEFITS:\n" + "\n".join([f"• {point}" for point in data['key_points']])
        else:
            key_points_text = "KEY HIGHLIGHTS:\n• Valuable learning and networking opportunities\n• Expert insights and practical knowledge\n• Memorable experiences and connections"
        
        professional_prompt = f"""
Create a PROFESSIONAL GRADE event email that drives registrations and engagement.

EVENT BRIEF:
- EVENT: {data['event_name']}
- TYPE: {data['event_type'].title()} - {event_lang}
- DATE: {data['date']}
- TIME: {data['time']}
- VENUE: {data['venue']}
- TARGET: {data['target_audience']}
- TONE: {data['tone'].title()} - {tone_guide}
- ORGANIZER: {data.get('organizer_name', 'Event Organizing Team')}
- CONTACT: {data.get('contact_info', 'Please reply to this email for inquiries')}

{key_points_text}

PROFESSIONAL REQUIREMENTS:
1. SUBJECT LINE: Must be compelling, under 60 characters, creates curiosity or urgency
2. OPENING: Strong hook that grabs attention immediately
3. VALUE PROPOSITION: Clear benefits and what attendees will gain
4. EVENT DETAILS: Well-organized, easy to scan information
5. CALL-TO-ACTION: Clear, compelling, and repeated
6. CLOSING: Professional sign-off with contact information
7. FORMATTING: Proper spacing, bullet points where appropriate, professional structure

TONE & STYLE: {tone_guide}
AUDIENCE: Speaking to {data['target_audience']}

Make this email impossible to ignore and highly likely to drive registrations.
"""
        return professional_prompt

    def _parse_professional_email_response(self, response: str, data: dict) -> dict:
        """Parse professional AI response into structured email"""
        print("   🔍 PARSING AI RESPONSE...")
        print(f"   Raw response type: {type(response)}")
        print(f"   Raw response length: {len(response)}")
        print(f"   Raw response content:\n--- START ---\n{response}\n--- END ---")
        
        try:
            lines = response.split('\n')
            print(f"   Number of lines: {len(lines)}")
            
            subject = ""
            body_lines = []
            
            in_body = False
            for i, line in enumerate(lines):
                line = line.strip()
                print(f"   Line {i}: '{line}'")
                
                if line.startswith('SUBJECT:') and not subject:
                    subject = line.replace('SUBJECT:', '').strip()
                    # Clean up subject - remove any extra labels
                    subject = subject.split('BODY:')[0].strip()
                    print(f"   ✅ FOUND SUBJECT: '{subject}'")
                elif line.startswith('BODY:'):
                    in_body = True
                    body_content = line.replace('BODY:', '').strip()
                    if body_content:
                        body_lines.append(body_content)
                    print(f"   ✅ ENTERED BODY SECTION")
                elif in_body and line:
                    body_lines.append(line)
                elif not in_body and line and not subject:
                    print(f"   ⚠️  Line before body (no subject found yet): '{line}'")
            
            body = '\n'.join(body_lines) if body_lines else response
            
            print(f"   PARSING RESULTS:")
            print(f"   - Subject found: '{subject}'")
            print(f"   - Body lines: {len(body_lines)}")
            print(f"   - In body flag: {in_body}")
            
            # Enhanced fallback if parsing failed
            if not subject:
                print("   ❌ NO SUBJECT FOUND IN RESPONSE")
                subject = self._generate_professional_subject(data)
                print(f"   Using generated subject: '{subject}'")
            
            if not body.strip():
                print("   ❌ NO BODY FOUND IN RESPONSE")
                body = self._professional_email_template(data)
                print("   Using fallback template for body")
            
            # Ensure professional formatting
            body = self._enhance_email_formatting(body)
            
            print(f"   ✅ FINAL PARSED RESULT:")
            print(f"   - Subject: {subject}")
            print(f"   - Body length: {len(body)}")
            
            return {
                "subject": subject,
                "body": body,
                "status": "success",
                "model_used": "llama-3.1-8b-instant"
            }
            
        except Exception as e:
            print(f"   ❌ PARSING ERROR: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return self._professional_fallback_email_generation(data)

    def _generate_professional_subject(self, data: dict) -> str:
        """Generate professional subject lines"""
        event_name = data['event_name']
        event_type = data['event_type']
        
        subject_templates = {
            "workshop": [
                f"Master New Skills: {event_name} Workshop",
                f"Hands-On Learning: {event_name} - Register Now!",
                f"Expert-Led Workshop: {event_name} - Limited Spots"
            ],
            "conference": [
                f"Don't Miss: {event_name} Conference 2024",
                f"Industry Insights: {event_name} - Secure Your Seat", 
                f"Network & Learn: {event_name} Conference Invitation"
            ],
            "social": [
                f"You're Invited: {event_name} Social Gathering",
                f"Join the Celebration: {event_name} - RSVP Today!",
                f"Connect & Celebrate: {event_name} Event"
            ]
        }
        
        templates = subject_templates.get(event_type, [
            f"Important: {event_name} - Your Invitation",
            f"Don't Miss Out: {event_name} Event", 
            f"Exclusive Invitation: {event_name}"
        ])
        
        return random.choice(templates)

    def _enhance_email_formatting(self, body: str) -> str:
        """Enhance email formatting for professional appearance"""
        # Ensure proper paragraph spacing and structure
        lines = body.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.isspace():
                # Capitalize first letter of each paragraph
                if line and line[0].islower():
                    line = line[0].upper() + line[1:]
                formatted_lines.append(line)
        
        return '\n\n'.join(formatted_lines)

    def _professional_fallback_email_generation(self, data: dict) -> dict:
        """Professional fallback email generation"""
        return {
            "subject": self._generate_professional_subject(data),
            "body": self._professional_email_template(data),
            "status": "success",
            "model_used": "professional-fallback-template"
        }

    def _professional_email_template(self, data: dict) -> str:
        """Professional email template"""
        organizer = data.get('organizer_name', 'Event Organizing Team')
        contact = data.get('contact_info', '')
        
        # Professional email structure
        return f"""
Dear Attendee,

You are cordially invited to an exceptional event that promises valuable insights and memorable experiences.

**EVENT DETAILS**
🎯 Event: {data['event_name']}
📅 Date: {data['date']}
⏰ Time: {data['time']}
📍 Venue: {data['venue']}
🎪 Type: {data['event_type'].title()}

**ABOUT THIS EVENT**
This {data['event_type']} is specially curated for {data['target_audience']} and offers a unique opportunity for growth, networking, and professional development.

**KEY HIGHLIGHTS**
{chr(10).join(f'• {point}' for point in data['key_points']) if data['key_points'] else '''• Expert-led sessions and workshops
• Valuable networking opportunities  
• Cutting-edge insights and knowledge
• Practical skills and takeaways'''}

**WHY ATTEND?**
- Gain valuable knowledge and skills
- Network with peers and experts
- Enhance your professional profile
- Discover new opportunities

**REGISTRATION**
Please confirm your attendance at your earliest convenience to secure your spot.

We are committed to delivering an exceptional experience and look forward to welcoming you to what promises to be an impactful event.

Best regards,

{organizer}
{contact if contact else ''}

---
This is an automated invitation. For any inquiries, please respond to this email.
"""

    # ============================================================================
    # INVITATION GENERATION (TWO-STAGE APPROACH)
    # ============================================================================

    def generate_invitation(self, request_data: dict) -> dict:
        """Generate invitation with separate design and text components"""
        try:
            print("🎟️ Generating premium invitation with separate components...")
            
            # Generate invitation text
            invitation_result = self._generate_premium_invitation_text(request_data)
            
            # Generate invitation design (background)
            design_result = self.generate_poster_background({
                **request_data,
                'theme': request_data.get('theme', 'elegant'),
                'event_type': 'invitation'
            })
            
            # Generate QR code if needed
            qr_code_url = self._generate_premium_qr_code(request_data) if request_data.get('rsvp_email') else None
            
            return {
                "invitation_text": invitation_result['invitation_text'],
                "formatted_invitation": invitation_result['formatted_invitation'],
                "design_background": design_result['background_url'],
                "qr_code_url": qr_code_url,
                "text_components": self._extract_invitation_text_components(invitation_result['formatted_invitation']),
                "status": "success",
                "model_used": f"{invitation_result['model_used']}+{design_result['model_used']}"
            }
            
        except Exception as e:
            print(f"❌ Premium invitation generation error: {e}")
            return self._professional_fallback_invitation_generation(request_data)

    def _extract_invitation_text_components(self, invitation_text: str) -> dict:
        """Extract structured text components for easy editing"""
        lines = [line.strip() for line in invitation_text.split('\n') if line.strip()]
        
        components = {
            "title": "",
            "subtitle": "", 
            "date": "",
            "time": "",
            "venue": "",
            "description": [],
            "rsvp_info": "",
            "organizer": ""
        }
        
        # Simple parsing logic - you can enhance this based on your invitation format
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(word in line_lower for word in ['request', 'pleasure', 'honor', 'invite']):
                components['title'] = line
            elif any(word in line_lower for word in ['date:']):
                components['date'] = line
            elif any(word in line_lower for word in ['time:']):
                components['time'] = line
            elif any(word in line_lower for word in ['venue:']):
                components['venue'] = line
            elif any(word in line_lower for word in ['rsvp', 'respond']):
                components['rsvp_info'] = line
            elif any(word in line_lower for word in ['regards', 'sincerely']):
                if i + 1 < len(lines):
                    components['organizer'] = lines[i + 1]
            elif line and not line.startswith('**') and len(line) > 10:
                components['description'].append(line)
        
        return components

    def _generate_premium_invitation_text(self, data: dict) -> dict:
        """Generate premium professional invitation text using advanced AI"""
        if not self.groq_client:
            template_result = self._premium_invitation_template(data)
            return {
                "invitation_text": template_result,
                "formatted_invitation": template_result,
                "model_used": "premium-template"
            }
        
        prompt = self._build_premium_invitation_prompt(data)
        
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are a luxury event planner and professional invitation writer with expertise in creating exquisite, high-end invitations for prestigious events.
                        
                        Create invitations that:
                        - Convey exclusivity and importance
                        - Use elegant, sophisticated language
                        - Maintain perfect formatting and structure
                        - Include all essential details beautifully
                        - Create a sense of anticipation and excitement
                        - Use proper invitation etiquette and formatting
                        
                        FORMAT REQUIREMENTS:
                        - Use elegant spacing and structure
                        - Include proper salutation and closing
                        - Make details easy to read and beautiful
                        - Create a memorable first impression"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                max_tokens=1200,
                top_p=0.9
            )
            
            invitation_text = chat_completion.choices[0].message.content
            formatted_invitation = self._format_premium_invitation(invitation_text, data)
            
            return {
                "invitation_text": invitation_text,
                "formatted_invitation": formatted_invitation,
                "model_used": "llama-3.1-8b-instant"
            }
        except Exception as e:
            print(f"❌ Premium invitation generation error: {e}")
            template_result = self._premium_invitation_template(data)
            return {
                "invitation_text": template_result,
                "formatted_invitation": template_result,
                "model_used": "premium-fallback"
            }

    def _build_premium_invitation_prompt(self, data: dict) -> str:
        """Build premium-grade prompt for invitation generation"""
        
        # Premium tone descriptions
        tone_descriptions = {
            "formal": "highly formal, black-tie appropriate, sophisticated, traditional elegance",
            "semi-formal": "elegant yet approachable, business professional, refined but welcoming", 
            "casual": "warm and friendly, approachable elegance, comfortable sophistication",
            "festive": "celebratory and joyful, elegant excitement, sophisticated celebration",
            "corporate": "professional excellence, business elegance, executive sophistication"
        }
        
        tone_desc = tone_descriptions.get(data.get('tone', 'formal').lower(), "elegant and sophisticated")
        
        rsvp_info = ""
        if data.get('rsvp_deadline') and data.get('rsvp_email'):
            rsvp_info = f"Kindly respond by {data['rsvp_deadline']} to {data['rsvp_email']}"
        elif data.get('rsvp_deadline'):
            rsvp_info = f"Please RSVP by {data['rsvp_deadline']}"
        elif data.get('rsvp_email'):
            rsvp_info = f"RSVP to: {data['rsvp_email']}"
        else:
            rsvp_info = "Your presence is requested - please confirm attendance"
        
        dress_code = data.get('dress_code', 'Elegant Attire')
        special_instructions = data.get('special_instructions', '')
        organizer = data.get('organizer_name', 'The Event Organizing Committee')
        
        premium_prompt = f"""
Create an EXQUISITE and PROFESSIONAL event invitation worthy of a high-profile gathering.

EVENT ESSENCE:
- EVENT: {data['event_name']}
- TYPE: {data['event_type'].title()} Event
- DATE: {data['date']}
- TIME: {data['time']}
- VENUE: {data['venue']}
- DRESS CODE: {dress_code}
- RSVP: {rsvp_info}
- ORGANIZER: {organizer}
- SPECIAL NOTES: {special_instructions if special_instructions else 'An unforgettable experience awaits'}
- TONE: {tone_desc}

**CRITICAL REQUIREMENTS:**
- Generate ONLY the invitation TEXT CONTENT - no design specifications
- NO font choices, color schemes, paper quality, or printing instructions
- NO design or formatting recommendations  
- Focus on elegant wording, proper etiquette, and beautiful language
- Create content that can be used in any design template
- Include all essential event information in a sophisticated manner

PREMIUM CONTENT REQUIREMENTS:
1. ELEGANT OPENING: Grand salutation that conveys importance
2. EVENT ANNOUNCEMENT: Beautiful presentation of event name and purpose  
3. DETAILS SECTION: Artfully organized essential information
4. RSVP ELEGANCE: Sophisticated response request
5. CLOSING: Warm yet professional conclusion
6. FORMATTING: Perfect spacing and elegant structure

Create an invitation that makes recipients feel honored to be invited and excited to attend.
The language should be refined, the structure should be impeccable, and the overall impression should be one of exclusivity and importance.

**REMEMBER: Generate TEXT CONTENT only - no design specifications.**
"""
        return premium_prompt

    def _format_premium_invitation(self, invitation_text: str, data: dict) -> str:
        """Format invitation text with premium styling"""
        try:
            # Clean and enhance the formatting
            lines = [line.strip() for line in invitation_text.split('\n') if line.strip()]
            formatted_lines = []
            
            for line in lines:
                if line and not line.isspace():
                    # Add elegant spacing for sections
                    if any(keyword in line.lower() for keyword in ['cordially', 'pleasure', 'honor', 'delighted']):
                        if formatted_lines:  # Add extra space before main invitation
                            formatted_lines.append('')
                    formatted_lines.append(line)
            
            # Ensure proper closing structure
            if not any(keyword in formatted_lines[-1].lower() for keyword in ['regards', 'sincerely', 'gratefully']):
                formatted_lines.append('')
                formatted_lines.append('We look forward to celebrating with you,')
                formatted_lines.append('')
                formatted_lines.append(data.get('organizer_name', 'The Event Hosts'))
            
            return '\n'.join(formatted_lines)
            
        except Exception as e:
            print(f"⚠️ Premium invitation formatting error: {e}")
            return invitation_text

    def _premium_invitation_template(self, data: dict) -> str:
        """Premium invitation template for fallback"""
        organizer = data.get('organizer_name', 'The Event Organizing Committee')
        rsvp_info = ""
        
        if data.get('rsvp_deadline') and data.get('rsvp_email'):
            rsvp_info = f"Kindly honor us with your response by {data['rsvp_deadline']}\nEmail: {data['rsvp_email']}"
        elif data.get('rsvp_deadline'):
            rsvp_info = f"Please RSVP by {data['rsvp_deadline']}"
        elif data.get('rsvp_email'):
            rsvp_info = f"RSVP Email: {data['rsvp_email']}"
        else:
            rsvp_info = "Your gracious response is requested at your earliest convenience"
        
        dress_code = data.get('dress_code', 'Elegant Attire')
        special_instructions = data.get('special_instructions', 'Join us for an evening of inspiration, connection, and celebration.')
        
        return f"""
With great pleasure,

{organizer}

requests the honor of your presence at

✨ {data['event_name'].upper()} ✨

A distinguished {data['event_type'].title()} gathering

📅 Date: {data['date']}
⏰ Time: {data['time']}
📍 Venue: {data['venue']}
👔 Attire: {dress_code}

{special_instructions}

{rsvp_info}

We eagerly anticipate the pleasure of your company
at this memorable occasion.

With warmest regards,
{organizer}
"""

    def _generate_premium_qr_code(self, data: dict) -> str:
        """Generate premium QR code with professional styling"""
        try:
            if not data.get('rsvp_email'):
                return None
                
            qr_content = f"mailto:{data['rsvp_email']}?subject=RSVP for {data['event_name']}&body=Dear Organizers,%0A%0AI am delighted to confirm my attendance for {data['event_name']} on {data['date']}.%0A%0AWith appreciation,"
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=20,
                border=6,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            
            # Create premium QR code with elegant styling
            qr_img = qr.make_image(fill_color="#2C3E50", back_color="#F8F9FA")
            
            # Add elegant border
            border_size = 20
            bordered_img = Image.new('RGB', 
                                   (qr_img.size[0] + border_size*2, qr_img.size[1] + border_size*2), 
                                   color="#F8F9FA")
            bordered_img.paste(qr_img, (border_size, border_size))
            
            # Add decorative corner elements
            draw = ImageDraw.Draw(bordered_img)
            corner_color = "#2C3E50"
            corner_length = 15
            thickness = 3
            
            # Draw corners
            corners = [
                (border_size//2, border_size//2),  # Top-left
                (bordered_img.width - border_size//2, border_size//2),  # Top-right
                (border_size//2, bordered_img.height - border_size//2),  # Bottom-left
                (bordered_img.width - border_size//2, bordered_img.height - border_size//2)  # Bottom-right
            ]
            
            for x, y in corners:
                # Horizontal line
                draw.line([(x, y), (x + corner_length, y)], fill=corner_color, width=thickness)
                # Vertical line
                draw.line([(x, y), (x, y + corner_length)], fill=corner_color, width=thickness)
            
            buffered = BytesIO()
            bordered_img.save(buffered, format="PNG", quality=100)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            print(f"⚠️ Premium QR code generation error: {e}")
            return None

    def _professional_fallback_invitation_generation(self, request_data: dict) -> dict:
        """Professional fallback for invitation generation"""
        invitation_text = self._premium_invitation_template(request_data)
        design_background = self._generate_template_background(request_data)
        
        buffered = BytesIO()
        design_background.save(buffered, format="PNG", quality=100)
        design_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "invitation_text": invitation_text,
            "formatted_invitation": invitation_text,
            "design_background": f"data:image/png;base64,{design_str}",
            "qr_code_url": self._generate_premium_qr_code(request_data) if request_data.get('rsvp_email') else None,
            "text_components": self._extract_invitation_text_components(invitation_text),
            "status": "success",
            "model_used": "premium-fallback-template"
        }

    # ============================================================================
    # UPDATED API ENDPOINT HANDLER
    # ============================================================================

    def handle_poster_generation(self, request_data: dict) -> dict:
        """Main handler for poster generation requests"""
        generation_type = request_data.get('generation_type', 'background')
        
        print(f"🚀 Poster Generation Request:")
        print(f"   - Type: {generation_type}")
        print(f"   - Event: {request_data.get('event_name')}")
        print(f"   - Theme: {request_data.get('theme')}")
        
        if generation_type == 'background':
            result = self.generate_poster_background(request_data)
            result['generation_type'] = 'background'
        else:
            result = self.generate_poster(request_data)
            result['generation_type'] = generation_type
        
        return result

# Global instance
ai_service = AIService()