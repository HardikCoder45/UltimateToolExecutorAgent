import cv2
from typing import Optional
import base64
from openai import OpenAI

client = OpenAI()

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


 

def add_grid_to_image(image_path: str, grid_size: int = 50, label_interval: int = 100) -> Optional[str]:
    """
    Adds a coordinate grid to an image and saves the modified version.
    
    Args:
        image_path (str): Path to the input image file
        grid_size (int): Size of each grid cell in pixels
        label_interval (int): Interval for coordinate labels
        
    Returns:
        str: Path to the saved gridded image, or None if failed
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image from '{image_path}'. Check file path.")
        return None
    
    # Get image dimensions
    height, width, _ = image.shape
    
    # Define visual parameters
    grid_color = (192, 192, 192)  # Light gray for grid lines
    label_color = (0, 0, 0)       # Black for labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5              # Font size for labels
    thickness = 1                 # Line and text thickness

    # Draw vertical grid lines
    for x in range(0, width, grid_size):
        cv2.line(image, (x, 0), (x, height), grid_color, thickness)

    # Draw horizontal grid lines
    for y in range(0, height, grid_size):
        cv2.line(image, (0, y), (width, y), grid_color, thickness)

    # Add x-axis labels at the bottom
    for x in range(0, width, label_interval):
        cv2.putText(image, str(x), (x, height - 10), font, font_scale, label_color, thickness)

    # Add y-axis labels on the left
    for y in range(0, height, label_interval):
        cv2.putText(image, str(y), (5, y + 10), font, font_scale, label_color, thickness)

    # Create output directory if it doesn't exist
 
    
    output_path = f"../screenshots/grid_screenshot.png"
    
    
    # Save the modified image
    if cv2.imwrite(output_path, image):
        print(f"Image with grid saved to: {output_path}")
        base_64=encode_image(output_path)
        return f"data:image/png;base64,{base_64}"
    else:
        print("Error: Failed to save the gridded image")
        return None
    
  