import random
import re
import unicodedata
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ChatbotTutorias:
    """
    Chatbot que trabaja con varios corpus independientes
    usando TF-IDF y similitud del coseno.
    """

    def __init__(self, rutas_corpus: dict):
        self.rutas_corpus = {
            categoria: Path(ruta)
            for categoria, ruta in rutas_corpus.items()
        }

        # Estado conversacional para recordar si le pedimos sus datos al usuario
        self.esperando_datos_tutoria = False

        self.saludos = [
            "¡Hola! ¿En qué puedo ayudarte?",
            "¡Buenas! Puedes preguntarme sobre tutorías, malla curricular o ICACIT.",
            "¡Hola! Estoy aquí para orientarte sobre la Escuela Profesional.",
            "¡Hola! ¿Qué información necesitas?"
        ]

        self.despedidas = [
            "¡Hasta pronto! Espero haberte ayudado.",
            "¡Hasta luego! Puedes volver cuando tengas otra consulta.",
            "¡Nos vemos! Que tengas un buen día."
        ]

        self.stopwords_espanol = [
            "a", "al", "algo", "algunas", "algunos", "ante", "antes",
            "como", "con", "contra", "cual", "cuando", "de", "del",
            "desde", "donde", "el", "ella", "ellas", "ellos", "en",
            "entre", "era", "eran", "eres", "es", "esa", "esas",
            "ese", "eso", "esos", "esta", "estaba", "estaban",
            "estado", "estamos", "estan", "estar", "estas", "este",
            "esto", "estos", "fue", "fueron", "ha", "hace", "hacia",
            "han", "hasta", "hay", "la", "las", "le", "les", "lo",
            "los", "mas", "me", "mi", "mis", "mucho", "muy", "no",
            "nos", "o", "para", "pero", "por", "porque", "que", "se",
            "ser", "si", "sin", "sobre", "son", "su", "sus", "tambien",
            "te", "tiene", "tienen", "tu", "un", "una", "uno", "unos",
            "y", "ya"
        ]

        self.fragmentos = []
        self.categorias = []

        self.vectorizador = None
        self.matriz_tfidf = None

        self._preparar_chatbot()

    def _leer_archivo(self, ruta: Path) -> str:
        if not ruta.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo: {ruta}"
            )

        try:
            return ruta.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ruta.read_text(
                encoding="latin-1",
                errors="ignore"
            )

    def _normalizar(self, texto: str) -> str:
        texto = texto.lower().strip()

        texto = unicodedata.normalize(
            "NFD",
            texto
        )

        texto = "".join(
            caracter
            for caracter in texto
            if unicodedata.category(caracter) != "Mn"
        )

        texto = re.sub(
            r"[^a-z0-9ñ\s]",
            " ",
            texto
        )

        texto = re.sub(
            r"\s+",
            " ",
            texto
        )

        return texto.strip()

    def _separar_bloques(self, texto: str) -> list:
        texto = texto.replace("\r", "").strip()

        bloques_por_titulo = re.split(
            r"\n(?=###\s+)",
            texto
        )

        bloques_limpios = [
            bloque.strip()
            for bloque in bloques_por_titulo
            if len(bloque.strip()) >= 30
        ]

        if len(bloques_limpios) > 1:
            return bloques_limpios

        texto_lineal = re.sub(
            r"\s+",
            " ",
            texto
        ).strip()

        oraciones = re.split(
            r"(?<=[.!?])\s+",
            texto_lineal
        )

        oraciones = [
            oracion.strip()
            for oracion in oraciones
            if len(oracion.strip()) >= 25
        ]

        fragmentos = []

        for indice in range(len(oraciones)):
            grupo = oraciones[indice:indice + 3]

            if grupo:
                fragmentos.append(
                    " ".join(grupo)
                )

        return fragmentos

    def _limpiar_respuesta(self, texto: str) -> str:
        lineas = texto.splitlines()
        lineas_limpias = []

        for linea in lineas:
            linea = linea.strip()

            if not linea:
                continue

            if linea.startswith("###"):
                continue

            if linea == "---":
                continue

            linea = linea.replace("_", " ")
            lineas_limpias.append(linea)

        respuesta = " ".join(lineas_limpias)

        respuesta = re.sub(
            r"\s+",
            " ",
            respuesta
        ).strip()

        return respuesta

    def _preparar_chatbot(self) -> None:
        for categoria, ruta in self.rutas_corpus.items():
            texto = self._leer_archivo(ruta)
            bloques = self._separar_bloques(texto)

            if not bloques:
                print(
                    f"Advertencia: el corpus {categoria} está vacío."
                )
                continue

            for bloque in bloques:
                self.fragmentos.append(bloque)
                self.categorias.append(categoria)

        if not self.fragmentos:
            raise ValueError(
                "No se encontró contenido válido en los corpus."
            )

        self.vectorizador = TfidfVectorizer(
            preprocessor=self._normalizar,
            lowercase=False,
            stop_words=self.stopwords_espanol,
            ngram_range=(1, 2),
            max_features=30000
        )

        self.matriz_tfidf = self.vectorizador.fit_transform(
            self.fragmentos
        )

        print(
            f"Se cargaron {len(self.fragmentos)} bloques "
            f"de {len(self.rutas_corpus)} corpus."
        )

    def _es_saludo(self, texto: str) -> bool:
        saludos = [
            "hola", "buenas", "buenos dias", "buenas tardes",
            "buenas noches", "hey", "saludos"
        ]
        return self._normalizar(texto) in saludos

    def _es_despedida(self, texto: str) -> bool:
        despedidas = [
            "adios", "chau", "hasta luego", "nos vemos", "salir"
        ]
        return self._normalizar(texto) in despedidas

    def _es_agradecimiento(self, texto: str) -> bool:
        agradecimientos = [
            "gracias", "muchas gracias", "te agradezco", "gracias por ayudarme"
        ]
        return self._normalizar(texto) in agradecimientos

    # -------------------------------------------------------------
    # NUEVOS MÉTODOS AUXILIARES
    # -------------------------------------------------------------
    def _extraer_codigo(self, texto: str) -> str:
        """Busca un código universitario numérico de 6 dígitos."""
        match = re.search(r'\b\d{6}\b', texto)
        return match.group(0) if match else None

    def _extraer_nombre_consulta(self, texto: str) -> str:
        """Limpia frases conversacionales para quedarse solo con el nombre."""
        texto_norm = self._normalizar(texto)
        palabras_ruido = [
            "podrias", "decirme", "quien", "es", "mi", "tutor", "tutora",
            "del", "alumno", "estudiante", "me", "llamo", "soy", "nombre",
            "codigo", "unsaac", "saber", "buscar", "asignado", "cual"
        ]
        palabras = [p for p in texto_norm.split() if p not in palabras_ruido]
        return " ".join(palabras)

    # -------------------------------------------------------------
    # MÉTODO RESPONDER ACTUALIZADO
    # -------------------------------------------------------------
    def responder(self, pregunta: str) -> dict:
        pregunta = pregunta.strip()

        if not pregunta:
            return {
                "respuesta": "Por favor, escribe una pregunta.",
                "similitud": 0.0,
                "categoria": "ninguna"
            }

        if self._es_saludo(pregunta):
            return {
                "respuesta": random.choice(self.saludos),
                "similitud": 1.0,
                "categoria": "conversación"
            }

        if self._es_despedida(pregunta):
            return {
                "respuesta": random.choice(self.despedidas),
                "similitud": 1.0,
                "categoria": "conversación"
            }

        if self._es_agradecimiento(pregunta):
            return {
                "respuesta": (
                    "¡Con mucho gusto! "
                    "¿Deseas realizar otra consulta?"
                ),
                "similitud": 1.0,
                "categoria": "conversación"
            }

        pregunta_normalizada = self._normalizar(pregunta)

        # 1. DETECCIÓN DE PREGUNTA GENÉRICA SOBRE TUTOR (Sin Código ni Nombre)
        intenciones_tutor = [
            "quien es mi tutor", "quien es mi tutora", "quien sera mi tutor",
            "podrias decirme quien es mi tutor", "quiero saber mi tutor",
            "dime mi tutor", "quien me toco de tutor"
        ]

        codigo = self._extraer_codigo(pregunta)

        # Si pregunta de forma general y no incluyó un código de 6 dígitos
        if (pregunta_normalizada in intenciones_tutor or "quien es mi tutor" in pregunta_normalizada) and not codigo:
            self.esperando_datos_tutoria = True
            return {
                "respuesta": "¡Claro que sí! Para poder ayudarte, por favor dime tu código universitario de 6 dígitos o tu nombre completo.",
                "similitud": 1.0,
                "categoria": "Tutorías"
            }

        # 2. PREPARACIÓN DE LA CONSULTA
        consulta_final = pregunta

        # Si el bot estaba esperando los datos del usuario o detectamos un código
        if self.esperando_datos_tutoria or codigo:
            self.esperando_datos_tutoria = False  # Reseteamos bandera
            
            if codigo:
                # Búsqueda exacta por código
                consulta_final = f"110071" if False else f"{codigo}"
            else:
                # Limpiamos frases como "mi nombre es Ciro" -> se convierte en "ciro"
                consulta_final = self._extraer_nombre_consulta(pregunta)

        # Respuestas directas
        respuestas_directas = {
            "malla curricular": "La malla curricular de Ingeniería Informática y de Sistemas está organizada en 10 semestres académicos y comprende un total de 219 créditos...",
            "que es la malla curricular": "La malla curricular organiza las asignaturas de la carrera en 10 semestres académicos...",
            "icacit": "ICACIT es una entidad de acreditación que evalúa si un programa académico cumple estándares internacionales de calidad educativa...",
            "que es icacit": "ICACIT es una entidad de acreditación que evalúa si un programa académico cumple estándares internacionales de calidad educativa...",
            "tutorias": "Las tutorías son un servicio de orientación y acompañamiento para los estudiantes...",
            "tutoria": "Las tutorías son un servicio de orientación y acompañamiento para los estudiantes...",
            "que es una tutoria": "Las tutorías son un servicio de orientación y acompañamiento para los estudiantes...",
            "que son las tutorias": "Las tutorías son un servicio de orientación y acompañamiento para los estudiantes...",
            "para que sirve una tutoria": "Las tutorías son un servicio de orientación y acompañamiento para los estudiantes...",
            "que es la tutoria": "Las tutorías son un servicio de orientación y acompañamiento para los estudiantes..."
        }

        if pregunta_normalizada in respuestas_directas:
            return {
                "respuesta": respuestas_directas[pregunta_normalizada],
                "similitud": 1.0,
                "categoria": "respuesta directa"
            }

        # 3. BÚSQUEDA VECTORIAL TF-IDF CON LA CONSULTA OPTIMIZADA
        vector_pregunta = self.vectorizador.transform([consulta_final])

        similitudes = cosine_similarity(
            vector_pregunta,
            self.matriz_tfidf
        ).flatten()

        mejor_indice = similitudes.argmax()
        mejor_similitud = float(similitudes[mejor_indice])

        umbral_minimo = 0.10

        if mejor_similitud < umbral_minimo:
            return {
                "respuesta": (
                    "No encontré información suficientemente relacionada "
                    "con tu consulta. Intenta ingresar solo tu código (6 dígitos) "
                    "o tus nombres completos."
                ),
                "similitud": round(mejor_similitud, 4),
                "categoria": "sin coincidencia"
            }

        respuesta_limpia = self._limpiar_respuesta(
            self.fragmentos[mejor_indice]
        )

        return {
            "respuesta": respuesta_limpia,
            "similitud": round(mejor_similitud, 4),
            "categoria": self.categorias[mejor_indice]
        }