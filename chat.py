import random
import spacy
import re
import unicodedata
import difflib

# Cargar modelo de español
nlp = spacy.load("es_core_news_sm")

# ======================
# Diccionarios de frases
# ======================
saludos_iniciales = ["hola", "buenas", "qué tal", "hey", "saludos", "buen día", "buenas tardes", "buenas noches"]
respuestas_saludo = ["¡Hola! ¿Cómo estás?", "Buenas, ¿qué tal te va?", "¡Hey! ¿Cómo te encuentras hoy?"]

respuestas_bien = ["¡Me alegra mucho!", "Genial, me da gusto escuchar eso.", "Perfecto, entonces podemos hablar de videojuegos."]
respuestas_mal = ["Ánimo, espero que te mejores pronto", "Vaya, lamento escuchar eso. Quizá hablar de videojuegos te anime un poco."]

transicion_recomendaciones = ["¿Quieres que te recomiende algunos videojuegos?", "¿Te gustaría que hablemos de videojuegos? Puedo sugerirte por género o plataforma."]

# Más despedidas
despedidas = [
    "adios", "adiós", "chao", "hasta luego", "me voy", "bye", "nos vemos",
    "ya no", "eso es todo", "listo", "terminamos", "de nada mas", "gracias no"
]

confirmaciones = ["sí", "si", "claro", "afirmativo", "dale", "por favor", "obvio", "de una"]
negaciones = ["no", "nop", "nah", "negativo"]

plataformas = ["pc", "playstation", "xbox", "nintendo"]
generos = ["acción", "aventura", "rpg", "deportes", "shooter", "estrategia"]

# ======================
# Sinónimos de géneros
# ======================
sinonimos_generos = {
    "rpg": ["rpg", "rol", "juego de rol", "juegos de rol"],
    "acción": ["accion", "de accion", "peleas", "combate"],
    "aventura": ["aventura", "exploracion", "viaje", "historia"],
    "deportes": ["deportes", "futbol", "basket", "baloncesto", "soccer", "nba", "fifa"],
    "shooter": ["shooter", "disparos", "fps", "tiros", "guerra", "armas"],
    "estrategia": ["estrategia", "tactica", "planificacion", "turnos", "estrategico"]
}

generos = list(sinonimos_generos.keys())  # ["rpg", "acción", "aventura", ...]

# ======================
# Detección de género
# ======================
def detectar_genero(texto):
    texto = normalizar(texto)
    for genero, palabras in sinonimos_generos.items():
        for p in palabras:
            if p in texto:
                return genero
    return aproximar(texto, generos)

# ======================
# Sinónimos de plataformas
# ======================
sinonimos_plataformas = {
    "pc": ["pc", "computadora", "ordenador", "steam"],
    "playstation": ["playstation", "ps", "ps4", "ps5", "play", "playstaton", "pley"],
    "xbox": ["xbox", "x box", "xbx"],
    "nintendo": ["nintendo", "switch", "nintendoswitch", "nds"]
}

plataformas = list(sinonimos_plataformas.keys())  # ["pc", "playstation", "xbox", "nintendo"]

# ======================
# Detección de plataforma
# ======================
def detectar_plataforma(texto):
    texto = normalizar(texto)
    for plataforma, palabras in sinonimos_plataformas.items():
        for p in palabras:
            if p in texto:
                return plataforma
    return aproximar(texto, plataformas)

# ======================
# Utilidades de texto
# ======================
def normalizar(texto):
    texto = texto.lower()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto

def procesar_texto(texto):
    doc = nlp(normalizar(texto))
    return [token.lemma_ for token in doc]

def aproximar(palabra, opciones):
    coincidencias = difflib.get_close_matches(palabra, opciones, n=1, cutoff=0.6)
    return coincidencias[0] if coincidencias else None

def contiene_saludo(texto):
    texto_normalizado = normalizar(texto)
    for saludo in saludos_iniciales:
        if saludo in texto_normalizado:
            return True
    return False

# ======================
# Chat en bucle con estados
# ======================
def chat_saludo():
    print("ChatBot: ¡Hola! Soy tu asistente gamer")
    estado = "saludo"

    while True:
        usuario = input("Tú: ")
        lemas = procesar_texto(usuario)

        # Manejo unificado de salida
        if any(p in lemas for p in despedidas):
            print("ChatBot: ¡Hasta luego! Espero que disfrutes jugando")
            break

        # ---------------------
        # Manejo de estados
        # ---------------------
        if contiene_saludo(usuario):
            print("ChatBot:", random.choice(respuestas_saludo))
            estado = "animo"

        elif estado == "animo":
            if any(p in lemas for p in ["bien", "excelente", "genial", "perfecto", "tranquilo"]):
                print("ChatBot:", random.choice(respuestas_bien))
                print("ChatBot:", random.choice(transicion_recomendaciones))
                estado = "esperando_confirmacion"
            elif any(p in lemas for p in ["mal", "cansado", "aburrido", "triste"]):
                print("ChatBot:", random.choice(respuestas_mal))
                print("ChatBot:", random.choice(transicion_recomendaciones))
                estado = "esperando_confirmacion"

        elif estado == "esperando_confirmacion":
            if any(p in lemas for p in confirmaciones):
                print("ChatBot: ¡Perfecto! ¿Quieres que te recomiende por *género* o por *plataforma*?")
                estado = "criterio"
            elif any(p in lemas for p in negaciones):
                print("ChatBot: Vale. Si cambias de opinión, dime *juegos* y te hago una recomendación")
                estado = "esperando_juegos"  # estado que espera confirmación o despedida
            else:
                print("ChatBot: Perdona, ¿quieres que te recomiende juegos o no?")

        elif estado == "esperando_juegos":
            if any(p in lemas for p in confirmaciones):
                print("ChatBot: ¡Genial! ¿Quieres que te recomiende por *género* o por *plataforma*?")
                estado = "criterio"
            elif any(p in lemas for p in despedidas):
                print("ChatBot: ¡Hasta luego! Espero que disfrutes jugando")
                break
            else:
                print("ChatBot: Estoy esperando que me digas si quieres hablar de juegos o una despedida")
                estado = "esperando_juegos"  # sigue en el mismo estado hasta recibir respuesta válida

        elif estado == "criterio":
            if "plataforma" in lemas:
                print("ChatBot: Perfecto dime qué plataforma usas: PC, PlayStation, Xbox o Nintendo.")
                estado = "plataforma"
            elif "genero" in lemas:
                print("ChatBot: Genial dime qué género prefieres: acción, aventura, RPG, deportes, shooter, estrategia.")
                estado = "genero"
            else:
                print("ChatBot: ¿Prefieres por género o por plataforma?")

        elif estado == "plataforma":
            plataforma_detectada = detectar_plataforma(usuario)
            if plataforma_detectada:
                print(f"ChatBot: Buenísima elección Aquí tienes algunos juegos recomendados para {plataforma_detectada.capitalize()}:")
                if plataforma_detectada == "pc":
                    print("- Counter-Strike 2\n- Baldur’s Gate 3\n- Minecraft")
                elif plataforma_detectada == "playstation":
                    print("- God of War: Ragnarök\n- Spider-Man 2\n- Bloodborne")
                elif plataforma_detectada == "xbox":
                    print("- Halo Infinite\n- Forza Horizon 5\n- Gears 5")
                elif plataforma_detectada == "nintendo":
                    print("- Zelda: Tears of the Kingdom\n- Mario Kart 8 Deluxe\n- Super Smash Bros Ultimate")
                estado = "fin"
            else:
                print("ChatBot: No entendí la plataforma prueba con PC, PlayStation, Xbox o Nintendo.")

        elif estado == "genero":
            genero_detectado = detectar_genero(usuario)
            if genero_detectado:
                print(f"ChatBot: Buenísima, aquí tienes unos juegos de {genero_detectado}:")
                if genero_detectado == "rpg":
                    print("- The Witcher 3\n- Final Fantasy XVI\n- Persona 5")
                elif genero_detectado == "acción":
                    print("- Devil May Cry 5\n- Sekiro: Shadows Die Twice\n- Bayonetta 3")
                elif genero_detectado == "aventura":
                    print("- Uncharted 4\n- The Last of Us\n- Tomb Raider")
                elif genero_detectado == "deportes":
                    print("- FIFA 24\n- NBA 2K24\n- eFootball")
                elif genero_detectado == "shooter":
                    print("- Call of Duty: Modern Warfare II\n- Apex Legends\n- Overwatch 2")
                elif genero_detectado == "estrategia":
                    print("- Age of Empires IV\n- Civilization VI\n- StarCraft II")
                estado = "fin"
            else:
                print("ChatBot: No entendí el género prueba con acción, aventura, RPG, deportes, shooter o estrategia.")

        elif estado == "fin":
            if any(p in lemas for p in ["gracias", "vale", "ok", "perfecto", "listo"]):
                print("ChatBot: ¡De nada! ¿Quieres otra recomendación o terminamos por hoy?")
                estado = "esperando_respuesta"

            elif any(p in lemas for p in confirmaciones):
                print("ChatBot: ¡Perfecto! ¿Quieres que te recomiende por *género* o por *plataforma*?")
                estado = "criterio"

            elif any(p in lemas for p in negaciones + despedidas):
                print("ChatBot: ¡Hasta luego! Espero que disfrutes jugando")
                break

            else:
                if "juego" in lemas:
                    print("ChatBot: ¿Quieres que te recomiende por *género* o por *plataforma*?")
                    estado = "criterio"
                elif "genero" in lemas:
                    print("ChatBot: Genial dime qué género prefieres: acción, aventura, RPG, deportes, shooter, estrategia.")
                    estado = "genero"
                elif "plataforma" in lemas:
                    print("ChatBot: Perfecto dime qué plataforma usas: PC, PlayStation, Xbox o Nintendo.")
                    estado = "plataforma"
                else:
                    respuestas_fallback = [
                        "Perdona, no te entendí ¿Quieres otra recomendación o terminamos por hoy?",
                        "Mmm no estoy seguro de lo que dijiste pero dime: ¿quieres más juegos o lo dejamos aquí?",
                        "Jajaja no entendí eso pero seguimos, ¿te recomiendo más juegos?"
                    ]
                    print("ChatBot:", random.choice(respuestas_fallback))
                    estado = "esperando_respuesta"

        elif estado == "esperando_respuesta":
            if any(p in lemas for p in confirmaciones):
                print("ChatBot: ¡Perfecto! ¿Quieres que te recomiende por *género* o por *plataforma*?")
                estado = "criterio"
            elif any(p in lemas for p in negaciones + despedidas):
                print("ChatBot: ¡Hasta luego! Espero que disfrutes jugando")
                break
            else:
                print("ChatBot: No entendí, responde con *sí* si quieres otra recomendación o *no* para terminar.")
                estado = "esperando_respuesta"

if __name__ == "__main__":
    chat_saludo()
