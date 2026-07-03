document.addEventListener("DOMContentLoaded", function () {
    const proveedorSelect = document.getElementById("id_proveedor");

    if (!proveedorSelect) return;

    proveedorSelect.addEventListener("change", function () {
        const proveedorId = this.value;

        if (proveedorId) {
            const url = new URL(window.location.href);
            url.searchParams.set("proveedor", proveedorId);
            window.location.href = url.toString();
        }
    });
});
