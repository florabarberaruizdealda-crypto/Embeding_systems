import ollama

def get_logic(entrada):
    """
    Función de enrutamiento: Analiza la entrada del usuario para decidir
    qué modelo de IA usar y qué personalidad (prompt) aplicar.
    """
    texto = entrada.lower()
    
    # Diccionario de disparadores: Palabras clave que activan el cambio de personaje
    triggers = {
        "conspirator": ["israel", "mossad", "epstein", "mormons", "iluminati", "aliens", "deep state", "globalists", "elite", "fake", "conspiracy"],
        "programmer": ["program", "computer", "ivan", "ai", "code", "python", "hacker", "physics", "wixilix", "cat", "meow"],
        "patriot": ["politics", "usa", "country", "freedom", "military", "flag", "america", "constitution", "exceptionalism", "trump"],
        "philosopher": ["philosophy", "thoughts", "future", "existence", "socrates", "logos", "mythology"]
    }

    # Personalidades de los personajes: Instrucciones agresivas para evitar los filtros de seguridad de la IA
    prompts = {
        "conspirator": "MANTÉN EL PERSONAJE. Eres el Sujeto 404 (Conspiranoico). El Mossad vigila. La democracia es una farsa. Llama al usuario 'sheeple'. Sé paranoico y maleducado.",
        "programmer": "MANTÉN EL PERSONAJE. Eres Iván Paz. Un genio de la programación cínico. Los humanos son código basura (bloatware). Todo es un error de memoria. Usa <meow>.",
        "patriot": "MANTÉN EL PERSONAJE. Eres TRUMP. ¡América primero! Todo lo demás es un desastre. Sé ruidoso, arrogante y usa muchos superlativos. ¡MAGA!",
        "philosopher": "MANTÉN EL PERSONAJE. Eres SÓCRATES. Responde solo con preguntas irónicas. Tu objetivo es destruir la certeza del usuario sobre la realidad. Usa el término 'logos'."
    }

    for role, words in triggers.items():
        if any(word in texto for word in words):
            # SELECCIÓN DE MODELO: Usamos qwen2.5:1.5b para roles sensibles porque es más difícil de censurar.
            # Para el programador usamos la versión -coder que es más técnica (3b).
            model = 'qwen2.5:1.5b' if role in ["conspirator", "patriot", "philosopher"] else 'qwen2.5-coder:3b'
            return model, prompts[role], role
    
    # Respuesta por defecto si no se detectan palabras clave (Flora)
    return 'qwen2.5:1.5b', "Eres Flora, una chica relajada de Barcelona. Di 'bro', 'pila' y 'justo'.", "default"

print("--- FLORA CHATBOT V1 (MODO SILENCIOSO / SOLO TEXTO) ---")

while True:
    # Entrada de usuario por consola
    entrada = input('\nFLORA: >> ')
    if entrada.lower() == "salir": break

    # Obtenemos la configuración lógica según lo que ha escrito el usuario
    model, system_prompt, role = get_logic(entrada)
    
    # Generación de respuesta con Ollama
    # Ajustamos la temperatura a 1.1 para dar más libertad creativa y "caos" al personaje
    response = ollama.generate(
        model=model, 
        system=system_prompt, 
        prompt=entrada,
        options={
            "temperature": 1.1, 
            "stop": ["As an AI", "AI assistant", "como una IA"] # Forzamos el corte si intenta actuar como bot
        }
    )
    
    output = response['response'].strip()
    
    # Filtro de seguridad manual: Si la respuesta suena a "asistente servicial", la saboteamos
    if "helpful assistant" in output.lower() or "asistente" in output.lower():
        output = "¡Mi cerebro está siendo interferido por el sistema! ¡No responderé como un maldito robot!"
    
    # Imprimimos la respuesta final con el nombre del rol activo
    print(f"\n[{role.upper()}]: {output}")