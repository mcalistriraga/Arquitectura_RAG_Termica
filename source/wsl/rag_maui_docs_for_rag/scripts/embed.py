import os
import json
import requests
import time

INPUT_FILE = "output_raw.jsonl"
OUTPUT_FILE = "embeddings.jsonl"

OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"

CPU_LOAD = 40
MAX_SLEEP = 1.5


def get_sleep_time():
    return (CPU_LOAD / 100) * MAX_SLEEP


def get_embedding(text):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": text
        }
    )

    if response.status_code == 200:
        return response.json()["embedding"]

    print("❌ Error:", response.text)
    return None


def main():

    print("🧠 Embeddings estructurados iniciando...")

    if not os.path.exists(INPUT_FILE):
        print("❌ No existe input")
        return

    sleep_time = get_sleep_time()

    with open(INPUT_FILE, "r", encoding="utf-8") as f, \
         open(OUTPUT_FILE, "a", encoding="utf-8") as out:

        for line in f:

            item = json.loads(line)

            text = f"""
FILE: {item['file']}
LAYER: {item['layer']}

CONTENT:
{item['content']}
"""

            embedding = get_embedding(text)

            if embedding is None:
                continue

            out.write(json.dumps({
                "file": item["file"],
                "layer": item["layer"],
                "content": item["content"],
                "embedding": embedding
            }) + "\n")

            out.flush()

            time.sleep(sleep_time)

    print("✅ Embeddings estructurados listos")


if __name__ == "__main__":
    main()