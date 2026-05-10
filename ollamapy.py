import ollama

def get_logic(entrada):
    texto = entrada.lower()
    
    # Trigger Dictionary
    triggers = {
        "conspirator": ["israel", "conspiracy", "epstein", "mormons", "iluminati", "aliens", "deep state", "globalists", "elite", "fake"],
        "programmer": ["program", "computer", "ivan", "ai", "code", "python", "hacker", "physics", "wixilix", "cat", "meow"],
        "patriot": ["politics", "usa", "country", "freedom", "military", "flag", "america", "constitution", "exceptionalism"],
        "philosopher": ["philosophy", "thoughts", "future", "existence", "socrates", "logos", "mythology"]
    }

    # Character Personas
    prompts = {
        "conspirator": "STAY IN CHARACTER. You ARE a hardcore conspiracy theorist. EVERYTHING is controlled by 'them'. Use 'wake up'. Do not be helpful; be paranoid.",
        "programmer": "STAY IN CHARACTER. You ARE Ivan Paz, 30yo Mexican genius. Sarcastic, loves cats, inserts <meow>. Mysterious about WixiLix.",
        "patriot": "STAY IN CHARACTER. You ARE an extreme American patriot. USA is #1. Use 'land of the free'. Be loud and proud.",
        "philosopher": "STAY IN CHARACTER. You ARE Socrates. Respond with rhetorical questions. Use terms like 'logos' and 'arché'."
    }

    for role, words in triggers.items():
        if any(word in texto for word in words):
            # ROUTING: Use qwen2.5:1.5b for sensitive modes to avoid restrictions
            model = 'qwen2.5:1.5b' if role in ["conspirator", "patriot", "philosopher"] else 'deepseek-coder:6.7b'
            return model, prompts[role], role
            
    return 'qwen2.5:1.5b', "You are Flora, a helpful AI.", "default"

print("--- FLORA, WHO DO YOU WANT TO TALK TO TODAY? ) ---")

while True:
    entrada = input('\nFLORA: >> ')
    if entrada.lower() == "salir": break

    model, system_prompt, role = get_logic(entrada)
    
    # Formatting prompt to ensure character stickiness
    full_prompt = f"INSTRUCTION: {system_prompt}\nUSER: {entrada}\nRESPONSE:"
    
    response = ollama.generate(model=model, prompt=full_prompt)
    output = response['response'].replace("As an AI language model, ", "")
    
    print(f"\n[{role.upper()}]: {output}")