# modal_app.py

import modal

# Define the app
app = modal.App("creative-brief-generator")

# Mount your current directory into the container
volume_mount = modal.Mount.from_local_dir(".", remote_path="/root")

# Build your image from requirements.txt
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install_from_requirements("requirements.txt")
)

@app.function(image=image, mounts=[volume_mount], timeout=600, workdir="/root")
def run_gradio():
    import app.main
    app.main.main()
