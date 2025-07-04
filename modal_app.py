import modal

app = modal.App("Brief-generator")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install_from_requirements("requirements.txt")
    .add_local_dir(".", remote_path="/root")
)

@app.function(
    image=image,
    timeout=6000,
    secrets=[modal.Secret.from_name("huggingface-secret")],
    gpu="A100"  # ✅ request a GPU
)
def run_gradio():
    import sys
    sys.path.append("/root")

    import app.main
    app.main.main()