# modal_app.py

import modal

# Define the app
app = modal.App("creative-brief-generator")

# Define the image (build from requirements)
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install_from_requirements("requirements.txt")
)

# Define the function to run the Gradio app
@app.function(image=image, timeout=600)
def run_gradio():
    import app.main
    app.main.main()
