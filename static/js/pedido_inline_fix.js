function inicializar_autocompletado(row) {
    row.querySelectorAll('input, select').forEach(input => {
        input.dispatchEvent(new Event('input'));
    });
}

document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('change', function(e) {
        if (e.target.name && e.target.name.includes('producto')) {
            const form = e.target.closest('.dynamic-pedidocompralinea_set');
            if (form) {
                form.querySelectorAll('input, select').forEach(input => {
                    input.dispatchEvent(new Event('input'));
                });
            }
        }
    });
});

django.jQuery(document).on('formset:added', function(event, row) {
    inicializar_autocompletado(row[0]);
});
