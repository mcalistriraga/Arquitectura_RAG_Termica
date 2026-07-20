import os

SOURCE_DIR = "/home/manuelc/rag_maui_docs"

VALID_EXTENSIONS = [".cs", ".xaml", ".md", ".json"]


def detect_layer(file_path):
    path = file_path.lower()

    if "viewmodel" in path:
        return "ViewModel"
    elif "view" in path or ".xaml" in path:
        return "UI"
    elif "service" in path or "api" in path:
        return "Service"
    else:
        return "Model"


def get_files(base_path):
    files = []
    for root, _, filenames in os.walk(base_path):
        for f in filenames:
            if any(f.endswith(ext) for ext in VALID_EXTENSIONS):
                files.append(os.path.join(root, f))
    return files


def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"ERROR leyendo {file_path}: {e}"


def main():
    print("🔍 Leyendo proyecto MAUI...")

    files = get_files(SOURCE_DIR)

    print(f"📄 Archivos encontrados: {len(files)}")

    dataset = []

    for file in files:
        content = read_file(file)

        dataset.append({
            "file": file,
            "layer": detect_layer(file),
            "content": content
        })

    print("✅ Lectura completada")

    output_path = "scripts/output_raw.jsonl"

    with open(output_path, "w", encoding="utf-8") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")

    print(f"💾 Dataset estructurado guardado en: {output_path}")


if __name__ == "__main__":
    main()