import os
import requests
import base64
from io import BytesIO
from groq import Groq
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import qrcode
import time
import random
import math
from datetime import datetime
from ..core.config import settings

class AIService:
    def __init__(self):
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
        
    def generate_email_content(self, request_data: dict) -> dict:
        """Generate professional email content with advanced AI"""
        if not self.groq_client:
            return self._professional_fallback_email_generation(request_data)
        
        prompt = self._build_professional_email_prompt(request_data)
        
        try:
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
                model="llama-3.1-70b-versatile",
                temperature=0.8,
                max_tokens=1500,
                top_p=0.9
            )
            
            response_text = chat_completion.choices[0].message.content
            return self._parse_professional_email_response(response_text, request_data)
            
        except Exception as e:
            print(f"Professional email generation error: {e}")
            return self._professional_fallback_email_generation(request_data)

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
        try:
            lines = response.split('\n')
            subject = ""
            body_lines = []
            
            in_body = False
            for line in lines:
                line = line.strip()
                if line.startswith('SUBJECT:') and not subject:
                    subject = line.replace('SUBJECT:', '').strip()
                    # Clean up subject - remove any extra labels
                    subject = subject.split('BODY:')[0].strip()
                elif line.startswith('BODY:'):
                    in_body = True
                    body_content = line.replace('BODY:', '').strip()
                    if body_content:
                        body_lines.append(body_content)
                elif in_body and line:
                    body_lines.append(line)
            
            body = '\n'.join(body_lines) if body_lines else response
            
            # Enhanced fallback if parsing failed
            if not subject:
                subject = self._generate_professional_subject(data)
            if not body.strip():
                body = self._professional_email_template(data)
            
            # Ensure professional formatting
            body = self._enhance_email_formatting(body)
            
            return {
                "subject": subject,
                "body": body,
                "status": "success",
                "model_used": "llama-3.1-70b-professional"
            }
        except Exception as e:
            print(f"Professional email parsing error: {e}")
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

    def generate_invitation(self, request_data: dict) -> dict:
        """Generate premium professional invitation with QR code"""
        try:
            print("🎟️ Generating premium professional invitation...")
            
            # Generate premium invitation text
            invitation_result = self._generate_premium_invitation_text(request_data)
            
            # Generate premium QR code
            qr_code_url = self._generate_premium_qr_code(request_data)
            
            # Generate invitation design using DALL-E 3
            invitation_design = self._generate_dalle3_invitation_design(request_data, invitation_result['invitation_text'])
            
            return {
                "invitation_text": invitation_result['invitation_text'],
                "formatted_invitation": invitation_result['formatted_invitation'],
                "qr_code_url": qr_code_url,
                "invitation_design": invitation_design,
                "status": "success",
                "model_used": invitation_result['model_used']
            }
            
        except Exception as e:
            print(f"Premium invitation generation error: {e}")
            return self._professional_fallback_invitation_generation(request_data)

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
                model="llama-3.1-70b-versatile",
                temperature=0.7,
                max_tokens=1200,
                top_p=0.9
            )
            
            invitation_text = chat_completion.choices[0].message.content
            formatted_invitation = self._format_premium_invitation(invitation_text, data)
            
            return {
                "invitation_text": invitation_text,
                "formatted_invitation": formatted_invitation,
                "model_used": "llama-3.1-70b-premium"
            }
        except Exception as e:
            print(f"Premium invitation generation error: {e}")
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

PREMIUM REQUIREMENTS:
1. ELEGANT OPENING: Grand salutation that conveys importance
2. EVENT ANNOUNCEMENT: Beautiful presentation of event name and purpose
3. DETAILS SECTION: Artfully organized essential information
4. RSVP ELEGANCE: Sophisticated response request
5. CLOSING: Warm yet professional conclusion
6. FORMATTING: Perfect spacing, elegant structure, luxury presentation

Create an invitation that makes recipients feel honored to be invited and excited to attend.
The language should be refined, the structure should be impeccable, and the overall impression should be one of exclusivity and importance.
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
            print(f"Premium invitation formatting error: {e}")
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
            print(f"Premium QR code generation error: {e}")
            return None

    def _generate_dalle3_invitation_design(self, data: dict, invitation_text: str) -> str:
        """Generate premium invitation design using DALL-E 3 through Groq"""
        try:
            if not self.groq_client:
                return self._generate_fallback_invitation_design(data, invitation_text)
            
            # Build premium DALL-E 3 prompt for invitation card
            prompt = self._build_dalle3_invitation_prompt(data, invitation_text)
            
            print(f"🎨 Generating DALL-E 3 invitation design with prompt: {prompt[:100]}...")
            
            # Generate image using DALL-E 3 via Groq
            response = self.groq_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Get the image URL from response
            image_url = response.data[0].url
            
            # Download and convert to base64
            image_response = requests.get(image_url)
            image = Image.open(BytesIO(image_response.content))
            
            # Apply premium enhancements
            image = self._apply_premium_enhancements(image, crisp=data.get('crisp_mode', False))
            
            # Convert to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG", quality=100)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"DALL-E 3 invitation generation error: {e}")
            return self._generate_fallback_invitation_design(data, invitation_text)

    def _build_dalle3_invitation_prompt(self, data: dict, invitation_text: str) -> str:
        """Build premium DALL-E 3 prompt for invitation design"""
        
        # Theme-based design descriptions
        theme_designs = {
            "elegant": """
            elegant luxury invitation card, gold foil embossing, marble and crystal textures,
            sophisticated modern typography, minimalist luxury design with ample white space,
            black and gold color scheme with deep navy accents, professional corporate design,
            high-end exclusive event, award-winning invitation design
            """,
            
            "royal": """
            royal premium invitation, regal design with crown elements, deep purple and gold colors,
            velvet texture background, ornate borders with intricate patterns, luxurious typography,
            majestic and sophisticated, traditional luxury with modern elegance
            """,
            
            "modern": """
            modern minimalist invitation, clean geometric design, sans-serif typography,
            bold color blocks with ample white space, contemporary aesthetic,
            professional grid-based layout, refined color palette with single accent color
            """,
            
            "classic": """
            classic traditional invitation, vintage design with ornate borders,
            serif typography with elegant spacing, parchment paper texture,
            traditional color scheme with deep reds and golds, timeless elegance
            """,
            
            "festive": """
            festive celebration invitation, vibrant colors with confetti elements,
            joyful and energetic design, party atmosphere with celebration motifs,
            bold typography with fun elements, colorful and engaging layout
            """,
            
            "professional": """
            professional corporate invitation, business conference design,
            clean modern layout with perfect alignment, sophisticated typography,
            brand-aligned design system, executive luxury event
            """
        }
        
        theme_desc = theme_designs.get(data.get('theme', 'elegant').lower(), theme_designs["elegant"])
        
        # Event type specific elements
        event_elements = {
            "workshop": "educational workshop design, creative learning elements, interactive session visuals",
            "conference": "professional conference design, networking event visuals, speaker session elements",
            "social": "social gathering design, community celebration elements, fun engaging visuals",
            "sports": "sports event design, athletic competition elements, team spirit visuals",
            "cultural": "cultural festival design, traditional artistic elements, diverse celebration visuals",
            "tech": "technology conference design, digital innovation elements, futuristic tech visuals"
        }
        
        event_elem = event_elements.get(data['event_type'].lower(), "professional event design")
        
        prompt = f"""
        Create a premium professional invitation card design for a {data['event_type']} event.
        
        EVENT: {data['event_name']}
        DESIGN STYLE: {theme_desc}
        EVENT ELEMENTS: {event_elem}
        KEY DETAILS: Date: {data['date']}, Time: {data['time']}, Venue: {data['venue']}
        
        DESIGN REQUIREMENTS:
        - Premium luxury invitation card design
        - Elegant and sophisticated layout
        - Professional typography with clear hierarchy
        - Appropriate color scheme for the theme
        - High-quality visual elements
        - Perfect balance and composition
        - No text overlay needed (will be added separately)
        - 3D realistic rendering with proper lighting
        - Award-winning design quality
        
        Create an invitation that looks expensive, professional, and makes recipients feel special.
        The design should be memorable and reflect the importance of the event.
        """
        
        return ' '.join(prompt.split())

    def _generate_fallback_invitation_design(self, data: dict, invitation_text: str) -> str:
        """Fallback invitation design generation"""
        try:
            # Create A4 size invitation (2480x3508 pixels at 300 DPI)
            width, height = 2480, 3508
            image = Image.new('RGB', (width, height), color='#FFFFFF')
            draw = ImageDraw.Draw(image)
            
            # Load premium fonts
            fonts = self._load_premium_fonts(width)
            
            # Color scheme based on theme
            colors = self._get_premium_color_scheme(data.get('theme', 'elegant'))
            
            # Draw premium background with gradient
            self._draw_premium_background(draw, width, height, colors)
            
            # Add decorative elements
            self._add_premium_decorations(draw, width, height, colors)
            
            # Render invitation text beautifully
            self._render_premium_invitation_text(draw, width, height, data, invitation_text, fonts, colors)
            
            # Convert to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG", quality=100)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"Fallback invitation design generation error: {e}")
            return None

    def _professional_fallback_invitation_generation(self, data: dict) -> dict:
        """Professional fallback invitation generation"""
        invitation_text = self._premium_invitation_template(data)
        return {
            "invitation_text": invitation_text,
            "formatted_invitation": invitation_text,
            "qr_code_url": self._generate_premium_qr_code(data) if data.get('rsvp_email') else None,
            "invitation_design": None,
            "status": "success",
            "model_used": "premium-fallback-template"
        }

    def generate_poster(self, request_data: dict) -> dict:
        """Generate professional event poster using DALL-E 3 as primary choice"""
        try:
            print("🎨 Generating premium professional poster with DALL-E 3...")
            
            # Generate with DALL-E 3 as first choice
            image = None
            model_used = "dall-e-3-premium"
            crisp_mode = bool(request_data.get('crisp_mode', False))
            
            # 1. Primary: Try DALL-E 3 through Groq
            image = self._generate_with_dalle3_premium(request_data)
            if not image:
                # 2. Fallback: Try Stable Diffusion XL
                image = self._generate_with_sdxl_premium(request_data)
                if image:
                    model_used = "stable-diffusion-xl-premium"
                else:
                    # 3. Ultimate fallback: Premium template
                    image = self._generate_premium_template_poster(request_data)
                    model_used = "premium-template"
            
            # Apply premium enhancements
            image = self._apply_premium_enhancements(image, crisp=crisp_mode)
            
            # Add professional text overlay
            image = self._add_premium_text_overlay(image, request_data)
            
            # Final quality check and optimization
            image = self._finalize_premium_poster(image)
            
            # Convert to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG", quality=100, optimize=True)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            prompt_used = self._build_dalle3_poster_prompt(request_data)
            
            return {
                "image_url": f"data:image/png;base64,{img_str}",
                "prompt_used": prompt_used,
                "status": "success",
                "model_used": model_used,
                "dimensions": f"{image.width}x{image.height}",
                "file_size": f"{len(buffered.getvalue()) // 1024}KB"
            }
            
        except Exception as e:
            print(f"Premium poster generation error: {e}")
            # Ultimate professional fallback
            image = self._generate_premium_template_poster(request_data)
            buffered = BytesIO()
            image.save(buffered, format="PNG", quality=100)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "image_url": f"data:image/png;base64,{img_str}",
                "prompt_used": "premium-event-poster-design",
                "status": "success",
                "model_used": "ultimate-premium-fallback"
            }

    def _generate_with_dalle3_premium(self, request_data: dict) -> Image.Image:
        """Generate premium poster using DALL-E 3 through Groq"""
        try:
            if not self.groq_client:
                return None
                
            prompt = self._build_dalle3_poster_prompt(request_data)
            
            print(f"🚀 Generating DALL-E 3 poster with prompt: {prompt[:100]}...")
            
            # Generate image using DALL-E 3 via Groq
            response = self.groq_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="hd",  # Use HD for best quality
                n=1,
            )
            
            # Get the image URL from response
            image_url = response.data[0].url
            
            # Download the image
            image_response = requests.get(image_url)
            image = Image.open(BytesIO(image_response.content))
            
            print("✅ Successfully generated premium poster with DALL-E 3")
            return image
            
        except Exception as e:
            print(f"DALL-E 3 Premium generation failed: {e}")
            return None

    def _build_dalle3_poster_prompt(self, data: dict) -> str:
        """Build premium-grade prompt for DALL-E 3 poster generation"""
        
        # Premium theme descriptions optimized for DALL-E 3
        theme_prompts = {
            "cyberpunk": """
            cyberpunk event poster masterpiece, neon noir aesthetic, futuristic megacityscape,
            vibrant neon color palette (electric blue, hot pink, lime green), detailed cyberpunk architecture,
            atmospheric lighting with volumetric fog, cinematic composition, ultra detailed,
            professional graphic design, sharp focus, perfect lighting, no text
            """,
            
            "elegant": """
            elegant luxury event poster, gold foil accents, marble and crystal textures,
            sophisticated modern typography, minimalist luxury design with ample white space,
            black and gold color scheme, professional corporate design, high-end exclusive event,
            award-winning design, ultra detailed, clean composition, premium finish, no text
            """,
            
            "minimalistic": """
            minimalist professional poster masterpiece, Swiss International Style design,
            clean elegant typography, ample intelligent white space, geometric elements,
            modern sophisticated aesthetic, professional grid-based layout, refined color palette,
            ultra sharp, perfect balance, timeless design, no text
            """,
            
            "vibrant": """
            vibrant energetic event poster masterpiece, bold saturated colors,
            dynamic asymmetric composition, festival atmosphere with joyful celebration energy,
            mixed media collage with texture overlays, professional illustration style,
            eye-catching design with strong visual hierarchy, ultra detailed, perfect contrast, no text
            """,
            
            "professional": """
            professional corporate event poster excellence, business conference premium design,
            clean modern layout with perfect alignment, sophisticated typography,
            brand-aligned design system, executive luxury event, ultra detailed,
            perfect spacing, corporate elegance, no text
            """,
            
            "nature": """
            organic natural event poster masterpiece, eco-friendly sustainable design,
            detailed botanical illustrations with leaf patterns, earthy green color palette,
            sustainable design with natural textures, environmental conservation theme,
            professional organic layout, natural lighting, serene composition, no text
            """,
            
            "artistic": """
            artistic creative event poster excellence, painterly style with visible brush strokes,
            abstract geometric elements, mixed media collage with texture layers,
            textured background with subtle patterns, creative dynamic composition,
            professional art direction, artistic integrity, emotional impact, no text
            """,
            
            "tech": """
            modern tech event poster masterpiece, futuristic innovative design,
            digital circuit board patterns with glowing connections, glowing neon effects,
            innovative technology theme with data visualization elements,
            professional tech industry design, cybernetic aesthetic, forward-thinking, no text
            """
        }
        
        # Event type enhancements
        event_prompts = {
            "workshop": "educational workshop poster, creative collaborative learning environment",
            "conference": "professional conference poster, networking business event",
            "social": "social event poster, community gathering celebration",
            "sports": "sports event poster, athletic competition energy",
            "cultural": "cultural festival poster, traditional artistic elements",
            "tech": "technology conference poster, digital innovation summit",
            "seminar": "educational seminar poster, professional development focus",
            "competition": "competitive event poster, challenge and achievement celebration"
        }
        
        theme_desc = theme_prompts.get(data['theme'].lower(), theme_prompts["professional"])
        event_desc = event_prompts.get(data['event_type'].lower(), "professional premium event")
        
        # DALL-E 3 specific optimizations
        quality_enhancers = """
        masterpiece, best quality, 8k resolution, ultra detailed, professional photography,
        cinematic lighting, perfect proportions, award-winning design, trending on artstation
        """
        
        prompt = f"""
        Professional event poster design for {data['event_name']} {data['event_type']},
        {event_desc}, {theme_desc}, {quality_enhancers},
        perfect visual hierarchy and composition, attractive compelling imagery,
        professional graphic design excellence, no text or letters
        """
        
        return ' '.join(prompt.split())

    def _generate_with_sdxl_premium(self, request_data: dict) -> Image.Image:
        """Generate with Stable Diffusion XL as fallback"""
        try:
            prompt = self._build_premium_poster_prompt(request_data)
            
            API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            headers = {}
            
            if settings.HF_API_TOKEN:
                headers["Authorization"] = f"Bearer {settings.HF_API_TOKEN}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "num_inference_steps": 50,
                    "guidance_scale": 8.5,
                    "width": 1024,
                    "height": 1024,
                    "negative_prompt": self._build_premium_negative_prompt()
                },
                "options": {
                    "wait_for_model": True,
                    "use_cache": False
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
            
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                print("✅ Successfully generated premium poster with Stable Diffusion XL")
                return image
            else:
                print(f"SD-XL Premium API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"SD-XL Premium generation failed: {e}")
            return None

    def _build_premium_poster_prompt(self, data: dict) -> str:
        """Build premium-grade prompt for fallback SD-XL generation"""
        # ... (keep existing SD-XL prompt building logic)
        theme_prompts = {
            "cyberpunk": "cyberpunk event poster masterpiece, neon noir aesthetic, futuristic megacityscape",
            "elegant": "elegant luxury event poster, gold foil accents, marble and crystal textures",
            # ... other themes
        }
        
        theme_desc = theme_prompts.get(data['theme'].lower(), theme_prompts["professional"])
        prompt = f"professional event poster design for {data['event_name']}, {theme_desc}, ultra detailed, 8k resolution, no text"
        return prompt

    def _build_premium_negative_prompt(self) -> str:
        """Premium negative prompt for SD-XL"""
        return """
        blurry, low quality, worst quality, bad quality, lowres, text, words, letters, watermark, signature,
        username, artist name, error, cropped, jpeg artifacts, deformed, ugly, bad anatomy,
        poorly drawn, amateur, cartoon, oversaturated, compression artifacts
        """

    def _apply_premium_enhancements(self, image: Image.Image, crisp: bool = False) -> Image.Image:
        """Apply premium image enhancements"""
        try:
            # Ensure high resolution
            if image.size[0] < 1024:
                image = image.resize((1024, 1024), Image.Resampling.LANCZOS)
            
            # Advanced sharpening
            image = image.filter(ImageFilter.DETAIL)
            image = image.filter(ImageFilter.UnsharpMask(radius=1.2, percent=140, threshold=2))
            
            # Professional color correction
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.06 if crisp else 1.12)
            
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.03 if crisp else 1.08)
            
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.01 if crisp else 1.03)
            
            # Gentle clarity
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2 if crisp else 1.15)

            # Final sharpening pass
            image = image.filter(ImageFilter.UnsharpMask(radius=1.2 if crisp else 1.5, percent=170 if crisp else 160, threshold=2))
            
        except Exception as e:
            print(f"Premium image enhancement failed: {e}")
            
        return image

    def _load_premium_fonts(self, width: int) -> dict:
        """Load premium fonts for invitation design"""
        fonts = {}
        
        # Dynamic font sizes based on width
        base_size = width / 30
        
        font_sizes = {
            'title': int(base_size * 2.5),      # ~200px
            'subtitle': int(base_size * 1.2),   # ~100px
            'header': int(base_size * 0.9),     # ~75px
            'body': int(base_size * 0.7),       # ~60px
            'detail': int(base_size * 0.6),     # ~50px
            'footer': int(base_size * 0.5)      # ~40px
        }
        
        # Try to load premium fonts
        font_paths = [
            # Elegant serif fonts
            "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/times.ttf",
            "C:/Windows/Fonts/gara.ttf",
            # Linux alternatives
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            # macOS
            "/Library/Fonts/Times New Roman.ttf",
            "/Library/Fonts/Georgia.ttf",
            # Fallback
            "arial.ttf"
        ]
        
        for font_type, size in font_sizes.items():
            font_loaded = False
            for path in font_paths:
                try:
                    fonts[font_type] = ImageFont.truetype(path, size)
                    font_loaded = True
                    break
                except:
                    continue
            
            if not font_loaded:
                try:
                    fonts[font_type] = ImageFont.truetype("arial.ttf", size)
                except:
                    fonts[font_type] = ImageFont.load_default()
        
        return fonts

    def _get_premium_color_scheme(self, theme: str) -> dict:
        """Get premium color schemes for different themes"""
        schemes = {
            "elegant": {
                "primary": "#2C3E50",    # Dark blue
                "secondary": "#7F8C8D",  # Gray
                "accent": "#C19A6B",     # Gold
                "background": "#FFFFFF", # White
                "text": "#2C3E50"        # Dark blue
            },
            "royal": {
                "primary": "#2C3E50",
                "secondary": "#8B7355",
                "accent": "#D4AF37",
                "background": "#FEF9E7",
                "text": "#2C3E50"
            },
            "modern": {
                "primary": "#34495E",
                "secondary": "#95A5A6",
                "accent": "#E74C3C",
                "background": "#ECF0F1",
                "text": "#2C3E50"
            },
            "classic": {
                "primary": "#8B4513",
                "secondary": "#DEB887",
                "accent": "#8B7355",
                "background": "#FFF8DC",
                "text": "#8B4513"
            }
        }
        return schemes.get(theme.lower(), schemes["elegant"])

    def _draw_premium_background(self, draw, width, height, colors):
        """Draw premium background with subtle effects"""
        # Main background
        draw.rectangle([0, 0, width, height], fill=colors['background'])
        
        # Subtle gradient overlay
        for i in range(0, height, 2):
            alpha = int(10 * (i / height))
            color = self._hex_to_rgb(colors['primary'], alpha)
            draw.line([(0, i), (width, i)], fill=color, width=1)
        
        # Decorative border
        border_width = 20
        draw.rectangle([border_width, border_width, width-border_width, height-border_width], 
                      outline=colors['accent'], width=5)

    def _add_premium_decorations(self, draw, width, height, colors):
        """Add premium decorative elements"""
        # Corner decorations
        corner_size = 100
        line_width = 3
        
        # Top-left corner
        draw.line([(50, 50), (50, 50 + corner_size)], fill=colors['accent'], width=line_width)
        draw.line([(50, 50), (50 + corner_size, 50)], fill=colors['accent'], width=line_width)
        
        # Top-right corner
        draw.line([(width-50, 50), (width-50, 50 + corner_size)], fill=colors['accent'], width=line_width)
        draw.line([(width-50, 50), (width-50 - corner_size, 50)], fill=colors['accent'], width=line_width)
        
        # Bottom-left corner
        draw.line([(50, height-50), (50, height-50 - corner_size)], fill=colors['accent'], width=line_width)
        draw.line([(50, height-50), (50 + corner_size, height-50)], fill=colors['accent'], width=line_width)
        
        # Bottom-right corner
        draw.line([(width-50, height-50), (width-50, height-50 - corner_size)], fill=colors['accent'], width=line_width)
        draw.line([(width-50, height-50), (width-50 - corner_size, height-50)], fill=colors['accent'], width=line_width)

    def _render_premium_invitation_text(self, draw, width, height, data, invitation_text, fonts, colors):
        """Render invitation text with premium typography"""
        y_position = 300

        layout_variant = str(data.get('layout_variant', 'classic')).lower()  # classic | split | centered
        
        # Event Title
        title = data['event_name'].upper()
        title_bbox = draw.textbbox((0, 0), title, font=fonts['title'])
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        
        # Title with shadow effect
        shadow_offset = 5
        draw.text((title_x + shadow_offset, y_position + shadow_offset), title, 
                 fill=self._hex_to_rgb(colors['secondary'], 100), font=fonts['title'])
        draw.text((title_x, y_position), title, fill=colors['primary'], font=fonts['title'])
        
        y_position += title_bbox[3] - title_bbox[1] + 50
        
        # Event Type
        event_type = data['event_type'].replace('_', ' ').title()
        type_bbox = draw.textbbox((0, 0), event_type, font=fonts['subtitle'])
        type_width = type_bbox[2] - type_bbox[0]
        type_x = (width - type_width) // 2
        draw.text((type_x, y_position), event_type, fill=colors['accent'], font=fonts['subtitle'])
        
        y_position += type_bbox[3] - type_bbox[1] + 80
        
        # Details section
        details = [
            f"Date: {data['date']}",
            f"Time: {data['time']}",
            f"Venue: {data['venue']}",
            f"Dress Code: {data.get('dress_code', 'Elegant Attire')}"
        ]
        
        if layout_variant == 'split':
            # Left/right column split
            left_x = width // 6
            right_x = width - width // 6
            text_box_width = (right_x - left_x) // 2
            # Left: details
            for detail in details:
                detail_bbox = draw.textbbox((0, 0), detail, font=fonts['body'])
                draw.text((left_x, y_position), detail, fill=colors['text'], font=fonts['body'])
                y_position += detail_bbox[3] - detail_bbox[1] + 30
            # Reset for body text on right
            y_body = 300
            body_lines = invitation_text.split('\n')
            for line in body_lines:
                if not line.strip():
                    y_body += fonts['body'].size
                    continue
                draw.text((left_x + text_box_width + 40, y_body), line, fill=colors['text'], font=fonts['body'])
                y_body += fonts['body'].size + 12
        else:
            for detail in details:
                detail_bbox = draw.textbbox((0, 0), detail, font=fonts['body'])
                detail_width = detail_bbox[2] - detail_bbox[0]
                detail_x = (width - detail_width) // 2
                draw.text((detail_x, y_position), detail, fill=colors['text'], font=fonts['body'])
                y_position += detail_bbox[3] - detail_bbox[1] + 40

            # Body text centered block
            y_position += 40
            for line in [l for l in invitation_text.split('\n') if l.strip()]:
                line_bbox = draw.textbbox((0, 0), line, font=fonts['body'])
                line_width = line_bbox[2] - line_bbox[0]
                line_x = (width - line_width) // 2
                draw.text((line_x, y_position), line, fill=colors['text'], font=fonts['body'])
                y_position += line_bbox[3] - line_bbox[1] + 18

    def _hex_to_rgb(self, hex_color, alpha=255):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (alpha,)

    def _professional_fallback_invitation_generation(self, data: dict) -> dict:
        """Professional fallback invitation generation"""
        invitation_text = self._premium_invitation_template(data)
        return {
            "invitation_text": invitation_text,
            "formatted_invitation": invitation_text,
            "qr_code_url": self._generate_premium_qr_code(data) if data.get('rsvp_email') else None,
            "invitation_design": None,
            "status": "success",
            "model_used": "premium-fallback-template"
        }

    def generate_poster(self, request_data: dict) -> dict:
        """Generate professional event poster using advanced AI models"""
        try:
            print("🎨 Generating premium professional poster...")
            
            # Generate with the best available model
            image = None
            model_used = "ultimate-fallback"
            crisp_mode = bool(request_data.get('crisp_mode', False))
            
            # 1. Try Stable Diffusion XL (highest quality)
            image = self._generate_with_sdxl_premium(request_data)
            if image:
                model_used = "stable-diffusion-xl-premium"
            else:
                # 2. Try DALL-E style models
                image = self._generate_with_dalle_style(request_data)
                if image:
                    model_used = "dalle-style-premium"
                else:
                    # 3. Ultimate fallback: Premium template
                    image = self._generate_premium_template_poster(request_data)
                    model_used = "premium-template"
            
            # Apply premium enhancements
            image = self._apply_premium_enhancements(image, crisp=crisp_mode)
            
            # Add professional text overlay
            image = self._add_premium_text_overlay(image, request_data)
            
            # Final quality check and optimization
            image = self._finalize_premium_poster(image)
            
            # Convert to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG", quality=100, optimize=True)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            prompt_used = self._build_premium_poster_prompt(request_data)
            
            return {
                "image_url": f"data:image/png;base64,{img_str}",
                "prompt_used": prompt_used,
                "status": "success",
                "model_used": model_used,
                "dimensions": f"{image.width}x{image.height}",
                "file_size": f"{len(buffered.getvalue()) // 1024}KB"
            }
            
        except Exception as e:
            print(f"Premium poster generation error: {e}")
            # Ultimate professional fallback
            image = self._generate_premium_template_poster(request_data)
            buffered = BytesIO()
            image.save(buffered, format="PNG", quality=100)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "image_url": f"data:image/png;base64,{img_str}",
                "prompt_used": "premium-event-poster-design",
                "status": "success",
                "model_used": "ultimate-premium-fallback"
            }

    def _generate_with_sdxl_premium(self, request_data: dict) -> Image.Image:
        """Generate with Stable Diffusion XL for premium quality"""
        try:
            prompt = self._build_premium_poster_prompt(request_data)
            
            API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            headers = {}
            
            if settings.HF_API_TOKEN:
                headers["Authorization"] = f"Bearer {settings.HF_API_TOKEN}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "num_inference_steps": 50,
                    "guidance_scale": 8.5,
                    "width": 1024,
                    "height": 1024,
                    "negative_prompt": self._build_premium_negative_prompt()
                },
                "options": {
                    "wait_for_model": True,
                    "use_cache": False
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
            
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                print("✅ Successfully generated premium poster with Stable Diffusion XL")
                return image
            else:
                print(f"SD-XL Premium API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"SD-XL Premium generation failed: {e}")
            return None

    def _generate_with_dalle_style(self, request_data: dict) -> Image.Image:
        """Generate with DALL-E style models for high quality"""
        try:
            prompt = self._build_dalle_style_prompt(request_data)
            
            # Try different high-quality models
            models = [
                "black-forest-labs/FLUX.1-schnell",
                "stabilityai/stable-diffusion-xl-base-1.0",
                "runwayml/stable-diffusion-v1-5"
            ]
            
            for model in models:
                try:
                    API_URL = f"https://api-inference.huggingface.co/models/{model}"
                    headers = {}
                    
                    if settings.HF_API_TOKEN:
                        headers["Authorization"] = f"Bearer {settings.HF_API_TOKEN}"
                    
                    payload = {
                        "inputs": prompt,
                        "parameters": {
                            "num_inference_steps": 40,
                            "guidance_scale": 8.0,
                            "width": 1024,
                            "height": 1024,
                            "negative_prompt": self._build_premium_negative_prompt()
                        }
                    }
                    
                    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
                    
                    if response.status_code == 200:
                        image = Image.open(BytesIO(response.content))
                        print(f"✅ Successfully generated with {model}")
                        return image
                        
                except Exception as e:
                    print(f"Model {model} failed: {e}")
                    continue
                    
            return None
                
        except Exception as e:
            print(f"DALL-E style generation failed: {e}")
            return None

    def _build_premium_poster_prompt(self, data: dict) -> str:
        """Build premium-grade prompt for high-quality poster generation"""
        
        # Premium theme descriptions with enhanced details
        theme_prompts = {
            "cyberpunk": """
            cyberpunk event poster masterpiece, neon noir aesthetic, futuristic megacityscape with holographic advertisements,
            vibrant neon color palette (electric blue, hot pink, lime green, purple), detailed cyberpunk architecture with Japanese influences,
            atmospheric lighting with volumetric fog, cinematic composition, 8k resolution, ultra detailed, trending on artstation,
            professional graphic design, by Syd Mead and Josan Gonzalez, sharp focus, perfect lighting
            """,
            
            "elegant": """
            elegant luxury event poster, gold foil accents and embossing, marble and crystal textures with subtle reflections,
            sophisticated modern typography, minimalist luxury design with ample white space, black and gold color scheme with deep navy,
            professional corporate design, high-end exclusive event, award-winning design, ultra detailed, 8k resolution,
            by Paula Scher, clean composition, premium finish
            """,
            
            "minimalistic": """
            minimalist professional poster masterpiece, Swiss International Style design, clean elegant typography with perfect kerning,
            ample intelligent white space, geometric elements with golden ratio proportions, modern sophisticated aesthetic,
            professional grid-based layout, refined color palette with single accent color, 8k resolution, ultra sharp,
            by Massimo Vignelli, perfect balance, timeless design
            """,
            
            "vibrant": """
            vibrant energetic event poster masterpiece, bold saturated colors with complementary harmony, dynamic asymmetric composition,
            festival atmosphere with joyful celebration energy, mixed media collage with texture overlays, professional illustration style,
            eye-catching design with strong visual hierarchy, 8k resolution, ultra detailed, by Malika Favre, pop art influences,
            perfect contrast and balance
            """,
            
            "professional": """
            professional corporate event poster excellence, business conference premium design, clean modern layout with perfect alignment,
            professional stock photography with diverse business people, sophisticated typography with multiple weights,
            brand-aligned design system, executive luxury event, ultra detailed, 8k resolution, by Pentagram design studio,
            perfect spacing, corporate elegance
            """,
            
            "nature": """
            organic natural event poster masterpiece, eco-friendly sustainable design, detailed botanical illustrations with leaf patterns,
            earthy green color palette with natural tones, sustainable design with recycled paper texture, environmental conservation theme,
            professional organic layout, 8k resolution, by Brian Steely, natural lighting, serene composition
            """,
            
            "artistic": """
            artistic creative event poster excellence, painterly style with visible brush strokes, abstract geometric elements with meaning,
            mixed media collage with texture layers, textured background with subtle patterns, creative dynamic composition, gallery exhibition style,
            professional art direction, 8k resolution, by James Jean, artistic integrity, emotional impact
            """,
            
            "tech": """
            modern tech event poster masterpiece, futuristic innovative design, digital circuit board patterns with glowing connections,
            glowing neon effects with light trails, innovative technology theme with data visualization elements,
            professional tech industry design, 8k resolution, by Ash Thorp, cybernetic aesthetic, forward-thinking
            """
        }
        
        # Event type enhancements with specific details
        event_prompts = {
            "workshop": "educational workshop poster, creative collaborative learning environment, interactive hands-on session design, skill development focus",
            "conference": "professional conference poster premium, networking business event, multiple speaker sessions with diverse topics, industry gathering excellence",
            "social": "social event poster excellence, community gathering celebration, fun engaging atmosphere with connection focus, memorable experience design",
            "sports": "sports event poster dynamic, athletic competition energy, active lifestyle promotion, team spirit and sportsmanship celebration",
            "cultural": "cultural festival poster vibrant, traditional artistic elements with modern twist, diverse cultural celebration, heritage and innovation fusion",
            "tech": "technology conference poster innovative, digital transformation summit, cutting-edge innovation showcase, future trends exploration",
            "seminar": "educational seminar poster professional, academic knowledge sharing event, professional development focus, expert-led learning experience",
            "competition": "competitive event poster exciting, challenge and achievement celebration, skill demonstration platform, excellence recognition design"
        }
        
        theme_desc = theme_prompts.get(data['theme'].lower(), theme_prompts["professional"])
        event_desc = event_prompts.get(data['event_type'].lower(), "professional premium event")
        
        # Realism controls
        realism_strength = data.get('realism', 'high')  # high | medium | low
        realism_desc = {
            'high': "photorealistic, physically based rendering, natural materials, soft global illumination, realistic shadows, lens-based bokeh, depth of field, subtle film grain, calibrated white balance",
            'medium': "highly realistic, soft lighting, subtle reflections, balanced contrast, gentle depth of field",
            'low': "stylized realism, clean lighting, moderate texture detail"
        }.get(str(realism_strength).lower(), "photorealistic, physically based rendering, natural materials, soft global illumination, realistic shadows, lens-based bokeh, depth of field, subtle film grain, calibrated white balance")

        camera_style = data.get('camera_style', 'prime')  # prime | wide | telephoto
        camera_desc = {
            'prime': "shot on 50mm prime lens, f/2.8 aperture, cinematic color grading",
            'wide': "shot on 24mm wide-angle lens, dramatic perspective, f/4.0",
            'telephoto': "shot on 85mm lens, compressed perspective, creamy bokeh, f/2.0",
        }.get(str(camera_style).lower(), "shot on 50mm prime lens, f/2.8 aperture, cinematic color grading")

        material_accent = data.get('material_accent', 'none')
        material_desc = {
            'paper': "fine paper fibers micro-texture, matte finish",
            'metallic': "subtle metallic sheen, brushed metal micro-texture",
            'glass': "subsurface scattering in glass, faint reflections",
            'fabric': "woven fabric micro-texture, tactile surface",
            'none': ""
        }.get(str(material_accent).lower(), "")

        # Premium prompt engineering with enhanced details and realism
        prompt = f"""
        Professional event poster design for "{data['event_name']}",
        {event_desc}, {theme_desc}, {realism_desc}, {camera_desc}, {material_desc},
        award-winning design, ultra detailed, professional graphic design excellence,
        perfect visual hierarchy and composition, attractive compelling imagery, no text,
        trending on artstation and behance, 8k resolution, 4k quality, sharp focus,
        professional photography, cinematic lighting, perfect proportions
        """
        
        return ' '.join(prompt.split())

    def _build_dalle_style_prompt(self, data: dict) -> str:
        """Build prompt in DALL-E style for premium quality"""
        
        styles = {
            "cyberpunk": "cyberpunk aesthetic::3 neon lights::2 futuristic city::2 digital art::1.5 --style raw --quality 2",
            "elegant": "elegant luxury design::3 gold foil::2 minimalist sophistication::2 corporate::1.5 --style raw --quality 2",
            "professional": "professional corporate design::3 modern business::2 executive premium::2 clean::1.5 --style raw --quality 2"
        }
        
        style = styles.get(data['theme'].lower(), "professional corporate design::3 modern::2 --style raw --quality 2")
        
        realism_tag = {
            'high': 'photorealistic::2 physically based rendering::1.5 film grain::0.5',
            'medium': 'realistic lighting::1.2 soft shadows::1.1',
            'low': 'stylized realism::1'
        }.get(str(data.get('realism', 'high')).lower(), 'photorealistic::2 physically based rendering::1.5 film grain::0.5')

        prompt = f"""
        professional event poster design for {data['event_name']} {data['event_type']},
        {style} {realism_tag}, ultra detailed, 8k resolution, award-winning design, no text, masterpiece
        """
        
        return ' '.join(prompt.split())
    def _generate_with_dalle3_premium(self, request_data: dict) -> Image.Image:
        try:
                if not self.groq_client:
                    print("❌ Groq client not available for DALL-E 3")
                    return None
                    
                prompt = self._build_dalle3_poster_prompt(request_data)
                
                print(f"🚀 Generating DALL-E 3 poster with prompt: {prompt[:100]}...")
                
                try:
                    # Generate image using DALL-E 3 via Groq
                    response = self.groq_client.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        size="1024x1024",
                        quality="hd",  # Use HD for best quality
                        n=1,
                    )
                    
                    # Get the image URL from response
                    image_url = response.data[0].url
                    print(f"✅ DALL-E 3 image generated successfully: {image_url}")
                    
                    # Download the image
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        image = Image.open(BytesIO(image_response.content))
                        print("✅ Successfully downloaded and processed DALL-E 3 image")
                        return image
                    else:
                        print(f"❌ Failed to download image from DALL-E 3: {image_response.status_code}")
                        return None
                        
                except Exception as e:
                    print(f"❌ DALL-E 3 API call failed: {str(e)}")
                    return None
                    
        except Exception as e:
            print(f"❌ DALL-E 3 Premium generation failed: {e}")
            return None

    def _build_premium_negative_prompt(self) -> str:
        """Premium negative prompt to avoid all common issues"""
        return """
        blurry, low quality, worst quality, bad quality, lowres, text, words, letters, watermark, signature,
        username, artist name, error, cropped, jpeg artifacts, signature, watermark, username, artist name,
        deformed, ugly, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions,
        malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers,
        long neck, poorly drawn, poorly drawn hands, poorly drawn face, mutation, mutated, extra limb, ugly,
        disgusting, amputation, bad art, amateur, cartoon, anime, 3d, render, fake, plastic, doll, toy,
        oversaturated, oversmooth, jpeg, compression, artifacts, harsh vignette, excessive blur
        """

    def _apply_premium_enhancements(self, image: Image.Image, crisp: bool = False) -> Image.Image:
        """Apply premium image enhancements for professional quality.
        When crisp=True, skip any softening/texture and keep maximum clarity.
        """
        try:
            # Ensure high resolution
            if image.size[0] < 1024:
                image = image.resize((1024, 1024), Image.Resampling.LANCZOS)
            
            # Advanced sharpening (crisp but controlled)
            image = image.filter(ImageFilter.DETAIL)
            image = image.filter(ImageFilter.UnsharpMask(radius=1.2, percent=140, threshold=2))
            
            # Professional color correction
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.06 if crisp else 1.12)
            
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.03 if crisp else 1.08)
            
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.01 if crisp else 1.03)
            
            # Gentle clarity (avoid any blur or haze)
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2 if crisp else 1.15)

            # Skip vignette and grain when crisp; otherwise keep subtle tone mapping
            if not crisp:
                image = self._apply_tone_mapping(image)
            
            # Final sharpening pass
            image = image.filter(ImageFilter.UnsharpMask(radius=1.2 if crisp else 1.5, percent=170 if crisp else 160, threshold=2))
            
        except Exception as e:
            print(f"Premium image enhancement failed: {e}")
            
        return image

    def _add_premium_vignette(self, image: Image.Image, intensity: float = 0.4) -> Image.Image:
        """Add premium vignette effect for depth"""
        try:
            width, height = image.size
            mask = Image.new('L', (width, height), 0)
            draw = ImageDraw.Draw(mask)
            
            # Draw elliptical gradient
            ellipse_bbox = [width * -0.3, height * -0.3, width * 1.3, height * 1.3]
            draw.ellipse(ellipse_bbox, fill=255)
            
            # Apply sophisticated Gaussian blur
            mask = mask.filter(ImageFilter.GaussianBlur(width * 0.15))
            
            # Convert image to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create subtle dark overlay
            overlay = Image.new('RGB', (width, height), (10, 10, 20))
            
            # Professional blending
            result = Image.blend(image, overlay, intensity * 0.25)
            
            # Apply vignette with smooth transition
            result.putalpha(mask)
            image = image.convert('RGBA')
            image = Image.alpha_composite(image, result)
            
        except Exception as e:
            print(f"Premium vignette effect failed: {e}")
            
        return image

    def _apply_film_grain(self, image: Image.Image, strength: float = 0.06) -> Image.Image:
        """Apply subtle film grain for realism."""
        try:
            import numpy as np
            rng = np.random.default_rng()
            width, height = image.size
            # Create monochrome grain
            grain = (rng.normal(0.0, 255 * strength, (height, width)).clip(-255, 255)).astype('int16')
            base = image.convert('L')
            base_np = np.array(base, dtype='int16')
            noisy = (base_np + grain).clip(0, 255).astype('uint8')
            noisy_rgb = Image.merge('RGB', [Image.fromarray(noisy)] * 3)
            # Blend lightly
            image = Image.blend(image.convert('RGB'), noisy_rgb, alpha=0.15)
        except Exception as e:
            print(f"Film grain failed: {e}")
        return image

    def _apply_tone_mapping(self, image: Image.Image) -> Image.Image:
        """Apply gentle S-curve tone mapping for more photographic contrast."""
        try:
            # Build S-curve LUT
            def s_curve(x: int) -> int:
                t = x / 255.0
                # Smooth S-curve
                y = 1 / (1 + math.exp(-6 * (t - 0.5)))
                return int(max(0, min(255, round(y * 255))))
            lut = [s_curve(i) for i in range(256)]
            if image.mode != 'RGB':
                image = image.convert('RGB')
            r, g, b = image.split()
            r = r.point(lut)
            g = g.point(lut)
            b = b.point(lut)
            image = Image.merge('RGB', (r, g, b))
        except Exception as e:
            print(f"Tone mapping failed: {e}")
        return image

    def _add_premium_text_overlay(self, image: Image.Image, data: dict) -> Image.Image:
        """Add premium professional text overlay with perfect clarity"""
        try:
            # Create a copy to work on
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
                
            draw = ImageDraw.Draw(image)
            width, height = image.size
            
            # Create premium overlays with perfect contrast
            top_overlay = Image.new('RGBA', (width, 300), (0, 0, 0, 230))  # Darker for better readability
            bottom_overlay = Image.new('RGBA', (width, 400), (0, 0, 0, 230))
            
            image.paste(top_overlay, (0, 0), top_overlay)
            image.paste(bottom_overlay, (0, height-400), bottom_overlay)
            
            # Add smooth gradient transitions
            gradient_top = Image.new('RGBA', (width, 100), (0, 0, 0, 0))
            grad_draw_top = ImageDraw.Draw(gradient_top)
            for i in range(100):
                alpha = int(230 * (i / 100))
                grad_draw_top.line([(0, i), (width, i)], fill=(0, 0, 0, alpha))
            
            gradient_bottom = Image.new('RGBA', (width, 100), (0, 0, 0, 0))
            grad_draw_bottom = ImageDraw.Draw(gradient_bottom)
            for i in range(100):
                alpha = int(230 * ((100 - i) / 100))
                grad_draw_bottom.line([(0, i), (width, i)], fill=(0, 0, 0, alpha))
            
            image.paste(gradient_top, (0, 300), gradient_top)
            image.paste(gradient_bottom, (0, height-400), gradient_bottom)

            # Premium typography system
            fonts = self._load_premium_poster_fonts(width)

            # Event name with premium styling
            event_name = data['event_name'].upper()
            title_font = fonts['title_large']
            
            # Calculate perfect text positioning
            title_bbox = draw.textbbox((0, 0), event_name, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
            title_x = (width - title_width) // 2
            title_y = 120
            
            # Premium text background with border
            title_bg_padding = 25
            draw.rectangle([
                title_x - title_bg_padding, 
                title_y - title_bg_padding,
                title_x + title_width + title_bg_padding,
                title_y + title_height + title_bg_padding
            ], fill=(0, 0, 0, 180), outline=(255, 215, 0, 200), width=3)
            
            # Multiple shadow effects for depth
            shadow_offsets = [(4, 4), (-4, 4), (4, -4), (-4, -4), (0, 4), (4, 0)]
            for offset_x, offset_y in shadow_offsets:
                draw.text((title_x + offset_x, title_y + offset_y), event_name, 
                         fill=(0, 0, 0, 120), font=title_font)
            
            # Main text with stroke
            draw.text((title_x, title_y), event_name, fill="white", font=title_font, 
                     stroke_width=3, stroke_fill=(0, 0, 0, 150))

            # Event type with premium styling
            event_type = data['event_type'].replace('_', ' ').title()
            subtitle_font = fonts['subtitle']
            type_bbox = draw.textbbox((0, 0), event_type, font=subtitle_font)
            type_width = type_bbox[2] - type_bbox[0]
            type_height = type_bbox[3] - type_bbox[1]
            type_x = (width - type_width) // 2
            type_y = title_y + title_height + 40
            
            # Event type background
            type_bg_padding = 18
            draw.rectangle([
                type_x - type_bg_padding,
                type_y - type_bg_padding,
                type_x + type_width + type_bg_padding,
                type_y + type_height + type_bg_padding
            ], fill=(40, 40, 40, 200), outline=(255, 215, 0, 180), width=2)
            
            draw.text((type_x, type_y), event_type, fill="#FFD700", font=subtitle_font, 
                     stroke_width=2, stroke_fill=(0, 0, 0, 120))

            # Premium details section
            details_y = height - 350
            details = [
                f"📅 {data['date']}",
                f"⏰ {data['time']}", 
                f"📍 {data['venue']}"
            ]
            
            detail_font = fonts['detail']
            for i, detail in enumerate(details):
                detail_bbox = draw.textbbox((0, 0), detail, font=detail_font)
                detail_width = detail_bbox[2] - detail_bbox[0]
                detail_height = detail_bbox[3] - detail_bbox[1]
                detail_x = (width - detail_width) // 2
                detail_y_pos = details_y + i * 70
                
                # Premium detail background
                detail_bg_padding = 15
                draw.rectangle([
                    detail_x - detail_bg_padding,
                    detail_y_pos - detail_bg_padding,
                    detail_x + detail_width + detail_bg_padding,
                    detail_y_pos + detail_height + detail_bg_padding
                ], fill=(0, 0, 0, 170), outline=(255, 255, 255, 100), width=2)
                
                # Text with premium shadow
                draw.text((detail_x + 2, detail_y_pos + 2), detail, fill=(0, 0, 0, 150), font=detail_font)
                draw.text((detail_x, detail_y_pos), detail, fill="white", font=detail_font)

            # Premium Call to action
            cta_text = "🎯 REGISTER NOW • LIMITED SEATS AVAILABLE 🎯"
            cta_font = fonts['cta']
            cta_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
            cta_width = cta_bbox[2] - cta_bbox[0]
            cta_height = cta_bbox[3] - cta_bbox[1]
            cta_x = (width - cta_width) // 2
            cta_y = height - 120
            
            # Premium CTA background with gradient
            cta_bg_width = cta_width + 80
            cta_bg = Image.new('RGBA', (cta_bg_width, cta_height + 40), (220, 20, 60, 240))  # Crimson red
            cta_bg_x = cta_x - 40
            cta_bg_y = cta_y - 20
            
            # Add premium border to CTA
            border_size = 6
            draw.rectangle([
                cta_bg_x - border_size, cta_bg_y - border_size,
                cta_bg_x + cta_bg_width + border_size, 
                cta_bg_y + cta_height + 40 + border_size
            ], fill=(255, 255, 255, 200), outline=(255, 255, 255, 230), width=3)
            
            image.paste(cta_bg, (cta_bg_x, cta_bg_y), cta_bg)
            
            # Premium CTA text with multiple shadows
            shadow_offsets = [(2, 2), (-2, 2), (2, -2), (-2, -2)]
            for offset_x, offset_y in shadow_offsets:
                draw.text((cta_x + offset_x, cta_y + offset_y), cta_text, 
                         fill=(0, 0, 0, 100), font=cta_font)
            
            draw.text((cta_x, cta_y), cta_text, fill="white", font=cta_font, 
                     stroke_width=1, stroke_fill=(0, 0, 0, 100))

            # Add premium decorative elements
            self._add_premium_decorative_elements(draw, width, height)

            return image.convert('RGB')
            
        except Exception as e:
            print(f"Premium text overlay failed: {e}")
            return image

    def _load_premium_poster_fonts(self, image_width):
        """Load premium fonts for poster with perfect sizing"""
        fonts = {}
        
        # Dynamic font sizes based on image width
        base_size = image_width / 18  # More generous sizing
        
        font_sizes = {
            'title_large': int(base_size * 2.2),  # ~125px for 1024px width
            'subtitle': int(base_size * 1.3),     # ~74px for 1024px width
            'detail': int(base_size * 0.9),       # ~51px for 1024px width
            'cta': int(base_size * 0.7)           # ~40px for 1024px width
        }
        
        # Try to load premium fonts
        font_paths = [
            # Premium bold fonts
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
            "C:/Windows/Fonts/verdanab.ttf",
            "C:/Windows/Fonts/trebucbd.ttf",
            # Linux alternatives
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            # macOS
            "/Library/Fonts/Arial Bold.ttf",
            "/Library/Fonts/Verdana Bold.ttf",
            "/Library/Fonts/Helvetica Bold.ttf",
            # Fallback
            "arialbd.ttf",
            "arial.ttf"
        ]
        
        for font_type, size in font_sizes.items():
            font_loaded = False
            for path in font_paths:
                try:
                    fonts[font_type] = ImageFont.truetype(path, size)
                    font_loaded = True
                    break
                except Exception as e:
                    continue
            
            if not font_loaded:
                # Ultimate fallback
                try:
                    fonts[font_type] = ImageFont.truetype("arial.ttf", size)
                except:
                    fonts[font_type] = ImageFont.load_default()
        
        return fonts

    def _add_premium_decorative_elements(self, draw, width, height):
        """Add premium decorative elements for visual excellence"""
        try:
            # Premium corner accents (clean lines only; no dots, no grid)
            accent_color = (255, 215, 0, 200)
            line_width = 5
            corner_size = 120

            # Top-left corner
            draw.line([(40, 40), (corner_size, 40)], fill=accent_color, width=line_width)
            draw.line([(40, 40), (40, corner_size)], fill=accent_color, width=line_width)

            # Top-right corner
            draw.line([(width - corner_size, 40), (width - 40, 40)], fill=accent_color, width=line_width)
            draw.line([(width - 40, 40), (width - 40, corner_size)], fill=accent_color, width=line_width)

            # Bottom-left corner
            draw.line([(40, height - corner_size), (40, height - 40)], fill=accent_color, width=line_width)
            draw.line([(40, height - 40), (corner_size, height - 40)], fill=accent_color, width=line_width)

            # Bottom-right corner
            draw.line([(width - 40, height - corner_size), (width - 40, height - 40)], fill=accent_color, width=line_width)
            draw.line([(width - corner_size, height - 40), (width - 40, height - 40)], fill=accent_color, width=line_width)
            
        except Exception as e:
            print(f"Premium decorative elements failed: {e}")

    def _apply_paper_texture(self, image: Image.Image, kind: str) -> Image.Image:
        """Overlay subtle paper textures to improve realism."""
        try:
            kind = str(kind).lower()
            overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            width, height = image.size

            if kind == 'linen':
                # Crosshatch linen texture
                spacing = max(6, width // 300)
                color = (255, 255, 255, 20)
                for x in range(0, width, spacing):
                    draw.line([(x, 0), (x, height)], fill=color, width=1)
                for y in range(0, height, spacing):
                    draw.line([(0, y), (width, y)], fill=color, width=1)
            elif kind == 'grain':
                # Use film grain routine but lighter
                image = self._apply_film_grain(image, strength=0.03)
                return image
            elif kind == 'canvas':
                # Diagonal strokes
                color = (255, 255, 255, 18)
                step = max(12, width // 200)
                for i in range(-height, width, step):
                    draw.line([(i, 0), (i + height, height)], fill=color, width=1)

            # Blend texture
            base = image.convert('RGBA')
            base.alpha_composite(overlay)
            image = base.convert('RGB')
        except Exception as e:
            print(f"Paper texture failed: {e}")
        return image

    def _generate_premium_template_poster(self, data: dict) -> Image.Image:
        """Generate premium template-based poster as ultimate fallback"""
        width, height = 1200, 1600  # Better proportions for posters
        
        # Premium color schemes
        color_schemes = {
            "cyberpunk": {
                "bg": (15, 20, 40), "primary": (0, 240, 240), "secondary": (240, 0, 240), 
                "accent": (240, 240, 0), "text": (255, 255, 255), "gradient": (30, 30, 60)
            },
            "elegant": {
                "bg": (250, 250, 255), "primary": (180, 140, 80), "secondary": (120, 120, 120), 
                "accent": (200, 160, 100), "text": (40, 40, 40), "gradient": (220, 220, 230)
            },
            "professional": {
                "bg": (245, 248, 250), "primary": (0, 80, 160), "secondary": (80, 120, 160), 
                "accent": (160, 160, 160), "text": (30, 30, 30), "gradient": (230, 235, 240)
            }
        }
        
        scheme = color_schemes.get(data['theme'].lower(), color_schemes["professional"])
        
        # Create premium base image with advanced gradient
        image = Image.new('RGB', (width, height), color=scheme["bg"])
        draw = ImageDraw.Draw(image)
        
        # Draw sophisticated gradient background
        for i in range(height):
            ratio = i / height
            # Multi-color gradient with smooth transitions
            r = int(scheme["bg"][0] * (1 - ratio) + scheme["gradient"][0] * ratio)
            g = int(scheme["bg"][1] * (1 - ratio) + scheme["gradient"][1] * ratio)
            b = int(scheme["bg"][2] * (1 - ratio) + scheme["gradient"][2] * ratio)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        # Add premium design elements
        # Main header with gradient
        for i in range(200):
            ratio = i / 200
            r = int(scheme["primary"][0] * ratio + scheme["bg"][0] * (1 - ratio))
            g = int(scheme["primary"][1] * ratio + scheme["bg"][1] * (1 - ratio))
            b = int(scheme["primary"][2] * ratio + scheme["bg"][2] * (1 - ratio))
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        # Premium decorative elements
        element_count = 8
        for i in range(element_count):
            angle = (i / element_count) * 360
            radius = 400
            x = width//2 + int(radius * math.cos(math.radians(angle)))
            y = height//2 + int(radius * math.sin(math.radians(angle)))
            size = 30 + i % 4 * 15
            
            # Draw elegant shapes
            if i % 2 == 0:
                # Circles
                draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], 
                            outline=scheme["secondary"], width=3, fill=scheme["primary"])
            else:
                # Diamonds
                points = [
                    (x, y-size//2),
                    (x+size//2, y),
                    (x, y+size//2),
                    (x-size//2, y)
                ]
                draw.polygon(points, outline=scheme["secondary"], width=3, fill=scheme["accent"])
        
        # Add premium text
        fonts = self._load_premium_poster_fonts(width)
        
        # Event name with shadow
        event_name = data['event_name'].upper()
        title_bbox = draw.textbbox((0, 0), event_name, font=fonts['title_large'])
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        
        # Text shadow
        draw.text((title_x + 4, 104), event_name, fill=(0, 0, 0, 100), font=fonts['title_large'])
        draw.text((title_x, 100), event_name, fill=scheme["text"], font=fonts['title_large'])
        
        # Event details with premium styling
        details = [
            f"DATE: {data['date']}",
            f"TIME: {data['time']}",
            f"VENUE: {data['venue']}",
            f"EVENT TYPE: {data['event_type'].replace('_', ' ').title()}"
        ]
        
        for i, detail in enumerate(details):
            detail_bbox = draw.textbbox((0, 0), detail, font=fonts['detail'])
            detail_width = detail_bbox[2] - detail_bbox[0]
            detail_x = (width - detail_width) // 2
            
            # Detail background
            draw.rectangle([
                detail_x - 20, 400 + i * 80 - 10,
                detail_x + detail_width + 20, 400 + i * 80 + detail_bbox[3] - detail_bbox[1] + 10
            ], fill=(255, 255, 255, 180), outline=scheme["accent"], width=2)
            
            draw.text((detail_x, 400 + i * 80), detail, fill=scheme["text"], font=fonts['detail'])
        
        # Premium Call to action
        cta_text = "RESERVE YOUR SPOT • LIMITED AVAILABILITY"
        cta_bbox = draw.textbbox((0, 0), cta_text, font=fonts['cta'])
        cta_width = cta_bbox[2] - cta_bbox[0]
        cta_x = (width - cta_width) // 2
        
        # CTA background
        draw.rectangle([
            cta_x - 30, height - 150,
            cta_x + cta_width + 30, height - 90
        ], fill=scheme["primary"], outline=scheme["accent"], width=3)
        
        draw.text((cta_x, height - 140), cta_text, fill="white", font=fonts['cta'])
        
        return image

    def _finalize_premium_poster(self, image: Image.Image) -> Image.Image:
        """Apply final premium touches to the poster"""
        try:
            # Ensure optimal size
            if image.size != (1200, 1600):
                image = image.resize((1200, 1600), Image.Resampling.LANCZOS)
            
            # Final sharpening
            image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=3))
            
            # Final color adjustment
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.05)
            
            return image
            
        except Exception as e:
            print(f"Final premium touches failed: {e}")
            return image

# Global instance
ai_service = AIService()