document.addEventListener("DOMContentLoaded", function () {
    console.log("PEDIDO JS CARGADO");

    // ============================================================
    // 🟩 SELECT2 — ESPERAR A QUE EL ADMIN INICIALICE EL WIDGET
    // ============================================================
    django.jQuery(document).on("django:select2-init", "select.admin-autocomplete", function (e) {

        const selectElem = e.target;

        // Ahora que Select2 está inicializado, enganchamos el evento real
        django.jQuery(selectElem).on("select2:select", function (ev) {

            const productoId = ev.params.data.id;
            console.log("CAMBIO PRODUCTO (SELECT2 ADMIN INIT), ID:", productoId);

            if (!productoId) return;

            const fila = selectElem.closest("tr");
            if (!fila) {
                console.log("No se encontró la fila del inline");
                return;
            }

            const precioInput = fila.querySelector("input[id$='precio_unitario']");
            const ivaInput = fila.querySelector("input[id$='iva']");

            // ⭐ LÍNEA 28 CORREGIDA ⭐
            const data = ev.params.data;

            if (!data) return;

            if (precioInput) precioInput.value = data.precio ?? "";
            if (ivaInput) ivaInput.value = data.iva ?? "";
        });
    });

    // ============================================================
    // 🟩 LISTENER SELECT2 (respaldo)
    // ============================================================
    django.jQuery(document).on('select2:select', "select[id$='producto']", function (e) {
        const productoId = e.params.data.id;
        console.log("CAMBIO PRODUCTO (SELECT2 RESPALDO), ID:", productoId);

        if (!productoId) return;

        const fila = this.closest("tr");
        if (!fila) {
            console.log("No se encontró la fila del inline");
            return;
        }

        const precioInput = fila.querySelector("input[id$='precio_unitario']");
        const ivaInput = fila.querySelector("input[id$='iva']");

        // ⭐ LÍNEA 63 CORREGIDA ⭐
        const data = e.params.data;

        if (!data) return;

        if (precioInput) precioInput.value = data.precio ?? "";
        if (ivaInput) ivaInput.value = data.iva ?? "";
    });

    // ============================================================
    // 🟩 LISTENER ORIGINAL (change) — respaldo adicional
    // ============================================================
    document.addEventListener("change", function (e) {

        if (!e.target.matches("select[id$='producto']")) return;

        const productoSelect = e.target;
        const productoId = productoSelect.value;

        console.log("CAMBIO PRODUCTO (CHANGE), ID:", productoId);

        if (!productoId) return;

        const fila = productoSelect.closest("tr");
        if (!fila) {
            console.log("No se encontró la fila del inline");
            return;
        }

        const precioInput = fila.querySelector("input[id$='precio_unitario']");
        const ivaInput = fila.querySelector("input[id$='iva']");

        // ⭐ LÍNEA 102 CORREGIDA ⭐
        const data = {
            precio: productoSelect.dataset.precio,
            iva: productoSelect.dataset.iva
        };

        if (!data) return;

        if (precioInput) precioInput.value = data.precio ?? "";
        if (ivaInput) ivaInput.value = data.iva ?? "";
    });
});
