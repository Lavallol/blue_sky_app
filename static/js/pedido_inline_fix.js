console.log("pedido_inline_fix.js cargado correctamente");

django.jQuery(function($) {

    function initSelect2(row) {
        row.find('select.admin-autocomplete').each(function() {
            $(this).djangoAdminSelect2();
        });
    }

    // Inicializar las filas existentes
    initSelect2($('.inline-group .form-row'));

    // Inicializar las filas nuevas cuando se agregan
    django.jQuery(document).on('formset:added', function(event, row) {
        initSelect2(row);
    });

});
