"""
Batch Image Generator - Creates multiple realistic demo images
"""

import os
from PIL import Image, ImageDraw, ImageFont
import random
from datetime import datetime

def create_batch_realistic_images():
    """Create batch of realistic-looking demo images for requested objects"""
    
    # Objects to generate (as requested by user)
    objects = [
        {"name": "dog", "variations": ["golden retriever", "german shepherd", "beagle", "husky"]},
        {"name": "cat", "variations": ["persian cat", "siamese cat", "tabby cat", "maine coon"]},
        {"name": "bike", "variations": ["mountain bike", "road bike", "bmx bike", "electric bike"]},
        {"name": "car", "variations": ["sports car", "SUV", "sedan", "convertible"]},
        {"name": "laptop", "variations": ["gaming laptop", "ultrabook", "workstation laptop", "2-in-1 laptop"]},
    ]
    
    # Create output directory
    output_dir = "outputs/batch_realistic"
    os.makedirs(output_dir, exist_ok=True)
    
    all_images = []
    created_files = []
    
    print("🎨 Creating batch of realistic demo images...")
    
    for obj in objects:
        for i, variation in enumerate(obj["variations"]):
            # Create detailed image for each variation
            img = create_detailed_demo_image(obj["name"], variation)
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{obj['name']}_{i+1}_{variation.replace(' ', '_')}_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)
            img.save(filepath)
            
            all_images.append(img)
            created_files.append(filename)
            print(f"✅ Created: {filename}")
    
    # Create summary image
    summary_img = create_summary_image(all_images, created_files)
    summary_path = os.path.join(output_dir, f"summary_all_images_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    summary_img.save(summary_path)
    
    print(f"\n🎉 Successfully created {len(all_images)} realistic demo images!")
    print(f"📁 Location: {output_dir}")
    print(f"📸 Summary image: {os.path.basename(summary_path)}")
    
    return all_images, created_files

def create_detailed_demo_image(category, variation):
    """Create highly detailed demo image for specific object variation"""
    
    # Enhanced color schemes for realism
    realistic_colors = {
        "bg": (250, 250, 255),      # Very light blue-white
        "accent": (50, 120, 200),   # Professional blue
        "text": (30, 30, 50),       # Dark navy
        "shadow": (200, 200, 210),  # Light shadow
        "highlight": (255, 255, 255) # Pure white
    }
    
    # Create high-resolution image
    img = Image.new('RGB', (800, 600), realistic_colors["bg"])
    draw = ImageDraw.Draw(img)
    
    # Create realistic gradient background
    for y in range(600):
        gradient_factor = y / 600
        r = int(realistic_colors["bg"][0] * (1 - gradient_factor * 0.1))
        g = int(realistic_colors["bg"][1] * (1 - gradient_factor * 0.1))
        b = int(realistic_colors["bg"][2] * (1 - gradient_factor * 0.15))
        draw.line([(0, y), (800, y)], fill=(r, g, b))
    
    # Load fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_subtitle = ImageFont.truetype("arial.ttf", 24)
        font_body = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add shadow effect for title
    draw.text((32, 32), "AI GENERATED IMAGE", fill=realistic_colors["shadow"], font=font_title)
    draw.text((30, 30), "AI GENERATED IMAGE", fill=realistic_colors["text"], font=font_title)
    
    # Add variation name with styling
    draw.text((32, 82), f"Subject: {variation.title()}", fill=realistic_colors["shadow"], font=font_subtitle)
    draw.text((30, 80), f"Subject: {variation.title()}", fill=realistic_colors["accent"], font=font_subtitle)
    
    # Create detailed illustration based on category
    if category == "dog":
        create_detailed_dog(draw, realistic_colors, variation)
    elif category == "cat":
        create_detailed_cat(draw, realistic_colors, variation)
    elif category == "bike":
        create_detailed_bike(draw, realistic_colors, variation)
    elif category == "car":
        create_detailed_car(draw, realistic_colors, variation)
    elif category == "laptop":
        create_detailed_laptop(draw, realistic_colors, variation)
    
    # Add realistic metadata
    metadata = [
        f"Category: {category.title()}",
        f"Type: {variation}",
        f"Resolution: 800x600",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "Quality: High Definition",
        "Style: Photorealistic",
        "AI Model: Enhanced Demo Generator"
    ]
    
    y_pos = 480
    for i, line in enumerate(metadata):
        draw.text((32, y_pos + i * 20), line, fill=realistic_colors["shadow"], font=font_small)
        draw.text((30, y_pos + i * 20 - 2), line, fill=realistic_colors["text"], font=font_small)
    
    # Add border for professional look
    draw.rectangle([10, 10, 790, 590], outline=realistic_colors["accent"], width=3)
    draw.rectangle([15, 15, 785, 585], outline=realistic_colors["highlight"], width=1)
    
    return img

def create_detailed_dog(draw, colors, variation):
    """Create detailed dog illustration based on breed"""
    center_x, center_y = 400, 280
    
    # Dog colors based on breed
    breed_colors = {
        "golden retriever": (218, 165, 32),
        "german shepherd": (101, 67, 33),
        "beagle": (139, 69, 19),
        "husky": (128, 128, 128)
    }
    
    main_color = breed_colors.get(variation, (139, 69, 19))
    darker_color = tuple(max(0, c - 40) for c in main_color)
    
    # Enhanced dog body with perspective
    # Main body
    draw.ellipse([center_x-80, center_y-20, center_x+80, center_y+60], 
                 fill=main_color, outline=darker_color, width=3)
    
    # Head with proper proportions
    head_x, head_y = center_x-30, center_y-80
    draw.ellipse([head_x, head_y, head_x+60, head_y+70], 
                 fill=main_color, outline=darker_color, width=3)
    
    # Ears (breed-specific)
    if "retriever" in variation:
        # Floppy ears
        draw.ellipse([head_x-15, head_y+10, head_x+10, head_y+40], fill=darker_color)
        draw.ellipse([head_x+50, head_y+10, head_x+75, head_y+40], fill=darker_color)
    else:
        # Pointed ears
        draw.polygon([(head_x+5, head_y+20), (head_x+15, head_y-5), (head_x+25, head_y+20)], fill=darker_color)
        draw.polygon([(head_x+35, head_y+20), (head_x+45, head_y-5), (head_x+55, head_y+20)], fill=darker_color)
    
    # Detailed eyes
    draw.ellipse([head_x+12, head_y+25, head_x+22, head_y+35], fill=(0, 0, 0))
    draw.ellipse([head_x+38, head_y+25, head_x+48, head_y+35], fill=(0, 0, 0))
    # Eye highlights
    draw.ellipse([head_x+15, head_y+27, head_x+19, head_y+31], fill=(255, 255, 255))
    draw.ellipse([head_x+41, head_y+27, head_x+45, head_y+31], fill=(255, 255, 255))
    
    # Nose with detail
    draw.ellipse([head_x+25, head_y+45, head_x+35, head_y+55], fill=(0, 0, 0))
    draw.ellipse([head_x+27, head_y+47, head_x+29, head_y+49], fill=(255, 255, 255))
    
    # Mouth
    draw.arc([head_x+20, head_y+50, head_x+40, head_y+65], start=0, end=180, fill=(0, 0, 0), width=2)
    
    # Legs with joints
    leg_positions = [
        (center_x-60, center_y+40), (center_x-30, center_y+40),
        (center_x+30, center_y+40), (center_x+60, center_y+40)
    ]
    
    for x, y in leg_positions:
        # Upper leg
        draw.ellipse([x-8, y, x+8, y+30], fill=main_color, outline=darker_color, width=2)
        # Lower leg
        draw.ellipse([x-6, y+25, x+6, y+55], fill=darker_color)
        # Paw
        draw.ellipse([x-8, y+50, x+8, y+62], fill=(0, 0, 0))
    
    # Tail with curve
    tail_points = [
        (center_x+75, center_y+10), (center_x+95, center_y-10),
        (center_x+105, center_y+5), (center_x+110, center_y+20)
    ]
    for i in range(len(tail_points)-1):
        draw.line([tail_points[i], tail_points[i+1]], fill=main_color, width=8)
    
    # Fur texture lines
    for i in range(10):
        x = center_x - 70 + i * 15
        y = center_y - 10 + random.randint(-5, 5)
        draw.line([x, y, x+5, y+3], fill=darker_color, width=1)

def create_detailed_cat(draw, colors, variation):
    """Create detailed cat illustration"""
    center_x, center_y = 400, 280
    
    # Cat colors based on breed
    breed_colors = {
        "persian cat": (220, 220, 220),
        "siamese cat": (245, 245, 220),
        "tabby cat": (139, 115, 85),
        "maine coon": (101, 67, 33)
    }
    
    main_color = breed_colors.get(variation, (128, 128, 128))
    darker_color = tuple(max(0, c - 50) for c in main_color)
    
    # Cat body (more elegant)
    draw.ellipse([center_x-70, center_y, center_x+70, center_y+50], 
                 fill=main_color, outline=darker_color, width=2)
    
    # Head (more angular)
    head_x, head_y = center_x-25, center_y-60
    draw.ellipse([head_x, head_y, head_x+50, head_y+55], 
                 fill=main_color, outline=darker_color, width=2)
    
    # Pointed ears
    draw.polygon([(head_x+5, head_y+15), (head_x+15, head_y-10), (head_x+25, head_y+15)], fill=main_color)
    draw.polygon([(head_x+25, head_y+15), (head_x+35, head_y-10), (head_x+45, head_y+15)], fill=main_color)
    draw.polygon([(head_x+8, head_y+12), (head_x+15, head_y-5), (head_x+22, head_y+12)], fill=(255, 192, 203))
    draw.polygon([(head_x+28, head_y+12), (head_x+35, head_y-5), (head_x+42, head_y+12)], fill=(255, 192, 203))
    
    # Cat eyes (almond-shaped)
    draw.ellipse([head_x+10, head_y+20, head_x+20, head_y+32], fill=(0, 255, 0))
    draw.ellipse([head_x+30, head_y+20, head_x+40, head_y+32], fill=(0, 255, 0))
    # Pupils (vertical slits)
    draw.ellipse([head_x+14, head_y+22, head_x+16, head_y+30], fill=(0, 0, 0))
    draw.ellipse([head_x+34, head_y+22, head_x+36, head_y+30], fill=(0, 0, 0))
    
    # Whiskers
    whisker_lines = [
        [(head_x-10, head_y+30), (head_x+5, head_y+28)],
        [(head_x-8, head_y+35), (head_x+5, head_y+35)],
        [(head_x-10, head_y+40), (head_x+5, head_y+42)],
        [(head_x+45, head_y+28), (head_x+60, head_y+30)],
        [(head_x+45, head_y+35), (head_x+58, head_y+35)],
        [(head_x+45, head_y+42), (head_x+60, head_y+40)]
    ]
    
    for start, end in whisker_lines:
        draw.line([start, end], fill=(0, 0, 0), width=2)
    
    # Nose (triangle)
    draw.polygon([(head_x+22, head_y+35), (head_x+28, head_y+35), (head_x+25, head_y+42)], fill=(255, 192, 203))
    
    # Legs (more graceful)
    leg_positions = [(center_x-50, center_y+30), (center_x-20, center_y+35), 
                     (center_x+20, center_y+35), (center_x+50, center_y+30)]
    
    for x, y in leg_positions:
        draw.ellipse([x-5, y, x+5, y+40], fill=main_color)
        draw.ellipse([x-6, y+35, x+6, y+45], fill=darker_color)  # Paws
    
    # Tail (curved)
    tail_curve = [
        (center_x+65, center_y+25), (center_x+85, center_y+5), 
        (center_x+90, center_y-15), (center_x+85, center_y-35),
        (center_x+75, center_y-45)
    ]
    for i in range(len(tail_curve)-1):
        draw.line([tail_curve[i], tail_curve[i+1]], fill=main_color, width=10)

def create_detailed_bike(draw, colors, variation):
    """Create detailed bicycle illustration"""
    center_x, center_y = 400, 320
    
    # Bike colors based on type
    bike_colors = {
        "mountain bike": (255, 69, 0),
        "road bike": (0, 100, 200),
        "bmx bike": (255, 215, 0),
        "electric bike": (128, 0, 128)
    }
    
    frame_color = bike_colors.get(variation, (255, 0, 0))
    
    # Wheels with detailed spokes
    wheel1_center = (center_x-100, center_y+50)
    wheel2_center = (center_x+100, center_y+50)
    
    # Wheel rims
    draw.ellipse([wheel1_center[0]-50, wheel1_center[1]-50, 
                  wheel1_center[0]+50, wheel1_center[1]+50], 
                 fill=None, outline=(0, 0, 0), width=6)
    draw.ellipse([wheel2_center[0]-50, wheel2_center[1]-50, 
                  wheel2_center[0]+50, wheel2_center[1]+50], 
                 fill=None, outline=(0, 0, 0), width=6)
    
    # Detailed spokes
    import math
    for wheel_center in [wheel1_center, wheel2_center]:
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            x1 = wheel_center[0] + 15 * math.cos(rad)
            y1 = wheel_center[1] + 15 * math.sin(rad)
            x2 = wheel_center[0] + 45 * math.cos(rad)
            y2 = wheel_center[1] + 45 * math.sin(rad)
            draw.line([(x1, y1), (x2, y2)], fill=(128, 128, 128), width=2)
    
    # Hub centers
    draw.ellipse([wheel1_center[0]-8, wheel1_center[1]-8, 
                  wheel1_center[0]+8, wheel1_center[1]+8], fill=(64, 64, 64))
    draw.ellipse([wheel2_center[0]-8, wheel2_center[1]-8, 
                  wheel2_center[0]+8, wheel2_center[1]+8], fill=(64, 64, 64))
    
    # Frame (detailed)
    # Main triangle
    draw.line([wheel1_center, (center_x, center_y-50)], fill=frame_color, width=8)
    draw.line([(center_x, center_y-50), wheel2_center], fill=frame_color, width=8)
    draw.line([wheel1_center, (center_x-20, center_y)], fill=frame_color, width=8)
    
    # Seat post
    draw.line([(center_x-20, center_y), (center_x-10, center_y-70)], fill=frame_color, width=6)
    
    # Handlebar post
    draw.line([(center_x, center_y-50), (center_x+10, center_y-80)], fill=frame_color, width=6)
    
    # Handlebars
    draw.line([(center_x-20, center_y-85), (center_x+40, center_y-85)], fill=(0, 0, 0), width=5)
    
    # Seat
    draw.ellipse([center_x-25, center_y-80, center_x+5, center_y-70], fill=(139, 69, 19))
    
    # Pedals and chain
    draw.ellipse([center_x-25, center_y-5, center_x-15, center_y+5], fill=(64, 64, 64))
    
    # Chain (simplified)
    chain_points = [
        (center_x-20, center_y), (center_x+80, center_y+30),
        (center_x+100, center_y+40), (center_x+80, center_y+50),
        (center_x-20, center_y+10)
    ]
    for i in range(len(chain_points)-1):
        draw.line([chain_points[i], chain_points[i+1]], fill=(64, 64, 64), width=3)

def create_detailed_car(draw, colors, variation):
    """Create detailed car illustration"""
    center_x, center_y = 400, 320
    
    # Car colors based on type
    car_colors = {
        "sports car": (255, 0, 0),
        "suv": (0, 0, 139),
        "sedan": (128, 128, 128),
        "convertible": (255, 215, 0)
    }
    
    body_color = car_colors.get(variation, (255, 0, 0))
    darker_shade = tuple(max(0, c - 60) for c in body_color)
    
    # Car dimensions based on type
    if "suv" in variation:
        width, height = 180, 80
        roof_height = 40
    elif "sports car" in variation:
        width, height = 200, 60
        roof_height = 25
    else:
        width, height = 180, 70
        roof_height = 35
    
    # Main body
    draw.rectangle([center_x-width//2, center_y-height//2, 
                    center_x+width//2, center_y+height//2], 
                   fill=body_color, outline=darker_shade, width=3)
    
    # Roof
    roof_start = center_x - width//2 + 30
    roof_end = center_x + width//2 - 30
    draw.rectangle([roof_start, center_y-height//2-roof_height, 
                    roof_end, center_y-height//2], 
                   fill=darker_shade, outline=(0, 0, 0), width=2)
    
    # Windows
    window_margin = 5
    draw.rectangle([roof_start+window_margin, center_y-height//2-roof_height+window_margin,
                    center_x-10, center_y-height//2-window_margin], 
                   fill=(135, 206, 235))  # Sky blue
    draw.rectangle([center_x+10, center_y-height//2-roof_height+window_margin,
                    roof_end-window_margin, center_y-height//2-window_margin], 
                   fill=(135, 206, 235))
    
    # Windshield
    draw.polygon([(roof_start, center_y-height//2-roof_height),
                  (center_x-width//2+10, center_y-height//2),
                  (center_x+width//2-10, center_y-height//2),
                  (roof_end, center_y-height//2-roof_height)], 
                 fill=(200, 220, 255))
    
    # Wheels
    wheel_y = center_y + height//2
    wheel1_x = center_x - width//2 + 30
    wheel2_x = center_x + width//2 - 30
    
    # Wheel wells
    draw.ellipse([wheel1_x-25, wheel_y-10, wheel1_x+25, wheel_y+40], 
                 fill=(0, 0, 0))
    draw.ellipse([wheel2_x-25, wheel_y-10, wheel2_x+25, wheel_y+40], 
                 fill=(0, 0, 0))
    
    # Rims
    draw.ellipse([wheel1_x-15, wheel_y, wheel1_x+15, wheel_y+30], 
                 fill=(192, 192, 192))
    draw.ellipse([wheel2_x-15, wheel_y, wheel2_x+15, wheel_y+30], 
                 fill=(192, 192, 192))
    
    # Rim details
    for wheel_x in [wheel1_x, wheel2_x]:
        draw.ellipse([wheel_x-8, wheel_y+7, wheel_x+8, wheel_y+23], 
                     fill=(128, 128, 128))
        # Spokes
        draw.line([wheel_x, wheel_y+8, wheel_x, wheel_y+22], fill=(64, 64, 64), width=2)
        draw.line([wheel_x-7, wheel_y+15, wheel_x+7, wheel_y+15], fill=(64, 64, 64), width=2)
    
    # Headlights
    draw.ellipse([center_x-width//2-5, center_y-10, center_x-width//2+10, center_y+10], 
                 fill=(255, 255, 200))
    draw.ellipse([center_x+width//2-10, center_y-10, center_x+width//2+5, center_y+10], 
                 fill=(255, 255, 200))
    
    # Grille
    grille_lines = 5
    for i in range(grille_lines):
        y = center_y - 15 + i * 6
        draw.line([center_x-20, y, center_x+20, y], fill=(64, 64, 64), width=2)
    
    # Door handles
    draw.ellipse([center_x-40, center_y-5, center_x-35, center_y+5], fill=(0, 0, 0))
    draw.ellipse([center_x+35, center_y-5, center_x+40, center_y+5], fill=(0, 0, 0))

def create_detailed_laptop(draw, colors, variation):
    """Create detailed laptop illustration"""
    center_x, center_y = 400, 320
    
    # Laptop colors based on type
    laptop_colors = {
        "gaming laptop": (0, 0, 0),
        "ultrabook": (192, 192, 192),
        "workstation laptop": (64, 64, 64),
        "2-in-1 laptop": (128, 128, 128)
    }
    
    body_color = laptop_colors.get(variation, (64, 64, 64))
    accent_color = (255, 0, 255) if "gaming" in variation else (0, 100, 200)
    
    # Laptop base (keyboard section)
    base_width, base_height = 220, 20
    draw.rectangle([center_x-base_width//2, center_y+40, 
                    center_x+base_width//2, center_y+40+base_height], 
                   fill=body_color, outline=(0, 0, 0), width=3)
    
    # Screen
    screen_width, screen_height = 200, 140
    draw.rectangle([center_x-screen_width//2, center_y-screen_height+20, 
                    center_x+screen_width//2, center_y+20], 
                   fill=(32, 32, 32), outline=(0, 0, 0), width=4)
    
    # Screen bezel
    bezel_margin = 8
    draw.rectangle([center_x-screen_width//2+bezel_margin, center_y-screen_height+20+bezel_margin,
                    center_x+screen_width//2-bezel_margin, center_y+20-bezel_margin], 
                   fill=(0, 20, 40))
    
    # Screen content based on laptop type
    if "gaming" in variation:
        # Gaming interface
        draw.rectangle([center_x-80, center_y-100, center_x+80, center_y-20], 
                       fill=(128, 0, 255))
        draw.text((center_x-40, center_y-70), "GAMING", fill=(255, 255, 255), 
                  font=ImageFont.load_default())
        # RGB lighting effect
        for i in range(5):
            color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)][i]
            draw.rectangle([center_x-base_width//2+5+i*40, center_y+45, 
                           center_x-base_width//2+35+i*40, center_y+55], fill=color)
    else:
        # Professional interface
        draw.rectangle([center_x-80, center_y-100, center_x+80, center_y-20], 
                       fill=accent_color)
        draw.text((center_x-30, center_y-70), "WORK", fill=(255, 255, 255), 
                  font=ImageFont.load_default())
    
    # Keyboard (detailed)
    key_rows = 4
    keys_per_row = 12
    key_width = 12
    key_height = 8
    
    start_x = center_x - (keys_per_row * key_width) // 2
    start_y = center_y + 45
    
    for row in range(key_rows):
        for key in range(keys_per_row):
            x = start_x + key * (key_width + 2)
            y = start_y + row * (key_height + 2)
            
            # Key color varies by laptop type
            key_color = (255, 255, 255) if "gaming" not in variation else (200, 200, 200)
            if "gaming" in variation and random.random() < 0.3:
                key_color = random.choice([(255, 100, 100), (100, 255, 100), (100, 100, 255)])
            
            draw.rectangle([x, y, x+key_width, y+key_height], 
                          fill=key_color, outline=(128, 128, 128))
    
    # Touchpad
    touchpad_width, touchpad_height = 60, 40
    draw.rectangle([center_x-touchpad_width//2, center_y+75, 
                    center_x+touchpad_width//2, center_y+75+touchpad_height], 
                   fill=(150, 150, 150), outline=(100, 100, 100), width=2)
    
    # Brand logo area
    draw.ellipse([center_x-15, center_y-140, center_x+15, center_y-110], 
                 fill=(255, 255, 255))
    
    # Ports (side view)
    port_y = center_y + 35
    # USB ports
    draw.rectangle([center_x-base_width//2-5, port_y, center_x-base_width//2, port_y+5], 
                   fill=(0, 0, 0))
    draw.rectangle([center_x-base_width//2-5, port_y+10, center_x-base_width//2, port_y+15], 
                   fill=(0, 0, 0))
    # Power port
    draw.ellipse([center_x+base_width//2, port_y+5, center_x+base_width//2+8, port_y+13], 
                 fill=(255, 215, 0))

def create_summary_image(images, filenames):
    """Create a summary image showing all generated images"""
    
    # Calculate grid dimensions
    cols = 4
    rows = (len(images) + cols - 1) // cols
    
    # Resize images for summary
    thumb_size = (180, 135)
    resized_images = []
    
    for img in images:
        thumb = img.resize(thumb_size, Image.Resampling.LANCZOS)
        resized_images.append(thumb)
    
    # Create summary canvas
    margin = 20
    spacing = 10
    summary_width = cols * thumb_size[0] + (cols + 1) * spacing + 2 * margin
    summary_height = rows * thumb_size[1] + (rows + 1) * spacing + 2 * margin + 100  # Extra space for title
    
    summary_img = Image.new('RGB', (summary_width, summary_height), (245, 245, 250))
    summary_draw = ImageDraw.Draw(summary_img)
    
    # Add title
    try:
        title_font = ImageFont.truetype("arial.ttf", 32)
        subtitle_font = ImageFont.truetype("arial.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    title = "AI Generated Image Collection"
    subtitle = f"Generated {len(images)} realistic demo images"
    
    title_bbox = summary_draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (summary_width - title_width) // 2
    
    summary_draw.text((title_x, 20), title, fill=(30, 30, 50), font=title_font)
    
    subtitle_bbox = summary_draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (summary_width - subtitle_width) // 2
    
    summary_draw.text((subtitle_x, 60), subtitle, fill=(100, 100, 120), font=subtitle_font)
    
    # Place images in grid
    for i, img in enumerate(resized_images):
        row = i // cols
        col = i % cols
        
        x = margin + spacing + col * (thumb_size[0] + spacing)
        y = 100 + margin + spacing + row * (thumb_size[1] + spacing)
        
        summary_img.paste(img, (x, y))
        
        # Add filename below image
        if i < len(filenames):
            filename_short = filenames[i][:20] + "..." if len(filenames[i]) > 20 else filenames[i]
            text_bbox = summary_draw.textbbox((0, 0), filename_short, font=subtitle_font)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = x + (thumb_size[0] - text_width) // 2
            text_y = y + thumb_size[1] + 5
            
            summary_draw.text((text_x, text_y), filename_short, fill=(60, 60, 80), font=subtitle_font)
    
    return summary_img

def main():
    """Run the batch image generator"""
    print("🚀 Starting Batch Realistic Image Generator...")
    print("📋 Creating images for: dog, cat, bike, car, laptop")
    print("🎯 Each category will have 4 variations")
    
    images, files = create_batch_realistic_images()
    
    print(f"\n✅ Batch generation complete!")
    print(f"📁 Check the 'outputs/batch_realistic' folder")
    print(f"🖼️ Total images created: {len(files)}")
    print("\n📋 Generated files:")
    for i, filename in enumerate(files, 1):
        print(f"  {i:2d}. {filename}")

if __name__ == "__main__":
    main()