import modal

# Create Modal app
app = modal.App("creative-brief-generator")

# Image with your code and dependencies
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install_from_requirements("requirements.txt")
    .add_local_dir(".", remote_path="/root")  # Your code will live in /root
)

@app.function(image=image, timeout=600)
def run_gradio():
    import sys
    sys.path.append("/root")  # ✅ Add your project to Python path

    import app.main
    app.main.main()
