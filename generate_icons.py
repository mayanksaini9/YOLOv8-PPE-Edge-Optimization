import os
from PIL import Image, ImageDraw, ImageFilter

def create_pulse_icon(size):
    # Create high-res canvas
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw rounded background
    radius = size // 5
    draw.rounded_rectangle(
        [0, 0, size, size], 
        radius=radius, 
        fill=(13, 14, 18, 255)
    )
    
    # Draw gradient glow
    glow_size = int(size * 0.75)
    glow_offset = (size - glow_size) // 2
    glow_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img)
    
    # Simple radial gradient draw for glow
    for r in range(glow_size, 0, -2):
        alpha = int((1.0 - (r / glow_size)) * 120)
        glow_draw.ellipse(
            [glow_offset + (glow_size - r)//2, glow_offset + (glow_size - r)//2, 
             glow_offset + (glow_size + r)//2, glow_offset + (glow_size + r)//2],
            fill=(99, 102, 241, alpha)
        )
    
    # Apply blur to glow
    glow_img = glow_img.filter(ImageFilter.GaussianBlur(size // 15))
    img = Image.alpha_composite(img, glow_img)
    
    # Draw the pulse line in the center
    # Pulse path nodes scaled to size
    cx = size // 2
    cy = size // 2
    w = size // 2
    h = size // 3
    
    points = [
        (cx - w//2, cy),
        (cx - w//4, cy),
        (cx - w//8, cy - h//2),
        (cx, cy + h//2),
        (cx + w//8, cy - h//3),
        (cx + w//4, cy),
        (cx + w//2, cy)
    ]
    
    # Draw glowing line under the main line
    draw_top = ImageDraw.Draw(img)
    line_glow_width = max(3, size // 30)
    line_width = max(2, size // 45)
    
    # Draw smooth lines
    for i in range(len(points) - 1):
        # Glow line
        draw_top.line([points[i], points[i+1]], fill=(236, 72, 153, 100), width=line_glow_width, joint="round")
        # Main line
        draw_top.line([points[i], points[i+1]], fill=(255, 255, 255, 255), width=line_width, joint="round")
        
    return img

# Save sizes
public_dir = r"E:\teams-clone\client\public"
os.makedirs(public_dir, exist_ok=True)

create_pulse_icon(192).save(os.path.join(public_dir, "icon-192.png"), "PNG")
create_pulse_icon(512).save(os.path.join(public_dir, "icon-512.png"), "PNG")
print("Successfully generated icon-192.png and icon-512.png")
