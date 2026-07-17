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
        """
        Si el corpus contiene títulos con ###,
        conserva cada bloque temático completo.
        Si no contiene títulos, divide el texto en fragmentos.
        """

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
        """
        Elimina títulos técnicos, separadores y formato innecesario.
        """

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
        """
        Lee todos los corpus y crea una matriz TF-IDF.
        """

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
            "hola",
            "buenas",
            "buenos dias",
            "buenas tardes",
            "buenas noches",
            "hey",
            "saludos"
        ]

        return self._normalizar(texto) in saludos

    def _es_despedida(self, texto: str) -> bool:
        despedidas = [
            "adios",
            "chau",
            "hasta luego",
            "nos vemos",
            "salir"
        ]

        return self._normalizar(texto) in despedidas

    def _es_agradecimiento(self, texto: str) -> bool:
        agradecimientos = [
            "gracias",
            "muchas gracias",
            "te agradezco",
            "gracias por ayudarme"
        ]

        return self._normalizar(texto) in agradecimientos

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

        respuestas_directas = {
            "malla curricular": (
                "La malla curricular de Ingeniería Informática y de Sistemas "
                "está organizada en 10 semestres académicos y comprende "
                "un total de 219 créditos. Incluye estudios generales, "
                "estudios específicos, estudios de especialidad, actividades "
                "extracurriculares y prácticas preprofesionales."
            ),

            "que es la malla curricular": (
                "La malla curricular organiza las asignaturas de la carrera "
                "en 10 semestres académicos. La carrera tiene un total de "
                "219 créditos e incluye cursos generales, específicos, "
                "electivos, actividades extracurriculares y prácticas "
                "preprofesionales."
            ),

            "icacit": (
                "ICACIT es una entidad de acreditación que evalúa si un "
                "programa académico cumple estándares internacionales de "
                "calidad educativa y mantiene procesos de mejora continua."
            ),

            "que es icacit": (
                "ICACIT es una entidad de acreditación que evalúa si un "
                "programa académico cumple estándares internacionales de "
                "calidad educativa y mantiene procesos de mejora continua."
            ),

            "tutorias": (
                "Las tutorías son un servicio de orientación y acompañamiento "
                "para los estudiantes durante su formación universitaria. "
                "Pueden ser académicas, personales o profesionales."
            ),

            "tutoria": (
                "Las tutorías son un servicio de orientación y acompañamiento "
                "para los estudiantes durante su formación universitaria. "
                "Pueden ser académicas, personales o profesionales."
            ),
            "que es una tutoria": (
                "Las tutorías son un servicio de orientación y acompañamiento "
                "para los estudiantes durante su formación universitaria. "
                "Pueden ser académicas, personales o profesionales."
            ),

            "que son las tutorias": (
                "Las tutorías son un servicio de orientación y acompañamiento "
                "para los estudiantes durante su formación universitaria. "
                "Pueden ser académicas, personales o profesionales."
            ),
            "para que sirve una tutoria": (
                "Las tutorías son un servicio de orientación y acompañamiento "
                "para los estudiantes durante su formación universitaria. "
                "Pueden ser académicas, personales o profesionales."
            ),

            "que es la tutoria": (
                "Las tutorías son un servicio de orientación y acompañamiento "
                "para los estudiantes durante su formación universitaria. "
                "Pueden ser académicas, personales o profesionales."
            )

        }

        if pregunta_normalizada in respuestas_directas:
            return {
                "respuesta": respuestas_directas[pregunta_normalizada],
                "similitud": 1.0,
                "categoria": "respuesta directa"
            }

        vector_pregunta = self.vectorizador.transform(
            [pregunta]
        )

        similitudes = cosine_similarity(
            vector_pregunta,
            self.matriz_tfidf
        ).flatten()

        mejor_indice = similitudes.argmax()
        mejor_similitud = float(
            similitudes[mejor_indice]
        )

        umbral_minimo = 0.10

        if mejor_similitud < umbral_minimo:
            return {
                "respuesta": (
                    "No encontré información suficientemente relacionada "
                    "con tu consulta. Intenta formularla con otras palabras."
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