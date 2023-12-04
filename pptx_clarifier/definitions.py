import os
import sys

# Get the root directory of the project
root = sys.path[1]

# Define the directories for uploads and outputs
uploads_directory = os.path.join(root, "pptx_clarifier", "uploads")
outputs_directory = os.path.join(root, "pptx_clarifier", "outputs")

# Create the directories if they don't exist
os.makedirs(uploads_directory, exist_ok=True)
os.makedirs(outputs_directory, exist_ok=True)

# Define the base URL for the application
base_url = 'localhost:5000'
