from flask import Flask, render_template, request, jsonify
import threading
import queue
import sys
import time

entrada = queue.Queue()
salida = queue.Queue()

# Captura de prints del bot
class CapturaPrints:
    def write(self, mensaje):
        mensaje = mensaje.strip()
        if mensaje:
            salida.put(mensaje)
    def flush(self):
        pass

# Hilo que ejecuta tu chatbot
def run_chat():
    import builtins
    import chat  # tu archivo original con chat_saludo()
    
    # Sobrescribir input() para leer de la cola
    builtins.input = lambda prompt="": entrada.get()
    # Sobrescribir stdout para capturar prints
    sys.stdout = CapturaPrints()
    
    chat.chat_saludo()  # ejecuta tu bot

threading.Thread(target=run_chat, daemon=True).start()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/mensaje", methods=["POST"])
def mensaje():
    msg = request.json.get("mensaje")
    entrada.put(msg)  # enviamos mensaje al bot
    
    # Esperamos hasta que haya respuesta del bot
    respuesta = salida.get()
    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    app.run(debug=True)
