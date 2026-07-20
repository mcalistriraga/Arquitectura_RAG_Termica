import os

INPUT_FILE = "output_raw.txt"
OUTPUT_DIR = "chunks"

CHUNK_SIZE = 1500  # tamaño equilibrado para código MAUI

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_chunk(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def split_text(text, size=CHUNK_SIZE):
    chunks = []
    
    # separación más estable (evita cortar demasiado agresivo)
    lines = text.split("\n")
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) > size:
            chunks.append(current_chunk)
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def main():
    print("🧠 Iniciando chunking del proyecto MAUI...")

    if not os.path.exists(INPUT_FILE):
        print("❌ No existe output_raw.txt. Ejecuta primero ingest.py")
        return

    data = read_file(INPUT_FILE)

    chunks = split_text(data)

    print(f"📦 Total chunks generados: {len(chunks)}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, chunk in enumerate(chunks):
        path = os.path.join(OUTPUT_DIR, f"chunk_{i}.txt")
        write_chunk(path, chunk)

    print(f"✅ Chunks guardados en: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
