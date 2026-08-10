document.addEventListener("DOMContentLoaded", function () {

    const autocompletes = document.querySelectorAll('.admin-autocomplete');

    autocompletes.forEach(function (ac) {

        ac.addEventListener('select2:select', function (e) {

            const codigo = e.params.data.text;   // Select2 devuelve el código en .text
            if (!codigo) return;

            fetch(`/inventario/buscar_producto_por_codigo?codigo=${codigo}`)
                .then(response => response.json())
                .then(data => {

                    if (!data.ok) return;

                    const row = ac.closest('.form-row');
                    if (!row) return;

                    const precioInput = row.querySelector('input[name$="precio_unitario"]');
                    if (!precioInput) return;

                    // Rellenar precio unitario
                    precioInput.value = data.precio_coste;

                    // Recalcular total si ya hay cantidad
                    const cantidadInput = row.querySelector('input[name$="cantidad_pedida"]');
                    const totalInput = row.querySelector('input[name$="total_linea"]');

                    if (cantidadInput && totalInput) {
                        const cantidad = parseFloat(cantidadInput.value || "0");
                        const precio = parseFloat(data.precio_coste || "0");
                        totalInput.value = (cantidad * precio).toFixed(2);
                    }
                });
        });
    });

    // Escuchar cambios en Cantidad Pedida
    document.addEventListener("input", function (e) {

        if (!e.target.name || !e.target.name.endsWith("cantidad_pedida")) return;

        const row = e.target.closest('.form-row');
        if (!row) return;

        const precioInput = row.querySelector('input[name$="precio_unitario"]');
        const totalInput = row.querySelector('input[name$="total_linea"]');

        if (!precioInput || !totalInput) return;

        const cantidad = parseFloat(e.target.value || "0");
        const precio = parseFloat(precioInput.value || "0");

        totalInput.value = (cantidad * precio).toFixed(2);
    });
});
