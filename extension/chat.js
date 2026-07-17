const ventanaChat =
    document.getElementById("ventana-chat");

const formularioChat =
    document.getElementById("formulario-chat");

const entradaUsuario =
    document.getElementById("mensaje-usuario");

const contenedorMensajes =
    document.getElementById("chat-mensajes");

const botonEnviar =
    document.getElementById("boton-enviar");



function usarPregunta(pregunta) {
    entradaUsuario.value = pregunta;
    entradaUsuario.focus();
}


function crearMensaje(
    texto,
    tipo,
    cargando = false
) {
    const fila =
        document.createElement("div");

    fila.classList.add(
        "fila-mensaje"
    );

    const mensaje =
        document.createElement("div");

    mensaje.classList.add(
        "mensaje"
    );

    if (tipo === "bot") {
    mensaje.innerHTML = texto.replace(
        /(https?:\/\/[^\s]+)/g,
        '<a href="$1" target="_blank">$1</a>'
        );
    } else {
    mensaje.textContent = texto;
    }
    if (tipo === "usuario") {
        fila.classList.add(
            "usuario"
        );

        mensaje.classList.add(
            "mensaje-usuario"
        );

        fila.appendChild(
            mensaje
        );
    } else {
        fila.classList.add(
            "bot"
        );

        const avatar =
            document.createElement("div");

        avatar.classList.add(
            "mini-avatar"
        );

        avatar.textContent = "🎓";

        mensaje.classList.add(
            "mensaje-bot"
        );

        if (cargando) {
            mensaje.classList.add(
                "mensaje-cargando"
            );
        }

        fila.appendChild(
            avatar
        );

        fila.appendChild(
            mensaje
        );
    }

    contenedorMensajes.appendChild(
        fila
    );

    contenedorMensajes.scrollTop =
        contenedorMensajes.scrollHeight;

    return fila;
}


async function enviarMensaje(pregunta) {
    crearMensaje(
        pregunta,
        "usuario"
    );

    botonEnviar.disabled = true;
    entradaUsuario.disabled = true;

    const mensajeCargando = crearMensaje(
        "Buscando información...",
        "bot",
        true
    );

    try {
        console.log(
            "Enviando pregunta al servidor:",
            pregunta
        );
        const respuestaServidor = await fetch(
            "http://127.0.0.1:5000/api/chat",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    mensaje: pregunta
                })
            }
        );

        const datos =
            await respuestaServidor.json();

        mensajeCargando.remove();

        if (!respuestaServidor.ok) {
            throw new Error(
                datos.respuesta ||
                "No se pudo procesar la consulta."
            );
        }

        crearMensaje(
    datos.respuesta,
    "bot"
);

        console.log(
            "Similitud:",
            datos.similitud
        );

    } catch (error) {
        mensajeCargando.remove();
        consoloe.error(error);

        crearMensaje(
            error.message,
            "bot"
        );

        console.error(
            error
        );

    } finally {
        botonEnviar.disabled = false;
        entradaUsuario.disabled = false;
        entradaUsuario.focus();
    }
}


formularioChat.addEventListener(
    "submit",
    async function (evento) {
        evento.preventDefault();

        const pregunta =
            entradaUsuario.value.trim();

        if (pregunta === "") {
            return;
        }

        entradaUsuario.value = "";

        await enviarMensaje(
            pregunta
        );
    }
);

const botonCerrar =
    document.getElementById("cerrar-chat");

botonCerrar.addEventListener(
    "click",
    () => {

        window.parent.postMessage(
            "cerrarChat",
            "*"
        );

    }
);

document.querySelectorAll(".pregunta-rapida").forEach((boton) => {

    boton.addEventListener("click", async () => {

        const pregunta = boton.dataset.pregunta;

        entradaUsuario.value = "";

        await enviarMensaje(pregunta);

        entradaUsuario.focus();

    });

});