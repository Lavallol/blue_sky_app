document.addEventListener("django-admin:init", function (e) {

    const selectElem = e.target;

    if (!selectElem.matches("select.admin-autocomplete")) return;

    django.jQuery(selectElem).on("select2:select", function (ev) {

        const productoId = ev.params.data.id;
        if (!productoId) return;

        const fila = selectElem.closest("tr");
        if (!fila) return;

        const precioInput = fila.querySelector('input[name$="precio_unitario"]');
        const ivaInput = fila.querySelector('input[name$="iva"]');

        fetch(`/admin/appcompras/pedidocompra/api/producto/${productoId}/`)
            .then(response => response.json())
            .then(data => {

                if (precioInput) precioInput.value = data.precio ?? "";
                if (ivaInput) ivaInput.value = data.iva ?? "";

                // Recalcular total si ya hay cantidad
                const cantidadInput = fila.querySelector('input[name$="cantidad_pedida"]');
                const totalInput = fila.querySelector('input[name$="total_linea"]');

                if (cantidadInput && totalInput) {
                    const cantidad = parseFloat(cantidadInput.value || "0");
                    const precio = parseFloat(precioInput.value || "0");
                    totalInput.value = (cantidad * precio).toFixed(2);
                }
            });
    });
});


// Recalcular total cuando cambia la cantidad
document.addEventListener("input", function (e) {

    if (!e.target.name || !e.target.name.endsWith("cantidad_pedida")) return;

    const fila = e.target.closest("tr");
    if (!fila) return;

    const precioInput = fila.querySelector('input[name$="precio_unitario"]');
    const totalInput = fila.querySelector('input[name$="total_linea"]');

    if (!precioInput || !totalInput) return;

    const cantidad = parseFloat(e.target.value || "0");
    const precio = parseFloat(precioInput.value || "0");

    totalInput.value = (cantidad * precio).toFixed(2);
});

document.addEventListener("DOMContentLoaded", function () {

    const selects = document.querySelectorAll("select.admin-autocomplete");

    selects.forEach(function (selectElem) {

        const jq = django.jQuery(selectElem);

        jq.on("select2:select", function (ev) {

            const productoId = ev.params.data.id;
            if (!productoId) return;

            const fila = selectElem.closest("tr");
            if (!fila) return;

            const precioInput = fila.querySelector('input[name$="precio_unitario"]');
            const ivaInput = fila.querySelector('input[name$="iva"]');

            fetch(`/admin/appcompras/pedidocompra/api/producto/${productoId}/`)
                .then(response => response.json())
                .then(data => {

                    if (precioInput) precioInput.value = data.precio ?? "";
                    if (ivaInput) ivaInput.value = data.iva ?? "";

                    const cantidadInput = fila.querySelector('input[name$="cantidad_pedida"]');
                    const totalInput = fila.querySelector('input[name$="total_linea"]');

                    if (cantidadInput && totalInput) {
                        const cantidad = parseFloat(cantidadInput.value || "0");
                        const precio = parseFloat(precioInput.value || "0");
                        totalInput.value = (cantidad * precio).toFixed(2);
                    }
                });
        });
    });
});
