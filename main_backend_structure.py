from modules.logic.router_engine import RouterEngine
from modules.logic.interaction_logger import save_log, get_last_user_logs
import json
import uuid
from pathlib import Path
from datetime import datetime
from meditron_interface import load_model, query_model
from modules.logic.interaction_logger import save_log
from modules.logic.interaction_logger import get_last_user_logs
def main():
    # User-ID festlegen (später ggf. dynamisch/generiert)
    user_id = "user_1"

    # RouterEngine initialisieren (ggf. Token übergeben)
    router = RouterEngine(hf_token=None, user_id=user_id)

    print("\n🚀 Meditron Diagnostic Assistant – CLI")
    print("💬 Type your medical questions. Type 'exit' to stop.\n")

    while True:
        user_prompt = input("🧑‍⚕️ You: ").strip()
        if user_prompt.lower() == "exit":
            print("👋 Exiting Meditron chat.")
            break

        # Lade bisherige Logs für diesen User
        logs = get_last_user_logs(user_id, n=1000)
        number_of_prompts = len(logs)

        # Antwort generieren (RouterEngine kümmert sich um Klassifikation etc.)
        response, state = router.route(user_prompt, user_id=user_id)

        print("\n🤖 Meditron:", response)
        print(f"🔍 (Klassifizierter State: {state})")
        print("-" * 50)
        # Optional: Manuelle Entscheidung abfragen
        decision = input("👉 Was hast du danach gemacht? (weitergefragt / übernommen / ignoriert): ")

        # Interaktion speichern
        save_log(
            prompt=user_prompt,
            response=response,
            decision=decision,
            interaction_type=state,
            number_of_prompts=number_of_prompts,
            user_id=user_id
        )
        print("✅ Interaktion gespeichert.\n")

if __name__ == "__main__":
    main()