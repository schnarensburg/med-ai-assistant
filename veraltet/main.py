from pathlib import Path
from backend.core.meditron_interface import load_model, query_model
from modules.backend.interaction_logger import save_log
from modules.backend.interaction_logger import get_last_user_logs
from modules.backend.cognitive_state_analyzer import classify_interaction_type

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
    # bei bedarf kann man hier noch UI zur erstellung der user_id einbauen
    user_id = "user_1" 
    logs = get_last_user_logs(user_id, n=1000)  # oder ein anderes n, das alle bisherigen lädt
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
    # Man kann entscheiden ob hier die log gespeichert wird oder in dem router_engine.py
    save_log(
            prompt=prompt,
            response=response,
            decision=decision,  # oder eine echte Entscheidung, falls vorhanden
            interaction_type=interaction_type,
            number_of_prompts=len(logs),
            user_id=user_id)
    print("✅ Interaktion gespeichert.")
