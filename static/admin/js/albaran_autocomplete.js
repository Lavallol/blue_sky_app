document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("select[id$='producto']").forEach(function (select) {
        select.addEventListener("change", function () {
            const row = this.closest("tr.form-row");
            const precioInput = row.querySelector("input[id$='precio_unitario']");
            const ivaSelect = row.querySelector("select[id$='iva']");

            const productoId = this.value;
            if (!productoId) return;

            fetch(`/admin/appcompras/albarancompra/api/producto/${productoId}/`)
                .then(response => response.json())
                .then(data => {
                    if (precioInput && (!precioInput.value || precioInput.value === "0")) {
                        precioInput.value = data.precio_compra;
                    }
                    if (ivaSelect && !ivaSelect.value) {
                        ivaSelect.value = data.iva_id;
                    }
                });
        });
    });
});
