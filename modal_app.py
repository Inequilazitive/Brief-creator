import modal

app = modal.App("brief-generator")

# Build Docker image with WeasyPrint dependencies and local code
image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install(
        "libpango-1.0-0",
        "libcairo2",
        "libgdk-pixbuf2.0-0",
        "libglib2.0-0",
        "libgobject-2.0-0",
        "libffi-dev",
        "shared-mime-info",
    )
    .pip_install_from_requirements("requirements.txt")
    .add_local_dir(".", remote_path="/root")
)

# Define the web-serving function as an ASGI app
@app.function(
    image=image,
    min_containers=1,
    scaledown_window=60 * 60,
    # gradio requires sticky sessions
    # so we limit the number of concurrent containers to 1
    # and allow it to scale to 100 concurrent inputs
    max_containers=1,
    secrets=[modal.Secret.from_name("huggingface-secret")],
    gpu="L4",
)
@modal.asgi_app()
def gradio_web_app():
    import sys
    sys.path.append("/root")

    import gradio as gr
    from fastapi import FastAPI
    from gradio.routes import mount_gradio_app

    from app.main import generate_gradio_interface  # You'll need to create this helper

    demo = generate_gradio_interface()  # This should return a gr.Interface object
    demo.queue(max_size=5)

    return mount_gradio_app(app=FastAPI(), blocks=demo, path="/")
