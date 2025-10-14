"""
Create a custom robot icon for the AI Surrogate app
Run this script to generate icon.png, adaptive-icon.png, and favicon.png
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    def create_robot_icon(size=1024):
        # Create a new image with gradient-like dark background
        img = Image.new('RGBA', (size, size), (15, 20, 30, 255))
        draw = ImageDraw.Draw(img)
        
        # Enhanced color palette
        cyan_bright = (0, 255, 255, 255)
        cyan_glow = (100, 255, 255, 255)
        blue_accent = (0, 150, 255, 255)
        white = (255, 255, 255, 255)
        dark_gray = (30, 35, 45, 255)
        darker = (10, 15, 20, 255)
        light_gray = (200, 210, 220, 255)
        
        # Robot head with metallic look
        head_margin = size // 7
        head_width = size - 2 * head_margin
        head_height = int(head_width * 1.1)
        head_radius = size // 12
        
        # Main head body with shadow effect
        shadow_offset = size // 64
        draw.rounded_rectangle(
            [head_margin + shadow_offset, head_margin + shadow_offset, 
             head_margin + head_width + shadow_offset, head_margin + head_height + shadow_offset],
            radius=head_radius,
            fill=darker
        )
        
        # Main head with gradient effect (simulate with multiple rectangles)
        draw.rounded_rectangle(
            [head_margin, head_margin, head_margin + head_width, head_margin + head_height],
            radius=head_radius,
            fill=dark_gray,
            outline=cyan_bright,
            width=size//100
        )
        
        # Top panel accent
        panel_height = size // 20
        draw.rounded_rectangle(
            [head_margin + size//32, head_margin + size//32, 
             head_margin + head_width - size//32, head_margin + panel_height],
            radius=size//64,
            fill=cyan_bright
        )
        
        # Eyes - more sophisticated design
        eye_width = size // 8
        eye_height = size // 10
        eye_y = head_margin + size // 4
        left_eye_x = head_margin + size // 4
        right_eye_x = head_margin + 3 * size // 4
        
        # Eye backgrounds (sockets)
        for eye_x in [left_eye_x, right_eye_x]:
            draw.rounded_rectangle(
                [eye_x - eye_width, eye_y - eye_height, 
                 eye_x + eye_width, eye_y + eye_height],
                radius=size//64,
                fill=darker,
                outline=blue_accent,
                width=size//256
            )
        
        # Glowing eye cores
        glow_size = eye_width // 2
        for eye_x in [left_eye_x, right_eye_x]:
            # Outer glow
            draw.ellipse(
                [eye_x - glow_size*1.5, eye_y - glow_size*1.2, 
                 eye_x + glow_size*1.5, eye_y + glow_size*1.2],
                fill=cyan_glow
            )
            # Inner bright core
            draw.ellipse(
                [eye_x - glow_size*0.8, eye_y - glow_size*0.6, 
                 eye_x + glow_size*0.8, eye_y + glow_size*0.6],
                fill=cyan_bright
            )
            # Highlight
            highlight_size = glow_size // 3
            draw.ellipse(
                [eye_x - glow_size*0.3, eye_y - glow_size*0.4, 
                 eye_x + highlight_size, eye_y],
                fill=white
            )
        
        # Face plate details
        mouth_y = head_margin + 2 * size // 3
        mouth_width = size // 5
        mouth_height = size // 48
        mouth_x = size // 2 - mouth_width // 2
        
        # Mouth with segments
        segment_count = 5
        segment_width = mouth_width // segment_count
        for i in range(segment_count):
            if i % 2 == 0:
                draw.rectangle(
                    [mouth_x + i * segment_width, mouth_y, 
                     mouth_x + (i + 1) * segment_width - size//256, mouth_y + mouth_height],
                    fill=cyan_bright
                )
        
        # Antenna with detail
        antenna_x = size // 2
        antenna_base_y = head_margin
        antenna_top_y = head_margin - size // 12
        antenna_width = size // 96
        
        # Antenna body
        draw.rectangle(
            [antenna_x - antenna_width*2, antenna_top_y + size//64, 
             antenna_x + antenna_width*2, antenna_base_y],
            fill=light_gray
        )
        
        # Antenna tip with glow
        tip_size = size // 24
        draw.ellipse(
            [antenna_x - tip_size, antenna_top_y - tip_size, 
             antenna_x + tip_size, antenna_top_y + tip_size],
            fill=cyan_glow,
            outline=cyan_bright,
            width=size//256
        )
        draw.ellipse(
            [antenna_x - tip_size//2, antenna_top_y - tip_size//2, 
             antenna_x + tip_size//2, antenna_top_y + tip_size//2],
            fill=white
        )
        
        # Circuit patterns - more intricate
        circuit_y_base = head_margin + size // 2
        
        # Left side circuits
        for i, offset in enumerate([0, size//32, size//16]):
            circuit_length = size // 8 - i * size // 32
            draw.rectangle(
                [head_margin + size//16, circuit_y_base + offset, 
                 head_margin + size//16 + circuit_length, circuit_y_base + offset + size//256],
                fill=blue_accent if i % 2 == 0 else cyan_bright
            )
            # Circuit nodes
            for j in range(3):
                node_x = head_margin + size//16 + j * circuit_length // 2
                node_size = size // 128
                draw.ellipse(
                    [node_x - node_size, circuit_y_base + offset - node_size,
                     node_x + node_size, circuit_y_base + offset + node_size],
                    fill=cyan_bright
                )
        
        # Right side circuits (mirror)
        for i, offset in enumerate([0, size//32, size//16]):
            circuit_length = size // 8 - i * size // 32
            circuit_x = head_margin + head_width - size//16 - circuit_length
            draw.rectangle(
                [circuit_x, circuit_y_base + offset,
                 circuit_x + circuit_length, circuit_y_base + offset + size//256],
                fill=blue_accent if i % 2 == 0 else cyan_bright
            )
            # Circuit nodes
            for j in range(3):
                node_x = circuit_x + j * circuit_length // 2
                node_size = size // 128
                draw.ellipse(
                    [node_x - node_size, circuit_y_base + offset - node_size,
                     node_x + node_size, circuit_y_base + offset + node_size],
                    fill=cyan_bright
                )
        
        # Chin/bottom detail
        chin_y = head_margin + head_height - size // 16
        chin_width = size // 3
        chin_height = size // 32
        draw.rounded_rectangle(
            [size//2 - chin_width//2, chin_y, size//2 + chin_width//2, chin_y + chin_height],
            radius=size//64,
            fill=darker,
            outline=blue_accent,
            width=size//256
        )
        
        # AI text with better styling
        try:
            font_size = size // 10
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        text = "AI"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = size // 2 - text_width // 2
        text_y = head_margin + 4 * size // 5 - text_height // 2
        
        # Text shadow
        shadow_offset = size // 128
        draw.text((text_x + shadow_offset, text_y + shadow_offset), text, font=font, fill=darker)
        # Main text with gradient effect
        draw.text((text_x, text_y), text, font=font, fill=cyan_bright)
        
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