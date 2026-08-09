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

            fetch(`/appcompras/pedidocompra/api/producto/${productoId}/`)
                .then(response => {
                    console.log("RESPUESTA API STATUS:", response.status);
                    return response.json();
                })
                .then(data => {
                    console.log("DATA API:", data);

                    if (!data) return;

                    if (precioInput) precioInput.value = data.precio ?? "";
                    if (ivaInput) ivaInput.value = data.iva ?? "";
                })
                .catch(error => console.error("Error:", error));
        });
    });

    // ============================================================
    // 🟩 LISTENER SELECT2 (respaldo)
    // ============================================================
    django.jQuery(document).on('select2:select', "select[name$='producto']", function (e) {

        const productoId = e.params.data.id;
        console.log("CAMBIO PRODUCTO (SELECT2 RESPALDO), ID:", productoId);

        if (!productoId) return;

        const fila = django.jQuery(this)[0].closest("tr");
        if (!fila) {
            console.log("No se encontró la fila del inline");
            return;
        }

        const precioInput = fila.querySelector("input[id$='precio_unitario']");
        const ivaInput = fila.querySelector("input[id$='iva']");

        fetch(`/appcompras/pedidocompra/api/producto/${productoId}/`)
            .then(response => {
                console.log("RESPUESTA API STATUS:", response.status);
                return response.json();
            })
            .then(data => {
                console.log("DATA API:", data);

                if (!data) return;

                if (precioInput) precioInput.value = data.precio ?? "";
                if (ivaInput) ivaInput.value = data.iva ?? "";
            })
            .catch(error => console.error("Error:", error));
    });

    // ============================================================
    // 🟩 LISTENER SELECT2 INVISIBLE — solución definitiva
    // ============================================================
    django.jQuery(document).on("change", ".select2-hidden-accessible", function () {

        const productoId = django.jQuery(this).val();
        console.log("CAMBIO PRODUCTO (INVISIBLE SELECT2), ID:", productoId);

        if (!productoId) return;

        const fila = this.closest("tr");
        if (!fila) return;

        const precioInput = fila.querySelector("input[id$='precio_unitario']");
        const ivaInput = fila.querySelector("input[id$='iva']");

        fetch(`/appcompras/pedidocompra/api/producto/${productoId}/`)
            .then(r => r.json())
            .then(data => {
                if (precioInput) precioInput.value = data.precio ?? "";
                if (ivaInput) ivaInput.value = data.iva ?? "";
            })
            .catch(err => console.error("Error:", err));
    });

    // ============================================================
    // 🟩 LISTENER ORIGINAL (change) — respaldo adicional
    // ============================================================
    document.addEventListener("change", function (e) {

        if (!e.target.matches("select[name$='producto']")) return;

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

        fetch(`/appcompras/pedidocompra/api/producto/${productoId}/`)
            .then(response => {
                console.log("RESPUESTA API STATUS:", response.status);
                return response.json();
            })
            .then(data => {
                console.log("DATA API:", data);

                if (!data) return;

                if (precioInput) precioInput.value = data.precio ?? "";
                if (ivaInput) ivaInput.value = data.iva ?? "";
            })
            .catch(error => console.error("Error:", error));
    });
});
