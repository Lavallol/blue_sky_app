window.addEventListener("load", function () {

    // ============================================================
    // FUNCIÓN GENERAL DE RECÁLCULO
    // ============================================================
    function recalcularFila(fila) {
        const cantidadInput = fila.querySelector("input[id$='-cantidad']");
        const mermaInput = fila.querySelector("input[id$='-merma_porcentaje']");
        const precioInput = fila.querySelector("input[id$='-precio_coste']");

        const cantidadNetaCell = fila.querySelector(".field-cantidad_neta p");
        const costeTeoricoCell = fila.querySelector(".field-coste_teorico p");
        const costeRealCell = fila.querySelector(".field-coste_real p");

        const cantidad = parseFloat(cantidadInput?.value) || 0;
        const merma = parseFloat(mermaInput?.value) || 0;
        const precio = parseFloat(precioInput?.value) || 0;

        const cantidadNeta = cantidad * (1 - merma / 100);
        const costeTeorico = cantidad * precio;
        const costeReal = cantidadNeta * precio;

        if (cantidadNetaCell) cantidadNetaCell.textContent = cantidadNeta.toFixed(3);
        if (costeTeoricoCell) costeTeoricoCell.textContent = costeTeorico.toFixed(4);
        if (costeRealCell) costeRealCell.textContent = costeReal.toFixed(4);
    }

    // ============================================================
    // SELECTOR CORRECTO PARA TU ADMIN  (PARCHE APLICADO)
    // ============================================================
    const SELECTOR_PRODUCTO = "select[id*='-producto']";

    // ============================================================
    // FUNCIÓN PARA ACTIVAR EVENTOS EN UNA FILA
    // ============================================================
    function activarEventosEnFila(fila) {
        const selectProducto = fila.querySelector(SELECTOR_PRODUCTO);
        const precioInput = fila.querySelector("input[id$='-precio_coste']");
        const cantidadInput = fila.querySelector("input[id$='-cantidad']");
        const mermaInput = fila.querySelector("input[id$='-merma_porcentaje']");

        if (selectProducto) {
            selectProducto.addEventListener("change", function () {
                const productoId = selectProducto.value;
                if (!productoId) return;

                fetch(`/escandallo_app/precio-producto/${productoId}/`)
                    .then(r => r.json())
                    .then(data => {
                        const precio = parseFloat(data.precio) || 0;
                        precioInput.value = precio.toFixed(4);
                        recalcularFila(fila);
                    });
            });
        }

        if (cantidadInput) {
            cantidadInput.addEventListener("input", function () {
                recalcularFila(fila);
            });
        }

        if (mermaInput) {
            mermaInput.addEventListener("input", function () {
                recalcularFila(fila);
            });
        }
    }

    // ============================================================
    // 1) ACTIVAR EVENTOS EN TODAS LAS FILAS EXISTENTES
    // ============================================================
    document.querySelectorAll("tr.form-row").forEach(function (fila) {
        activarEventosEnFila(fila);
    });

    // ============================================================
    // 2) AUTOCOMPLETAR AL CARGAR LÍNEAS EXISTENTES
    // ============================================================
    document.querySelectorAll(SELECTOR_PRODUCTO).forEach(function (select) {
        const fila = select.closest("tr");
        const precioInput = fila.querySelector("input[id$='-precio_coste']");
        const productoId = select.value;

        if (!productoId) return;
        if (precioInput && precioInput.value && parseFloat(precioInput.value) > 0) return;

        fetch(`/escandallo_app/precio-producto/${productoId}/`)
            .then(r => r.json())
            .then(data => {
                const precio = parseFloat(data.precio) || 0;
                precioInput.value = precio.toFixed(4);
                recalcularFila(fila);
            });
    });

    // ============================================================
    // 3) NUEVAS FILAS AÑADIDAS DINÁMICAMENTE (CLAVE)
    // ============================================================
    document.body.addEventListener("formset:added", function (event) {
        const filaNueva = event.target;
        activarEventosEnFila(filaNueva);
    });

});
