// ===============================
// SESIÓN DE xCONTEO — MÓDULO LIMPIO
// ===============================

console.log("🔥 ARCHIVO REAL — VERSION 999");

console.log("🔥 SESION.JS CARGADO (ARCHIVO EJECUTADO)");

document.addEventListener("DOMContentLoaded", function () {

    // ===============================
    // ELEMENTOS DOM
    // ===============================
    const inputCodigo = document.getElementById("input-codigo");
    const tablaLineas = document.getElementById("tabla_lineas");
    const sesionId = document.body.dataset.sesionId;

    console.log("DOMCONTENTLOADED OK");
    console.log("inputCodigo =", inputCodigo);
    console.log("tablaLineas =", tablaLineas);
    console.log("sesionId =", sesionId);

    console.log("INPUT EVENT BINDING TEST");

    if (inputCodigo) {
        inputCodigo.addEventListener("input", () => {
            console.log("INPUT REAL:", inputCodigo.value);
        });
    } else {
        console.error("❌ input-codigo NO existe en el DOM");
    }

    // ===============================
    // ESTADO
    // ===============================
    let temporizadorLectura = null;

    // 🔥 NUEVO: anti-duplicados del escáner
    let ultimoCodigo = "";

    // ===============================
    // INICIALIZACIÓN
    // ===============================
    restaurarFoco();
    recalcularTotales();

    // ===============================
    // ESCÁNER — LISTENER UNIFICADO
    // ===============================
    inputCodigo.addEventListener("input", function () {

        clearTimeout(temporizadorLectura);

        const valor = inputCodigo.value.trim();

        temporizadorLectura = setTimeout(() => {

            // 🔴 CÓDIGO DE BARRAS (automático)
            const esCodigoBarras = /^\d{8,13}$/.test(valor);

            if (esCodigoBarras) {

                if (valor === ultimoCodigo) return;
                ultimoCodigo = valor;

                procesarCodigo(valor);
                inputCodigo.value = "";
            }

        }, 150);
    });

    inputCodigo.addEventListener("keydown", function (e) {

        if (e.key !== "Enter") return;

        const valor = inputCodigo.value.trim();
        if (!valor) return;

        if (valor === ultimoCodigo) return;
        ultimoCodigo = valor;

        procesarCodigo(valor);
        inputCodigo.value = "";

        e.preventDefault();
    });

    // ===============================
    // FOCO
    // ===============================
    function restaurarFoco() {
        setTimeout(() => inputCodigo.focus(), 80);
    }

    // ===============================
    // PROCESAR CÓDIGO
    // ===============================
    function procesarCodigo(codigo) {
        console.log("👉 CODIGO ENVIADO:", codigo);

        fetch(`/conteo/api/buscar_producto/?query=${encodeURIComponent(codigo)}`)
            .then(r => r.json())
            .then(data => {

                console.log("👉 RESPUESTA API:", data);

                if (data.error) {
                    alert(data.error);
                    limpiarInput();
                    restaurarFoco();
                    return;
                }

                if (data.id) {
                    manejarProductoEncontrado(codigo, data.id);
                }

                limpiarInput();

                if (!buscarFilaPorCodigo(codigo)) {
                    restaurarFoco();
                }

            })
            .catch(err => {
                console.error("Error en búsqueda:", err);
                limpiarInput();
                restaurarFoco();
            });
    }

    // ===============================
    // MANEJO DE PRODUCTO (VERSIÓN ESTABLE)
    // ===============================
    function manejarProductoEncontrado(codigo, productoId) {

        const filaExistente = buscarFilaPorCodigo(codigo);

        if (filaExistente) {

            const input = filaExistente.querySelector(".input-stock-contado");

            limpiarInput();

            setTimeout(() => {
                if (input) {
                    input.focus();
                    input.select();
                } else {
                    restaurarFoco();
                }
            }, 10);

            return;
        }

        crearLinea(productoId);
    }

    function buscarFilaPorCodigo(codigo) {
        const filas = tablaLineas.querySelectorAll("tr");

        for (let tr of filas) {
            const celdas = tr.querySelectorAll("td");
            if (celdas.length < 2) continue;

            const codBarras = (celdas[0].textContent || "").trim();
            const codInterno = (celdas[1].textContent || "").trim();

            if (codBarras === codigo || codInterno === codigo) {
                return tr;
            }
        }

        return null;
    }

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

            if (nuevaFila) {

                document.activeElement?.blur();

                tablaLineas.insertAdjacentElement("beforeend", nuevaFila);

                recalcularTotales();
            }

            limpiarInput();

            setTimeout(() => {
                const input = document.getElementById("input-codigo");
                if (input) {
                    input.focus();
                    input.select();
                }
            }, 0);

        })
        .catch(err => {
            console.error("Error al agregar línea:", err);
            limpiarInput();

            setTimeout(() => {
                const input = document.getElementById("input-codigo");
                if (input) {
                    input.focus();
                    input.select();
                }
            }, 0);
        });
    }

    // 🧹 limpiar input de escaneo
    limpiarInput();

    // ===============================
    // ACTUALIZACIONES DINÁMICAS
    // ===============================

    // ✔ CORRECTO: actualizar solo cuando el usuario pulse ENTER
    document.addEventListener("keydown", function (e) {
        if (e.target.classList.contains("input-stock-contado") && e.key === "Enter") {
            actualizarLinea(e.target.dataset.lineaId);
        }
    });

    // Motivo: se actualiza al cambiar el campo
    document.addEventListener("change", function (e) {
        if (e.target.classList.contains("input-motivo")) {
            actualizarLinea(e.target.dataset.lineaId);
        }
    });

    // Eliminar línea
    document.addEventListener("click", function (e) {
        if (e.target.classList.contains("btn-eliminar-linea")) {

            const lineaId = e.target.dataset.lineaId;
            if (!lineaId) return;

            if (!confirm("¿Eliminar esta línea de conteo?")) return;

            fetch("/conteo/api/eliminar_linea/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": obtenerCSRF()
                },
                body: JSON.stringify({ linea_id: lineaId })
            })
            .then(r => r.json())
            .then(data => {

                if (data.error) {
                    alert(data.error);
                    return;
                }

                const fila = document.querySelector(`tr[data-linea-id="${lineaId}"]`);
                if (fila) fila.remove();

                recalcularTotales();
                restaurarFoco();
            })
            .catch(err => console.error(err));
        }
    });

    // ===============================
    // API UPDATE (CORREGIDO)
    // ===============================
    function actualizarLinea(lineaId) {

        const stock = obtenerStockContado(lineaId);
        const motivo = obtenerMotivo(lineaId);

        fetch("/conteo/api/actualizar_linea/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": obtenerCSRF()
            },
            body: JSON.stringify({
                linea_id: lineaId,
                stock_contado: stock,
                motivo: motivo
            })
        })
        .then(r => r.json())
        .then(data => {

            if (data.error) {
                alert(data.error);
                return;
            }

            // ===============================
            // ACTUALIZAR CELDAS DE LA FILA
            // ===============================
            const fila = document.querySelector(`tr[data-linea-id="${lineaId}"]`);

            if (fila) {
                fila.querySelector(".importe-contado").textContent = Number(data.importe_contado).toFixed(2);
                fila.querySelector(".diferencia").textContent = data.diferencia;
                fila.querySelector(".importe-aumenta").textContent = Number(data.importe_aumenta).toFixed(2);
                fila.querySelector(".importe-disminuye").textContent = Number(data.importe_disminuye).toFixed(2);
            }

            recalcularTotales();

            setTimeout(() => {
                const input = document.getElementById("input-codigo");
                if (input) input.focus();
            }, 50);

        })
        .catch(err => console.error(err));
    }

    // ===============================
    // TOTALES
    // ===============================
    function recalcularTotales() {

        let totalContado = 0;
        let totalAumenta = 0;
        let totalDisminuye = 0;

        document.querySelectorAll("td.importe-contado").forEach(td => {
            totalContado += parseFloat(td.textContent) || 0;
        });

        document.querySelectorAll("td.importe-aumenta").forEach(td => {
            totalAumenta += parseFloat(td.textContent) || 0;
        });

        document.querySelectorAll("td.importe-disminuye").forEach(td => {
            totalDisminuye += parseFloat(td.textContent) || 0;
        });

        const elContado = document.getElementById("total-contado");
        const elAumenta = document.getElementById("total-aumenta");
        const elDisminuye = document.getElementById("total-disminuye");

        if (elContado) elContado.textContent = totalContado.toFixed(2);
        if (elAumenta) elAumenta.textContent = totalAumenta.toFixed(2);
        if (elDisminuye) elDisminuye.textContent = totalDisminuye.toFixed(2);
    }

    // ===============================
    // HELPERS
    // ===============================
    function limpiarInput() {
        inputCodigo.value = "";
    }

    // 🟩 CORREGIDO: AHORA FUNCIONA SIEMPRE
    function obtenerStockContado(lineaId) {
        const input = document.querySelector(`input[data-linea-id="${lineaId}"]`);
        return input ? input.value : "0";
    }

    function obtenerMotivo(lineaId) {
        const input = document.querySelector(`input.input-motivo[data-linea-id="${lineaId}"]`);
        return input ? input.value : "";
    }

    function obtenerCSRF() {
        return document.cookie
            .split(";")
            .find(c => c.trim().startsWith("csrftoken="))
            ?.split("=")[1] || "";
    }
});
