document.addEventListener("DOMContentLoaded", function () {

    (function ($) {

        // ================================
        //  Inicializar Select2 en una fila
        // ================================
        function inicializarSelect2(row) {
            const selectProducto = row.querySelector('select[id$="-producto"]');
            if (!selectProducto) return;

            // Django ya inicializa Select2 en filas iniciales,
            // pero NO en filas dinámicas → lo hacemos aquí.
            $(selectProducto).select2({
                width: "100%",
                dropdownAutoWidth: true,
            });
        }

        // ==========================================
        //  Autocompletar precio + IVA desde endpoint
        // ==========================================
        function inicializarAutocompletado(row) {
            const selectProducto = row.querySelector('select[id$="-producto"]');
            if (!selectProducto) return;

            selectProducto.addEventListener("change", function () {
                const productoId = this.value;
                if (!productoId) return;

                // ENDPOINT CORRECTO PARA PEDIDO
                const url = `/admin/appcompras/pedidocompra/api/producto/${productoId}/`;

                fetch(url, { credentials: "same-origin" })
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) return;

                        const precioInput = row.querySelector('input[id$="-precio_unitario"]');
                        const ivaInput = row.querySelector('input[id$="-iva"]');

                        if (precioInput) precioInput.value = data.precio;
                        if (ivaInput) ivaInput.value = data.iva;

                        recalcularTotales(row);
                    })
                    .catch(err => console.error("Error cargando producto:", err));
            });
        }

        // ============================
        //  Recalcular subtotal + total
        // ============================
        function recalcularTotales(row) {
            const cantidadInput = row.querySelector('input[id$="-cantidad_pedida"]');
            const precioInput = row.querySelector('input[id$="-precio_unitario"]');
            const ivaInput = row.querySelector('input[id$="-iva"]');

            const subtotalField = row.querySelector('input[id$="-subtotal"]');
            const ivaImporteField = row.querySelector('input[id$="-iva_importe"]');
            const totalField = row.querySelector('input[id$="-total_linea"]');

            const cantidad = parseFloat(cantidadInput?.value || 0);
            const precio = parseFloat(precioInput?.value || 0);
            const iva = parseFloat(ivaInput?.value || 0);

            const subtotal = cantidad * precio;
            const ivaImporte = subtotal * (iva / 100);
            const total = subtotal + ivaImporte;

            if (subtotalField) subtotalField.value = subtotal.toFixed(2);
            if (ivaImporteField) ivaImporteField.value = ivaImporte.toFixed(2);
            if (totalField) totalField.value = total.toFixed(2);
        }

        // ==========================================
        //  Inicializar una fila completa
        // ==========================================
        function inicializarFila(row) {
            inicializarSelect2(row);
            inicializarAutocompletado(row);

            // Recalcular totales cuando cambie cantidad o precio
            ["cantidad_pedida", "precio_unitario", "iva"].forEach(campo => {
                const input = row.querySelector(`input[id$="-${campo}"]`);
                if (input) {
                    input.addEventListener("input", () => recalcularTotales(row));
                }
            });
        }

        // ==========================================
        //  Inicializar todas las filas existentes
        // ==========================================
        function inicializarTodasLasFilas() {
            const filas = document.querySelectorAll("table tbody tr");
            filas.forEach(inicializarFila);
        }

        inicializarTodasLasFilas();

        // ==========================================
        //  Detectar filas nuevas (botón "Añadir línea")
        // ==========================================
        document.body.addEventListener("click", function (e) {
            if (e.target && e.target.closest(".add-row")) {
                setTimeout(inicializarTodasLasFilas, 200);
            }
        });

    })(django.jQuery);

});
