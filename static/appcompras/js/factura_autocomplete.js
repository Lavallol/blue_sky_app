document.addEventListener("DOMContentLoaded", function () {
    console.log("FACTURA JS CARGADO");

    // ---------------------------------------------------------
    // Recalcular línea cuando cambian cantidad, precio o descuento
    // ---------------------------------------------------------
    function recalcularLinea(inline, ivaPorcentaje) {
        const cantidadInput = inline.querySelector("input[id$='cantidad']");
        const precioInput = inline.querySelector("input[id$='precio_unitario']");
        const descuentoInput = inline.querySelector("input[id$='importe_descuento']");
        const impuestosInput = inline.querySelector("input[id$='importe_impuestos']");
        const totalInput = inline.querySelector("input[id$='total']");

        if (!cantidadInput || !precioInput || !impuestosInput || !totalInput) return;

        const cantidad = parseFloat(cantidadInput.value || "0");
        const precio = parseFloat(precioInput.value || "0");
        const descuento = parseFloat(descuentoInput ? (descuentoInput.value || "0") : "0");

        const base = (cantidad * precio) - descuento;
        const impuestos = base * (ivaPorcentaje / 100);
        const total = base + impuestos;

        impuestosInput.value = impuestos.toFixed(2);
        totalInput.value = total.toFixed(2);
    }

    // ---------------------------------------------------------
    // Detectar todos los inlines de líneas de factura
    // ---------------------------------------------------------
    const inlines = document.querySelectorAll("tr.form-row");

    inlines.forEach(inline => {
        const productoSelect = inline.querySelector("select[id$='producto']");
        const precioInput = inline.querySelector("input[id$='precio_unitario']");
        const cantidadInput = inline.querySelector("input[id$='cantidad']");
        const descuentoInput = inline.querySelector("input[id$='importe_descuento']");

        if (!productoSelect) return;

        // ---------------------------------------------------------
        // Cuando cambia el producto → traer precio e IVA
        // ---------------------------------------------------------
        productoSelect.addEventListener("change", function () {
            const productoId = this.value;
            if (!productoId) return;

            fetch(`/appcompras/api/producto/${productoId}/`)
                .then(r => r.json())
                .then(data => {
                    const ivaPorcentaje = data.iva ?? 0;

                    if (precioInput) precioInput.value = data.precio ?? "";

                    recalcularLinea(inline, ivaPorcentaje);
                })
                .catch(error => console.error("Error FACTURA:", error));
        });

        // ---------------------------------------------------------
        // Recalcular cuando cambian cantidad, precio o descuento
        // ---------------------------------------------------------
        [cantidadInput, precioInput, descuentoInput].forEach(input => {
            if (!input) return;
            input.addEventListener("input", function () {
                const productoId = productoSelect.value;
                if (!productoId) return;

                fetch(`/appcompras/api/producto/${productoId}/`)
                    .then(r => r.json())
                    .then(data => {
                        const ivaPorcentaje = data.iva ?? 0;
                        recalcularLinea(inline, ivaPorcentaje);
                    })
                    .catch(error => console.error("Error FACTURA:", error));
            });
        });
    });
});
