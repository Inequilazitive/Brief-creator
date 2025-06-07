import modal

# Create Modal app
app = modal.App("Brief-generator")

# Add your local code folder to the image at runtime
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install_from_requirements("requirements.txt")
    .add_local_dir(".", remote_path="/root")  # ✅ replaces mounts
)

@app.function(image=image, workdir="/root", timeout=600)
def run_gradio():
    import app.main
    app.main.main()
