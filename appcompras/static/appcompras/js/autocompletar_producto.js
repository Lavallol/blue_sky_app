/* ============================================================
   AUTOCOMPLETAR PRODUCTO EN TODAS LAS FILAS DEL INLINE
   - Funciona en filas iniciales
   - Funciona en filas nuevas (formset:added)
   ============================================================ */

/* 🟩 1. Listener para filas iniciales (las dos primeras) */
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

/* ============================================================
   🟩 2. Listener para filas nuevas creadas dinámicamente
   Django Admin dispara "formset:added" cuando se agrega una fila
   ============================================================ */

document.addEventListener('formset:added', function(e) {
    const row = e.target;

    const select = row.querySelector('.select2-hidden-accessible');
    if (!select) return;

    select.addEventListener('change', function() {

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
    });
});

document.addEventListener("click", function(e) {
    if (e.target && e.target.closest(".add-row")) {

        setTimeout(function() {

            const filas = document.querySelectorAll(".dynamic-pedidocompralinea_set");

            filas.forEach(function(row) {

                const select = row.querySelector(".select2-hidden-accessible");

                if (!select) return;

                if (select.dataset.listenerAttached === "1") return;
                select.dataset.listenerAttached = "1";

                select.addEventListener("change", function() {

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
                });
            });

        }, 150);
    }
});

document.addEventListener('DOMNodeInserted', function(e) {

    if (e.target && e.target.classList && e.target.classList.contains('select2-container')) {

        const select = e.target.previousElementSibling;

        if (!select || !select.classList.contains('select2-hidden-accessible')) return;

        const row = select.closest('.dynamic-pedidocompralinea_set');
        if (!row) return;

        if (select.dataset.listenerAttached === "1") return;
        select.dataset.listenerAttached = "1";

        select.addEventListener('change', function() {

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
        });
    }
});
