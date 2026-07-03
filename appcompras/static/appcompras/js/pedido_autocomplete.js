document.addEventListener("DOMContentLoaded", function () {
    console.log("PEDIDO JS CARGADO");

    const inlines = document.querySelectorAll("tr.form-row");
    console.log("FILAS ENCONTRADAS:", inlines.length);

    inlines.forEach(inline => {
        const productoSelect = inline.querySelector("select[id$='producto']");
        const precioInput = inline.querySelector("input[id$='precio_unitario']");
        // Dejamos de tocar el IVA desde JS para evitar que desaparezca
        // const ivaInput = inline.querySelector("input[id$='iva']");

        if (!productoSelect) return;

        productoSelect.addEventListener("change", function () {
            console.log("CAMBIO PRODUCTO, ID:", this.value);

            const productoId = this.value;
            if (!productoId) return;

            fetch(`/appcompras/api/producto/${productoId}/`)
                .then(response => {
                    console.log("RESPUESTA API STATUS:", response.status);
                    return response.json();
                })
                .then(data => {
                    console.log("DATA API:", data);

                    if (!data) return;

                    // ✔ Autocompletamos solo el PRECIO
                    if (precioInput) precioInput.value = data.precio ?? "";

                    // ❌ No tocamos el IVA aquí
                    // Django Admin lo borra después del cambio
                    // y tu modelo ya lo rellena correctamente al guardar
                })
                .catch(error => console.error("Error:", error));
        });
    });
});
