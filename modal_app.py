import modal

# Create Modal app
app = modal.App("creative-brief-generator")

# Build image with dependencies and include your code
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install_from_requirements("requirements.txt")
    .add_local_dir(".", remote_path="/root")  # includes your app/
    .set_workdir("/root")                     # ✅ sets working directory here
)

@app.function(image=image, timeout=600)
def run_gradio():
    import app.main
    app.main.main()
