import modal
from modal import mount

# Define the app
app = modal.App("creative-brief-generator")

# Mount your local code into the container
volume_mount = mount.Mount.from_local_dir(".", remote_path="/root")

# Image with dependencies
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install_from_requirements("requirements.txt")
)

# Run Gradio app
@app.function(image=image, mounts=[volume_mount], workdir="/root", timeout=600)
def run_gradio():
    import app.main
    app.main.main()
