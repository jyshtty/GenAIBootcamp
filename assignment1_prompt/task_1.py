import tiktoken
from transformers import AutoTokenizer


# =========================================================
# TEXTS
# =========================================================

texts = {
    "English": """
The cat sat on the windowsill, watching the rain fall. Suddenly, a flash of lightning lit up the sky, startling the little creature. It leaped down and scurried to its favorite hiding spot under the bed.
""",

    "Spanish": """
El gato estaba sentado en el alféizar de la ventana, mirando la lluvia caer. De repente, un relámpago iluminó el cielo, sobresaltando a la pequeña criatura. Saltó y corrió a su escondite favorito debajo de la cama.
""",

    "Arabic": """
جلست القطة على حافة النافذة، تراقب هطول المطر. وفجأة، أضاءت ومضة من البرق السماء، مما أثار ذهول المخلوق الصغير. قفزت إلى أسفل وهرعت إلى مكان اختبائها المفضل تحت السرير.
""",

    "Hindi": """
बिल् ली खि ड़की पर बैठी हुई बा रि श को देख रही थी । अचा नक, आसमा न में बि जली चमकी , जि ससे छो टा जी व चौं क गया । वह नी चे कूद गई और बि स्तर के नी चे अपनी पसंदी दा छि पने की जगह पर भा ग गई।
"""
}


# =========================================================
# OPENAI TOKEN COUNT FUNCTION
# =========================================================

def count_openai_tokens(model_name, text):

    model_encoding = {
        "gpt-3.5-turbo": "cl100k_base",
        "gpt-4": "cl100k_base",
        "gpt-4o": "o200k_base"
    }

    encoding_name = model_encoding.get(model_name)

    if encoding_name is None:
        raise ValueError(f"Unsupported model: {model_name}")

    encoding = tiktoken.get_encoding(encoding_name)

    return len(encoding.encode(text))


# =========================================================
# LOAD HUGGINGFACE TOKENIZER
# =========================================================

def load_hf_tokenizer(model_name):

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        return tokenizer

    except Exception:
        return None


# =========================================================
# COUNT HF TOKENS
# =========================================================

def count_hf_tokens(model_name, text):

    tokenizer = load_hf_tokenizer(model_name)

    if tokenizer is None:
        return None

    return len(tokenizer.encode(text))


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("\n================ OPENAI MODELS ================\n")

    openai_models = [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4o"
    ]

    for model in openai_models:

        print(f"\nModel: {model}")
        print("-" * 50)

        for language, text in texts.items():

            token_count = count_openai_tokens(model, text)

            print(f"{language:<10} -> {token_count} tokens")


    # =====================================================
    # HUGGINGFACE MODELS
    # =====================================================

    hf_models = {
        "Llama-3.1-8B": "meta-llama/Meta-Llama-3.1-8B",
        "Mistral-v0.3": "mistralai/Mistral-7B-v0.3",
        "Mistral-Nemo": "mistralai/Mistral-Nemo-Base-2407"
    }

    print("\n================ HF MODELS ================\n")

    for display_name, repo_name in hf_models.items():

        print(f"\nModel: {display_name}")
        print("-" * 50)

        tokenizer = load_hf_tokenizer(repo_name)

        if tokenizer is None:
            print("Tokenizer could not be loaded.")
            continue

        for language, text in texts.items():

            token_count = count_hf_tokens(repo_name, text)

            print(f"{language:<10} -> {token_count} tokens")
