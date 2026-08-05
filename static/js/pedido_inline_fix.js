document.addEventListener("DOMContentLoaded", function() {

    console.log("pedido_inline_fix.js cargado correctamente");

    (function($) {

        function initSelect2(row) {
            row.find('select.admin-autocomplete').each(function() {
                $(this).djangoAdminSelect2();
            });
        }

        // Inicializar las filas existentes
        initSelect2($('.inline-group .form-row'));

        // Inicializar las filas nuevas cuando se agregan
        $(document).on('formset:added', function(event, row) {
            initSelect2(row);
        });

    })(django.jQuery);

});
