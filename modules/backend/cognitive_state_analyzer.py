# modules/kognitive_state_analyzer.py
def classify_interaction_type(prompt):
    # Placeholder-Logik: du kannst das später durch Klassifikation oder Embedding ersetzen
    if "warum" in prompt.lower():
        return "explorativ"
    elif "was soll ich tun" in prompt.lower():
        return "exploitativ"
    elif "alternativen" in prompt.lower():
        return "konstruktiv"
    else:
        return "unklar"
