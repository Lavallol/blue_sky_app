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
    // SELECTOR CORRECTO PARA TU ADMIN
    // ============================================================
    const SELECTOR_PRODUCTO = "select[id^='id_escandallolinea_set-'][id$='-producto']";

    // ============================================================
    // 1) CAMBIO DE PRODUCTO → AUTOCOMPLETAR PRECIO (BLOQUE NUEVO)
    // ============================================================
    document.addEventListener("change", function (event) {
        const select = event.target;

        if (!select.matches(SELECTOR_PRODUCTO)) return;

        const fila = select.closest("tr");
        const productoId = select.value;
        const precioInput = fila.querySelector("input[id$='-precio_coste']");

        if (!productoId || !precioInput) return;

        fetch(`/escandallo_app/precio-producto/${productoId}/`)
            .then(r => r.json())
            .then(data => {
                const precio = parseFloat(data.precio) || 0;
                precioInput.value = precio.toFixed(4);
                recalcularFila(fila);
            });
    });

    // ============================================================
    // 2) AUTOCOMPLETAR AL CARGAR LÍNEAS EXISTENTES
    // ============================================================
    const selectsProducto = document.querySelectorAll(SELECTOR_PRODUCTO);

    selectsProducto.forEach(function (select) {
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
    // 3) CAMBIO DE CANTIDAD O MERMA → RECÁLCULO
    // ============================================================
    const inputsRecalculo = document.querySelectorAll(
        "input[id^='id_escandallolinea_set-'][id$='-cantidad'], input[id^='id_escandallolinea_set-'][id$='-merma_porcentaje']"
    );

    inputsRecalculo.forEach(function (input) {
        input.addEventListener("input", function () {
            const fila = input.closest("tr");
            recalcularFila(fila);
        });
    });

});
