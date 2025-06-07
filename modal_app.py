# modal_app.py

from modal import Image, Stub, web_endpoint
import os

# Set up the Modal stub
stub = Stub("creative-brief-generator")

# Define the image (Docker-like environment)
image = (
    Image.debian_slim(python_version="3.10")
    .pip_install_from_requirements("requirements.txt")
    .env({"ENV": "production"})  # optionally load any .env vars
)

# Define the function to run the Gradio app
@stub.function(image=image, gpu="any", allow_concurrent_inputs=10, timeout=600)
def run_gradio():
    import app.main
    app.main.main()
