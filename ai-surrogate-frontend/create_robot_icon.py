"""
Create a custom robot icon for the AI Surrogate app
Run this script to generate icon.png, adaptive-icon.png, and favicon.png
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    def create_robot_icon(size=1024):
        # Create a new image with a dark background
        img = Image.new('RGBA', (size, size), (10, 10, 10, 255))
        draw = ImageDraw.Draw(img)
        
        # Colors
        cyan = (0, 255, 255, 255)
        blue = (0, 123, 255, 255)
        white = (255, 255, 255, 255)
        dark = (10, 10, 10, 255)
        
        # Robot head (rounded rectangle)
        head_margin = size // 8
        head_size = size - 2 * head_margin
        head_radius = size // 16
        
        # Draw robot head background
        draw.rounded_rectangle(
            [head_margin, head_margin + size//16, head_margin + head_size, head_margin + head_size - size//16],
            radius=head_radius,
            fill=cyan,
            outline=white,
            width=size//128
        )
        
        # Eyes
        eye_size = size // 12
        eye_y = head_margin + size // 4
        left_eye_x = head_margin + size // 4
        right_eye_x = head_margin + 3 * size // 4
        
        # Draw eye sockets
        draw.ellipse([left_eye_x - eye_size, eye_y - eye_size, left_eye_x + eye_size, eye_y + eye_size], fill=dark)
        draw.ellipse([right_eye_x - eye_size, eye_y - eye_size, right_eye_x + eye_size, eye_y + eye_size], fill=dark)
        
        # Draw glowing eyes
        glow_size = eye_size // 2
        draw.ellipse([left_eye_x - glow_size, eye_y - glow_size, left_eye_x + glow_size, eye_y + glow_size], fill=cyan)
        draw.ellipse([right_eye_x - glow_size, eye_y - glow_size, right_eye_x + glow_size, eye_y + glow_size], fill=cyan)
        
        # Mouth
        mouth_y = head_margin + 2 * size // 3
        mouth_width = size // 6
        mouth_height = size // 32
        mouth_x = size // 2 - mouth_width // 2
        
        draw.rounded_rectangle(
            [mouth_x, mouth_y, mouth_x + mouth_width, mouth_y + mouth_height],
            radius=mouth_height//2,
            fill=dark
        )
        
        # Antenna
        antenna_x = size // 2
        antenna_top = head_margin - size // 16
        antenna_height = size // 16
        antenna_width = size // 128
        
        draw.rectangle([antenna_x - antenna_width, antenna_top, antenna_x + antenna_width, head_margin], fill=white)
        draw.ellipse([antenna_x - size//32, antenna_top - size//32, antenna_x + size//32, antenna_top + size//32], fill=cyan)
        
        # Circuit patterns
        circuit_y1 = head_margin + size // 2
        circuit_y2 = circuit_y1 + size // 32
        circuit_width = size // 8
        circuit_height = size // 256
        
        # Left circuits
        draw.rectangle([head_margin + size//8, circuit_y1, head_margin + size//8 + circuit_width, circuit_y1 + circuit_height], fill=blue)
        draw.rectangle([head_margin + size//8, circuit_y2, head_margin + size//8 + circuit_width//2, circuit_y2 + circuit_height], fill=blue)
        
        # Right circuits  
        draw.rectangle([head_margin + 5*size//8, circuit_y1, head_margin + 5*size//8 + circuit_width, circuit_y1 + circuit_height], fill=blue)
        draw.rectangle([head_margin + 5*size//8, circuit_y2, head_margin + 5*size//8 + circuit_width//2, circuit_y2 + circuit_height], fill=blue)
        
        # AI text
        try:
            font_size = size // 12
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        text = "AI"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = size // 2 - text_width // 2
        text_y = head_margin + 3 * size // 4 - text_height // 2
        
        draw.text((text_x, text_y), text, font=font, fill=white)
        
        return img
    
    def main():
        assets_dir = "assets"
        
        print("Creating robot icon...")
        
        # Create main icon (1024x1024)
        icon = create_robot_icon(1024)
        icon.save(os.path.join(assets_dir, "icon.png"))
        print("✓ Created icon.png (1024x1024)")
        
        # Create adaptive icon (1024x1024)
        adaptive_icon = create_robot_icon(1024)
        adaptive_icon.save(os.path.join(assets_dir, "adaptive-icon.png"))
        print("✓ Created adaptive-icon.png (1024x1024)")
        
        # Create splash icon (1024x1024)
        splash_icon = create_robot_icon(1024)
        splash_icon.save(os.path.join(assets_dir, "splash-icon.png"))
        print("✓ Created splash-icon.png (1024x1024)")
        
        # Create favicon (48x48)
        favicon = create_robot_icon(1024)
        favicon = favicon.resize((48, 48), Image.Resampling.LANCZOS)
        favicon.save(os.path.join(assets_dir, "favicon.png"))
        print("✓ Created favicon.png (48x48)")
        
        print("\n🤖 Robot icons created successfully!")
        print("Your AI Surrogate app now has a custom robot icon!")
        
    if __name__ == "__main__":
        main()
        
except ImportError:
    print("PIL (Pillow) not found. Installing...")
    import subprocess
    import sys
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        print("Pillow installed! Please run the script again.")
    except:
        print("Could not install Pillow automatically.")
        print("Please install it manually: pip install Pillow")
        print("Then run this script again.")