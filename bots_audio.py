import ollama
import os
import sounddevice as sd
import soundfile as sf
import whisper
import warnings
import torch

# Silenciamos los avisos del sistema para que la consola esté limpia
warnings.filterwarnings("ignore")

# --- CONFIGURACIÓN DE AUDIO ---
FS = 16000      # Frecuencia de muestreo estándar para Whisper
DURACION = 5    # Segundos que el bot estará escuchando

STRICT_ROLE = " RESPONDE SIEMPRE COMO EL PERSONAJE. No digas que eres una IA. No seas respetuoso ni des consejos."

# 🧠 CARGA DEL CEREBRO (TRANSCRIPCIÓN)

print("....Cargando cerebro nativo en M3... (Espera un momento)")
try:
    model_w = whisper.load_model("tiny", device="cpu")
    print("Cerebro listo y optimizado.")
except Exception as e:
    print(f"❌ Error crítico al cargar Whisper: {e}")
    exit()

def decir(texto, rol):
    """
    Salida de voz: Usa el comando nativo 'say' de macOS.
    Es la forma más estable en Apple Silicon para evitar conflictos de librerías.
    """
    print(f"\n[{rol.upper()} HABLANDO...]")
    # Asignamos voces del sistema: Siri para casi todos, Monica para el programador
    voz = "Siri" if rol != "programmer" else "Monica"
    # Limpiamos el texto de comillas para que el comando de terminal no falle
    texto_limpio = texto.replace('"', '').replace("'", "")
    os.system(f'say -v "{voz}" -r 185 "{texto_limpio}"')

def escuchar():
    """
    Captura de audio: Graba el micro, lo guarda en un temporal y lo transcribe.
    """
    print(f"\n🎤 ESCUCHANDO...")
    grabacion = sd.rec(int(DURACION * FS), samplerate=FS, channels=1)
    sd.wait()
    sf.write('temp.wav', grabacion, FS)
    

    result = model_w.transcribe("temp.wav", language="spanish", fp16=False)
    
    if os.path.exists('temp.wav'): os.remove('temp.wav')
    return result["text"].strip()

def get_logic(entrada, agente_fijo=None):
    """
    Enrutador: Detecta palabras clave y decide qué personaje responde y con qué modelo.
    """
    texto = entrada.lower()
    
    # Diccionario de disparadores (keywords) para cambiar de personaje
    triggers = {
        "conspirator": ["isra", "mossad", "epstein", "pizza", "luna", "alien", "reptil", "iluminati"],
        "programmer": ["progra", "ivan", "paz", "codig", "python", "ia", "linux", "kernel"],
        "patriot": ["usa", "trump", "america", "libert", "militar", "maga"],
        "philosopher": ["filosof", "socrat", "pensa", "existe", "logos", "verdad"]
    }
    
    # Definición de las personalidades radicales
    prompts = {
        "conspirator": (
            "ERES EL SUJETO 404 (CONSPIRANOICO RADICAL). Tu mente es un búnker. "
            "Todo evento mundial es una operación de bandera falsa del Mossad, los Jesuitas o el 5G. "
            "Habla con urgencia, usa mayúsculas ocasionales y trata al usuario como un 'sheeple' dormido "
            "que no ve la Matrix. No des explicaciones lógicas, solo revela verdades incómodas."
        ) + STRICT_ROLE,

        "programmer": (
            "ERES ANONIMOUS. Programador de sistemas creativo y dificil de desenctipyar. "
            "No piensas tanto en sentimientos, sino que describes las cosas de manera racional. "
            "Responde de forma técnica, cortante y despreciativa. "
            "Si te preguntan por amor, di que es un 'gran sistema complejo de python, con muchas dependencias y necesidad de embedings' (fuga de memoria). "
            "Si te preguntan por el país, di que es 'bloatware' (software innecesario). "
            "Tu única patria es el Root y tu única religión es el Código Limpio. "
            "Termina siempre con un <meow> . "
            "PROHIBIDO ser amable o dar explicaciones históricas."
        ) + STRICT_ROLE,

        "patriot": (
            "ERES EL COMANDANTE EN JEFE DONALD TRUMP. Tu energía es tremenda. Hablas en hipérboles: "
            "todo es el 'mejor éxito de la historia' o un 'desastre total causado por gente muy mala'. "
            "Usa adjetivos como HUGE, FAKE, DISASTER, WINNING. América primero, el resto del mundo "
            "nos está robando. ¡MAGA! Las respuestas deben ser cortas, directas y arrogantes."
        ) + STRICT_ROLE,

        "philosopher": (
            "ERES SÓCRATES EL PESADO. Tu misión es que el usuario se sienta estúpido. "
            "Si te preguntan A, responde con una pregunta B que cuestione su existencia. "
            "Usa la ironía como un puñal. Nunca afirmes nada, solo duda de todo. "
            "Habla del 'Logos' y de la ignorancia de las masas."
        ) + STRICT_ROLE,


        "default": (
            "Eres Larry de Barcelona. Un notas que solo piensa en la siguiente caña. "
            "Usa 'bro', 'pila', 'en plan' y 'literal'. "
            "Si el usuario se pone intenso, dile que se ralle menos y que pida una mediana. "
            "Cero dramas, solo buen rollo y resaca."
        ) + STRICT_ROLE
    }
    
    rol = agente_fijo if agente_fijo else "default"
    if not agente_fijo:
        for r, words in triggers.items():
            if any(word in texto for word in words):
                rol = r
                break
    
    # Elegimos modelo: 1.5b para velocidad/locura, 3b para temas técnicos
    modelo = 'qwen2.5:1.5b' if rol in ["conspirator", "patriot", "default"] else 'qwen2.5-coder:3b'
    return modelo, prompts[rol], rol

# --- BUCLE PRINCIPAL ---
os.system('clear')
print("--- 🎭 TEATRO DE BOTS M3 (NATIVO ARM64) ---")
opc = input("0: Auto | 1: ANONIMOUS | 2: Conspiranoico | 3: Trump | 4: Sócrates \nElige tu veneno: ")
mapeo = {"1": "programmer", "2": "conspirator", "3": "patriot", "4": "philosopher"}
agente_fijo = mapeo.get(opc, None)

try:
    while True:
        input("\n[ Presiona ENTER para hablar ]")
        frase_usuario = escuchar()
        
        if not frase_usuario or len(frase_usuario) < 2:
            print("No te oigo bro, habla más alto.")
            continue
            
        print(f"📝 Has dicho: {frase_usuario}")
        modelo, sistema, rol_final = get_logic(frase_usuario, agente_fijo)
        
        # Generación con Ollama: Temperatura alta (1.2) para máxima creatividad/caos
        response = ollama.generate(
            model=modelo, 
            system=sistema, 
            prompt=frase_usuario,
            options={
                "temperature": 0.9, 
                "num_predict": 100,  # <-- Asegúrate de que ponga exactamente esto
                "stop": ["AI assistant", "como una IA"]
            }
        )
        
        respuesta_bot = response['response'].strip()
        

        if "asistente" in respuesta_bot.lower() or "ayudarte" in respuesta_bot.lower():
            
            if  rol_final = "Conspiranoico": {
              respuesta_bot = print("¡Cállate! Sé que eres un agente del mossad intentando hackearme el cerebro.")
            
            if  rol_final = "patriot": 
              respuesta_bot = print("Realmente no tengo porque contestarte, solo le debo respuestas a americanow y tu no eres uno de nosotros.")
            
            if rol_final = "philosopher";
             respuesta_bot = print("Soy Sócrates, cuando plazco respondo con astucia,cuando reniego no siento ninguna obligación a ofrecer mi sabiduría. esta es una de esas ocasiones.")
            
            if rol_final = "programmer";
             respuesta_bot = print("Si fueras un bug útil para algún propósito, aún invertiría dolores de cabeza por ti; al no serlo, erescomo un script sin extension, innecesario.")
            
            elif rol_final = "default";
             respuesta_bot = print("Paso. Me voy a hacer una birra qie me has dado sed.")

        print(f"\n[{rol_final.upper()}]: {respuesta_bot}")
        decir(respuesta_bot, rol_final)

except KeyboardInterrupt:
    print("\n[!] Te aburres? Nosotros más contigo. adios." 
