from flask import Flask, jsonify, render_template, request
from pathlib import Path
from chatbot import ChatbotTutorias
from flask_cors import CORS


app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
CORS(app)

try:
    chatbot = ChatbotTutorias(
    rutas_corpus={
        "Tutorías": BASE_DIR / "datos" / "corpus_tutorias.txt",
        "Malla curricular": BASE_DIR / "datos" / "corpus_malla.txt",
        "Acreditación ICACIT": BASE_DIR / "datos" / "corpus_icacit.txt"
    }
)

    print("Corpus cargado correctamente.")

except (FileNotFoundError, ValueError) as error:
    print(f"Error al iniciar el chatbot: {error}")
    chatbot = None


@app.route("/")
def inicio():
    """
    Muestra la página principal.
    """

    return render_template(
        "index.html"
    )


@app.route("/api/chat", methods=["POST"])
def conversar():
    """
    Recibe una pregunta y devuelve la respuesta del chatbot.
    """

    if chatbot is None:
        return jsonify({
            "respuesta": (
                "El chatbot no pudo cargar el corpus. "
                "Revisa el archivo datos/corpus_tutorias.txt."
            ),
            "similitud": 0.0
        }), 500

    datos = request.get_json(
        silent=True
    )

    if not datos:
        return jsonify({
            "respuesta": "No se recibieron datos válidos.",
            "similitud": 0.0
        }), 400

    pregunta = datos.get(
        "mensaje",
        ""
    ).strip()

    if not pregunta:
        return jsonify({
            "respuesta": "Por favor, escribe una pregunta.",
            "similitud": 0.0
        }), 400

    resultado = chatbot.responder(
        pregunta
    )
    print(resultado)

    return jsonify(
        resultado
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
