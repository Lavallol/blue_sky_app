document.addEventListener("DOMContentLoaded", function () {
    console.log("PEDIDO JS CARGADO");

    // ============================================================
    // 🟩 EVENTO REAL DEL ADMIN (AutocompleteSelect)
    // ============================================================
    django.jQuery(document).on('django:autocomplete', ".admin-autocomplete", function (e) {
        const productoId = this.value;
        console.log("CAMBIO PRODUCTO (AUTOCOMPLETE ADMIN), ID:", productoId);

        if (!productoId) return;

        const fila = this.closest("tr");
        if (!fila) {
            console.log("No se encontró la fila del inline");
            return;
        }

        const precioInput = fila.querySelector("input[id$='precio_unitario']");
        const ivaInput = fila.querySelector("input[id$='iva']");

        fetch(`/admin/appcompras/pedidocompra/api/producto/${productoId}/`)
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
    // 🟩 LISTENER SELECT2 (queda como respaldo, no molesta)
    // ============================================================
    $(document).on('select2:select', "select[id$='producto']", function (e) {
        const productoId = e.params.data.id;
        console.log("CAMBIO PRODUCTO (SELECT2), ID:", productoId);

        if (!productoId) return;

        const fila = this.closest("tr");
        if (!fila) {
            console.log("No se encontró la fila del inline");
            return;
        }

        const precioInput = fila.querySelector("input[id$='precio_unitario']");
        const ivaInput = fila.querySelector("input[id$='iva']");

        fetch(`/admin/appcompras/pedidocompra/api/producto/${productoId}/`)
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
    // 🟩 LISTENER ORIGINAL (change) — respaldo adicional
    // ============================================================
    document.addEventListener("change", function (e) {

        if (!e.target.matches("select[id$='producto']")) return;

        const productoSelect = e.target;
        const productoId = productoSelect.value;

        console.log("CAMBIO PRODUCTO, ID:", productoId);

        if (!productoId) return;

        const fila = productoSelect.closest("tr");
        if (!fila) {
            console.log("No se encontró la fila del inline");
            return;
        }

        const precioInput = fila.querySelector("input[id$='precio_unitario']");
        const ivaInput = fila.querySelector("input[id$='iva']");

        fetch(`/admin/appcompras/pedidocompra/api/producto/${productoId}/`)
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
