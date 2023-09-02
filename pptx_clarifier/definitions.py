import os
import sys

root = sys.path[1]
uploads_directory = os.path.join(root, "pptx_clarifier", "uploads")
outputs_directory = os.path.join(root, "pptx_clarifier", "outputs")
os.makedirs(uploads_directory, exist_ok=True)
os.makedirs(outputs_directory, exist_ok=True)

base_url = 'localhost:5000'
