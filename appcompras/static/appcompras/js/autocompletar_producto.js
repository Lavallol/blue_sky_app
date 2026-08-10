document.addEventListener('change', function(e) {
    if (e.target && e.target.classList.contains('select2-hidden-accessible')) {

        const select = e.target;
        const row = select.closest('.dynamic-pedidocompralinea_set');

        const productoId = select.value;

        if (!productoId) return;

        fetch(`/admin/appcompras/pedidocompra/api/producto/${productoId}/`)
            .then(response => response.json())
            .then(data => {

                const precioInput = row.querySelector('input[name$="precio_unitario"]');
                const ivaInput = row.querySelector('input[name$="iva"]');
                const totalInput = row.querySelector('input[name$="total"]');

                if (precioInput) precioInput.value = data.precio;
                if (ivaInput) ivaInput.value = data.iva;

                const cantidadInput = row.querySelector('input[name$="cantidad"]');
                if (cantidadInput && totalInput) {
                    const cantidad = parseFloat(cantidadInput.value || 0);
                    totalInput.value = (cantidad * data.precio).toFixed(2);
                }
            });
    }
});
