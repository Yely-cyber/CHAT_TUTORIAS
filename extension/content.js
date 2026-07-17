// Crear botón

const boton = document.createElement("button");

boton.id = "mi-chatbot";

const imagen = document.createElement("img");

imagen.src = chrome.runtime.getURL("imagenes/chatbot.png");
imagen.alt = "Chatbot";

boton.appendChild(imagen);

document.body.appendChild(boton);

// Evento click

boton.onclick = abrirChat;

const panel = document.createElement("div");

panel.id = "panel-chat";

panel.innerHTML = `
    <iframe
        src="${chrome.runtime.getURL("chatbot.html")}"
        frameborder="0">
    </iframe>
`;

document.body.appendChild(panel);

function abrirChat(){

    panel.classList.add("abierto");

    boton.style.display = "none";

}

function cerrarChat(){

    panel.classList.remove("abierto");

    boton.style.display = "flex";

}

window.addEventListener(
    "message",
    (evento)=>{

        if(evento.data==="cerrarChat"){

            cerrarChat();

        }

    }
);