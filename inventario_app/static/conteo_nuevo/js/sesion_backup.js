// ===============================
// SESIÓN DE CONTEO — JS RESTAURADO + ESCANEO SIN ENTER
// ===============================

document.addEventListener("DOMContentLoaded", function () {

    const inputCodigo = document.getElementById("input-codigo");
    const tablaLineas = document.getElementById("tabla_lineas");
    const sesionId = document.body.dataset.sesionId;

    if (!inputCodigo) return;

    // ===============================
    // CONTROL DE ESCRITURA RÁPIDA (evita el error “101”)
    // AHORA ADAPTADO PARA FUNCIONAR SIN ENTER
    // ===============================
    let bloqueo = false;
    let debounceTimer = null;

    // Evita que Enter envíe formularios o recargue
    inputCodigo.addEventListener("keydown", function (e) {
        if (e.key === "Enter") e.preventDefault();
    });

    // PROCESO AUTOMÁTICO SIN ENTER
    inputCodigo.addEventListener("input", function () {
        if (bloqueo) return;

        clearTimeout(debounceTimer);

        bloqueo = true;
        debounceTimer = setTimeout(() => {
            bloqueo = false;

            const codigo = inputCodigo.value.trim();
            if (codigo !== "") {
                procesarCodigo(codigo);
                inputCodigo.value = "";
            }

        }, 180); // tiempo ideal para lectores de códigos
    });

    // ===============================
    // PROCESAR CÓDIGO
    // ===============================
    function procesarCodigo(codigo) {
        if (codigo === "") return;

        fetch(`/conteo/api/buscar_producto/?query=${encodeURIComponent(codigo)}`)
            .then(r => r.json())
            .then(data => {

                if (data.error) {
                    alert(data.error);
                    return;
                }

                agregarLinea(data.id);

                inputCodigo.value = "";
                inputCodigo.focus();
            })
            .catch(err => console.error("Error en búsqueda:", err));
    }

    // ===============================
    // AGREGAR LÍNEA
    // ===============================
function crearLinea(productoId) {
    fetch("/conteo/api/agregar_linea/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": obtenerCSRF()
        },
        body: JSON.stringify({
            sesion_id: sesionId,
            producto_id: productoId
        })
    })
        .then(r => r.text())
        .then(html => {
            const temp = document.createElement("tbody");
            temp.innerHTML = html.trim();
            const nuevaFila = temp.querySelector("tr");

            if (!nuevaFila) {
                limpiarInput();
                restaurarFoco();
                return;
            }

            const idProducto = nuevaFila.getAttribute("data-producto-id");
            const existente = tablaLineas.querySelector(`tr[data-producto-id="${idProducto}"]`);

            if (existente) {
                existente.replaceWith(nuevaFila);
            } else {
                tablaLineas.insertAdjacentElement("beforeend", nuevaFila);
            }

            recalcularTotales();
            limpiarInput();
            restaurarFoco();
        })
        .catch(err => {
            console.error("Error al agregar línea:", err);
            limpiarInput();
            restaurarFoco();
        });
}

        fetch("/conteo/api/agregar_linea/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": obtenerCSRF()
            },
            body: JSON.stringify({
                sesion_id: sesionId,
                producto_id: productoId
            })
        })
            .then(r => r.text())
            .then(html => {

                tablaLineas.insertAdjacentHTML("beforeend", html);

                const filas = tablaLineas.querySelectorAll("tr");
                const ultima = filas[filas.length - 1];

                const inputStock = ultima.querySelector(".input-stock-contado");

                if (inputStock) {
                    inputStock.focus();
                    inputStock.select();
                }
            })
            .catch(err => console.error("Error al agregar línea:", err));
    }

    // ===============================
    // ACTUALIZAR STOCK CONTADO
    // ===============================
    document.addEventListener("input", function (e) {
        if (e.target.classList.contains("input-stock-contado")) {
            const lineaId = e.target.dataset.lineaId;

            actualizarLinea(lineaId, {
                stock_contado: e.target.value,
                motivo: obtenerMotivo(lineaId)
            });
        }
    });

    // ===============================
    // ACTUALIZAR MOTIVO
    // ===============================
    document.addEventListener("change", function (e) {
        if (e.target.classList.contains("input-motivo")) {
            const lineaId = e.target.dataset.lineaId;

            actualizarLinea(lineaId, {
                stock_contado: obtenerStockContado(lineaId),
                motivo: e.target.value
            });
        }
    });

    // ===============================
    // FUNCIONES AUXILIARES
    // ===============================
    function obtenerStockContado(lineaId) {
        return document.querySelector(
            `input.input-stock-contado[data-linea-id="${lineaId}"]`
        ).value;
    }

    function obtenerMotivo(lineaId) {
        const input = document.querySelector(
            `input.input-motivo[data-linea-id="${lineaId}"]`
        );
        return input ? input.value : "";
    }

    // ===============================
    // ACTUALIZAR LÍNEA (AJAX)
    // ===============================
    function actualizarLinea(lineaId, data) {

        fetch("/conteo/api/actualizar_linea/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": obtenerCSRF()
            },
            body: JSON.stringify({
                linea_id: lineaId,
                stock_contado: data.stock_contado,
                motivo: data.motivo
            })
        })
            .then(r => r.json())
            .then(data => {

                if (data.error) {
                    alert(data.error);
                    return;
                }

                document.querySelector(
                    `td.importe-contado[data-linea-id="${lineaId}"]`
                ).textContent = Number(data.importe_contado).toFixed(2);

                const celdaDif = document.querySelector(
                    `td.diferencia[data-linea-id="${lineaId}"]`
                );
                celdaDif.textContent = Number(data.diferencia).toFixed(2);

                if (data.diferencia > 0) celdaDif.style.color = "green";
                else if (data.diferencia < 0) celdaDif.style.color = "red";
                else celdaDif.style.color = "#333";

                document.querySelector(
                    `td.importe-aumenta[data-linea-id="${lineaId}"]`
                ).textContent = Number(data.importe_aumenta).toFixed(2);

                document.querySelector(
                    `td.importe-disminuye[data-linea-id="${lineaId}"]`
                ).textContent = Number(data.importe_disminuye).toFixed(2);

            })
            .catch(err => console.error("Error al actualizar línea:", err));
    }

    // ===============================
    // CSRF
    // ===============================
    function obtenerCSRF() {
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split("=");

            if (name === "csrftoken") {
                return value;
            }
        }
        return "";
    }

});
