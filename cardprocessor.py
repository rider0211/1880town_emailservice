from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

def change_image_text(image_number, animalname, new_text, output_path):
    # Open an image file
    with Image.open(f"{image_number}.png") as img:
        # Ensure the image is in RGBA mode to handle transparency
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        draw = ImageDraw.Draw(img)
        
        # Define the font and size
        font = ImageFont.truetype("arial.ttf", 40)  # Adjust size as needed
        
        # Calculate text width and height to center it
        text_width = draw.textlength(new_text, font=font)
        text_height = 50
        text_position = ((img.width - text_width) / 2, 40)
        
        # Draw the new text centered
        draw.text(text_position, new_text, font=font, fill='black')
        footer = animalname + ' - ' + datetime.now().strftime("%B %d, %Y")
        animalfont = ImageFont.truetype("arial.ttf", 20)
        text_width = draw.textlength(footer, font=font)
        text_height = 20
        text_position = (10, img.height - 30)
        draw.text(text_position, footer, font=animalfont)
        # Save the modified image
        img.save(output_path, "PNG")

# Example usage
for i in range(1, 4):
    change_image_text(i, "otis", "Hi, Alice", f"{i}_out.png")
