document.addEventListener("DOMContentLoaded", function () {
    console.log("PEDIDO JS CARGADO — Listener Django 6 activo");

    django.jQuery(document).on("change", "select[data-autocomplete-light-function]", function () {

        const productoId = django.jQuery(this).val();
        console.log("CAMBIO PRODUCTO (ADMIN AUTOCOMPLETE REAL), ID:", productoId);

        if (!productoId) return;

        const fila = this.closest("tr");
        if (!fila) {
            console.log("No se encontró la fila del inline");
            return;
        }

        const precioInput = fila.querySelector("input[id$='precio_unitario']");
        const ivaInput = fila.querySelector("input[id$='iva']");

        fetch(`/appcompras/api/pedidocompra/producto/${productoId}/`, {
            credentials: "same-origin"
        })
            .then(r => r.json())
            .then(data => {
                console.log("DATA API:", data);

                if (!data) return;

                if (precioInput) precioInput.value = data.precio_unitario ?? "";
                if (ivaInput) ivaInput.value = data.iva ?? "";
            })
            .catch(err => console.error("Error:", err));
    });
});
