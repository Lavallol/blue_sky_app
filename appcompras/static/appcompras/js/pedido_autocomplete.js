document.addEventListener("DOMContentLoaded", function () {
    console.log("PEDIDO JS CARGADO");

    const inlines = document.querySelectorAll("tr.form-row");
    console.log("FILAS ENCONTRADAS:", inlines.length);

    inlines.forEach(inline => {
        const productoSelect = inline.querySelector("select[id$='producto']");
        const precioInput = inline.querySelector("input[id$='precio_unitario']");
        const ivaInput = inline.querySelector("input[id$='iva']");

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

                    // ✔ Autocompletar PRECIO
                    if (precioInput) precioInput.value = data.precio ?? "";

                    // ✔ Autocompletar IVA
                    if (ivaInput) ivaInput.value = data.iva ?? "";
                })
                .catch(error => console.error("Error:", error));
        });
    });
});
