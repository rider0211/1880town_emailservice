from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

def change_image_text(image_number, animalname, new_text, output_path):
    # Open an image file
    if image_number <= 10:
        imagename = "Jgurgin-" + str(image_number * 2  - 1).zfill(2)
        with Image.open(f"img/otis/{imagename}.jpg") as img:
            # Ensure the image is in RGBA mode to handle transparency
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            draw = ImageDraw.Draw(img)
            
            # Define the font and size
            font = ImageFont.truetype("font/Tilda Script S Non-connect Demo.otf", 50)  # Adjust size as needed
            
            # Calculate text width and height to center it
            text_width = draw.textlength(new_text, font=font)
            text_height = 50
            text_position = ((img.width - text_width) / 2, 400)
            
            # Draw the new text centered
            draw.text(text_position, new_text, font=font, fill='black')
            footer = animalname + ' - ' + datetime.now().strftime("%B %d, %Y")
            animalfont = ImageFont.truetype("font/arial.ttf", 30)
            text_width = draw.textlength(footer, font=font)
            text_height = 20
            text_position = (10, img.height - 40)
            draw.text(text_position, footer, font=animalfont)
            # Save the modified image
            img.save(output_path, "PNG")
    else:
        imagename = "jgurgin-" + str(image_number - 10).zfill(2)
        with Image.open(f"img/bing/{imagename}.jpg") as img:
            # Ensure the image is in RGBA mode to handle transparency
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            draw = ImageDraw.Draw(img)
            
            # Define the font and size
            font = ImageFont.truetype("font/Tilda Script S Non-connect Demo.otf", 50)  # Adjust size as needed
            
            # Calculate text width and height to center it
            text_width = draw.textlength(new_text, font=font)
            text_height = 50
            text_position = ((img.width - text_width) / 2, 20)
            
            # Draw the new text centered
            draw.text(text_position, new_text, font=font, fill='black')
            footer = animalname + ' - ' + datetime.now().strftime("%B %d, %Y")
            animalfont = ImageFont.truetype("font/arial.ttf", 30)
            text_width = draw.textlength(footer, font=font)
            text_height = 20
            text_position = (10, img.height - 40)
            draw.text(text_position, footer, font=animalfont, fill='black')
            # Save the modified image
            img.save(output_path, "PNG")

# Example usage
change_image_text(12, "otis", "Hi Alice", f"{2}_out.png")