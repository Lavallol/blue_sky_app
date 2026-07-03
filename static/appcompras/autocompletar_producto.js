(function() {

    function inicializarFila(row) {
        const selectProducto = row.querySelector('select[id$="-producto"]');
        if (!selectProducto) return;

        selectProducto.addEventListener("change", function() {
            const productoId = this.value;
            if (!productoId) return;

            // URL REAL que sí existe en tu admin
            const url = "/admin/appcompras/albarancompra/api/producto/" + productoId + "/";

            fetch(url, { credentials: "same-origin" })
                .then(response => response.json())
                .then(data => {
                    if (data.error) return;

                    const precioInput = row.querySelector('input[id$="-precio_unitario"]');
                    const ivaInput = row.querySelector('input[id$="-iva"]');

                    if (precioInput) precioInput.value = data.precio;
                    if (ivaInput) ivaInput.value = data.iva;
                })
                .catch(err => console.error("Error cargando producto:", err));
        });
    }

    function inicializarTodasLasFilas() {
        const filas = document.querySelectorAll("table tbody tr");
        filas.forEach(inicializarFila);
    }

    document.addEventListener("DOMContentLoaded", inicializarTodasLasFilas);

    document.body.addEventListener("click", function(e) {
        if (e.target && e.target.classList.contains("add-row")) {
            setTimeout(inicializarTodasLasFilas, 200);
        }
    });

})();
