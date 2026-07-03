document.addEventListener("DOMContentLoaded", function () {
    const proveedorInput = document.querySelector("#id_proveedor");

    if (!proveedorInput) return;

    proveedorInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            const saveButton = document.querySelector("input[name='_save']");
            if (saveButton) saveButton.click();
        }
    });
});
