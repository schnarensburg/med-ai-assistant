import json
import uuid
from pathlib import Path
from datetime import datetime
from meditron_interface import load_model, query_model
from modules.interaction_logger import save_log
from modules.cognitive_state_analyzer import classify_interaction_type

def load_prompt(file_path=None):
    if file_path is None:
        # Basisverzeichnis des aktuellen Skripts
        base_dir = Path(__file__).parent.resolve()
        file_path = base_dir / "prompts" / "default_prompt.txt"
        file_path = file_path.resolve()  # Umwandeln in absoluten Pfad    
    print(f"Lade Prompt von: {file_path}")
    with open(file_path, "r") as f:
        return f.read()


if __name__ == "__main__":
    print("🚀 Meditron Diagnostic Assistant – CLI\n")

    prompt = load_prompt()
    print(f"📌 Prompt:\n{prompt}\n")

    print("🔄 Lade Modell...")
    pipe = load_model()

    print("🧠 Anfrage an Meditron...")
    response = query_model(pipe, prompt)
    print(f"\n💬 Antwort:\n{response}\n")

    print("📋 Automatische Klassifikation des Interaktionstyps...")
    interaction_type = classify_interaction_type(prompt)
    print(f"🔍 Klassifizierter Interaktionstyp: {interaction_type}\n")

    # Manuelle Bewertung der Interaktion
    decision = input("👉 Was hast du danach gemacht? (weitergefragt / übernommen / ignoriert): ")
    # interaction_type = input("👉 Interaktionstyp (explorativ / exploitativ / konstruktiv / schädlich): ")

    save_log(prompt, response, decision, interaction_type)
    print("✅ Interaktion gespeichert.")
