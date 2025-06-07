from transformers import pipeline

# Use a more powerful model (make sure it's installed or use Hugging Face Inference API)
generator = pipeline(
    "text-generation",
    model="tiiuae/falcon-rw-1b",
    tokenizer="tiiuae/falcon-rw-1b",
    max_new_tokens=60,
    temperature=0.7,
    do_sample=True,
)

def generate_headlines(brand_name, angle_description):
    prompt = (
        f"Write 3 short and compelling Facebook ad headlines for the product '{brand_name}' "
        f"based on this campaign angle: {angle_description}."
    )
    results = generator(prompt, num_return_sequences=3)
    print(f"results: {results}")
    headlines = [res["generated_text"].strip().split("\n")[0] for res in results]
    print(f"headlines: {headlines}")
    headlines = headlines[:3]
    print(f"headlines after slicing: {headlines}")
    return [[*headlines, *[""] * (3 - len(headlines))]]

def generate_subheadlines(brand_name, angle_description):
    prompt = (
        f"Write 2 persuasive subheadlines for Facebook ads for the product '{brand_name}', "
        f"using this campaign angle: {angle_description}. Each subheadline should be 1 sentence explaining the benefit."
    )
    results = generator(prompt, num_return_sequences=2)
    subheadlines = [res["generated_text"].strip().split("\n")[0] for res in results]
    subheadlines = subheadlines[:2]
    return [[*subheadlines, *[""] * (2 - len(subheadlines))]]