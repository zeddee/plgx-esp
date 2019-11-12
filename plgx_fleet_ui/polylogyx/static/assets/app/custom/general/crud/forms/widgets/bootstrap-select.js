// Class definition

var BootstrapSelect = function () {

    // Private functions
    var demos = function () {
        // minimum setup
        $('.kt-selectpicker').selectpicker();
    }

    return {
        // public functions
        init: function() {
            demos();
        }
    };
}();

jQuery(document).ready(function() {
    BootstrapSelect.init();
});
