document.addEventListener("DOMContentLoaded", function () {
    console.log("PEDIDO JS CARGADO");

    // ============================================================
    // 🟩 LISTENER ESPECIAL PARA SELECT2 (evento real del widget)
    // ============================================================
    $(document).on('select2:select', "select[id$='producto']", function (e) {
        const productoId = e.params.data.id;
        console.log("CAMBIO PRODUCTO (SELECT2), ID:", productoId);

        if (!productoId) return;

        // Encontrar la fila del inline
        const fila = this.closest("tr");
        if (!fila) {
            console.log("No se encontró la fila del inline");
            return;
        }

        // Inputs dentro de la fila
        const precioInput = fila.querySelector("input[id$='precio_unitario']");
        const ivaInput = fila.querySelector("input[id$='iva']");

        // Llamada al endpoint
        fetch(`/admin/appcompras/pedidocompra/api/producto/${productoId}/`)
            .then(response => {
                console.log("RESPUESTA API STATUS:", response.status);
                return response.json();
            })
            .then(data => {
                console.log("DATA API:", data);

                if (!data) return;

                // Autocompletar PRECIO
                if (precioInput) precioInput.value = data.precio ?? "";

                // Autocompletar IVA
                if (ivaInput) ivaInput.value = data.iva ?? "";
            })
            .catch(error => console.error("Error:", error));
    });

    // ============================================================
    // 🟩 LISTENER ORIGINAL (change) — sigue funcionando como respaldo
    // ============================================================
    document.addEventListener("change", function (e) {

        // Solo reaccionamos a selects cuyo ID termina en "producto"
        if (!e.target.matches("select[id$='producto']")) return;

        const productoSelect = e.target;
        const productoId = productoSelect.value;

        console.log("CAMBIO PRODUCTO, ID:", productoId);

        if (!productoId) return;

        // Encontrar la fila del inline (TabularInline)
        const fila = productoSelect.closest("tr");
        if (!fila) {
            console.log("No se encontró la fila del inline");
            return;
        }

        // Inputs dentro de la fila
        const precioInput = fila.querySelector("input[id$='precio_unitario']");
        const ivaInput = fila.querySelector("input[id$='iva']");

        // Llamada al endpoint CORREGIDA
        fetch(`/admin/appcompras/pedidocompra/api/producto/${productoId}/`)
            .then(response => {
                console.log("RESPUESTA API STATUS:", response.status);
                return response.json();
            })
            .then(data => {
                console.log("DATA API:", data);

                if (!data) return;

                // Autocompletar PRECIO
                if (precioInput) precioInput.value = data.precio ?? "";

                // Autocompletar IVA
                if (ivaInput) ivaInput.value = data.iva ?? "";
            })
            .catch(error => console.error("Error:", error));
    });
});
