from flask_assets import Bundle, Environment

css = Bundle(

    'assets/vendors/general/perfect-scrollbar/css/perfect-scrollbar.css',
    'assets/vendors/general/socicon/css/socicon.css',
    'assets/vendors/custom/vendors/line-awesome/css/line-awesome.css',
    'assets/vendors/custom/vendors/flaticon/flaticon.css',
    'assets/vendors/custom/vendors/flaticon2/flaticon.css',
    'assets/vendors/custom/vendors/fontawesome5/css/all.min.css',
    'assets/demo/default/base/style.bundle.css',
    'assets/demo/default/skins/brand/dark.css',

    'assets/demo/default/skins/aside/dark.css',

    'assets/vendors/general/perfect-scrollbar/css/perfect-scrollbar.css',
    'assets/vendors/general/select2/dist/css/select2.css',
    'assets/vendors/general/socicon/css/socicon.css',

    'assets/vendors/general/bootstrap-select/dist/css/bootstrap-select.css',
    'assets/vendors/general/sweetalert2/dist/sweetalert2.css',

    'assets/demo/default/base/style.bundle.css',

    'assets/bootstrap-tagsinput.css',
    'css/cube.css',
    'css/patternfly/c3.min.css',
    'css/patternfly/timeline.css',
    'css/patternfly/patternfly-additions.min.css',

    'assets/demo/default/skins/header/base/light.css',
    'assets/demo/default/skins/header/menu/light.css',

    'css/datatable.css',
    'assets/vendors/custom/datatables/datatables.bundle.css',
    filters='cssmin',
    output='public/css/common.css',
)

js = Bundle(

    # old start
    'assets/vendors/general/jquery/dist/jquery.js',
    'assets/vendors/general/popper.js/dist/umd/popper.js',
    'assets/vendors/general/bootstrap/dist/js/bootstrap.min.js',
    'assets/vendors/general/moment/min/moment.min.js',
    'assets/vendors/general/tooltip.js/dist/umd/tooltip.min.js',
    'assets/vendors/general/perfect-scrollbar/dist/perfect-scrollbar.js',
    'assets/vendors/general/jquery-form/dist/jquery.form.min.js',
    'assets/vendors/general/block-ui/jquery.blockUI.js',
    'assets/vendors/general/bootstrap-select/dist/js/bootstrap-select.js',
    'assets/vendors/general/typeahead.js/dist/typeahead.bundle.js',
    'assets/vendors/general/autosize/dist/autosize.js',
    'assets/vendors/general/clipboard/dist/clipboard.min.js',
    'assets/demo/default/base/scripts.bundle.js',
    'assets/app/custom/general/dashboard.js',
    'assets/app/custom/login/login-general.js',
    'assets/app/bundle/app.bundle.js',

    'assets/vendors/general/sweetalert2/dist/sweetalert2.js',

    'assets/vendors/custom/sweetalert2/init.js',
    'assets/app/custom/general/components/extended/sweetalert2.js',

    'assets/vendors/general/select2/dist/js/select2.full.js',
    'assets/vendors/general/inputmask/dist/jquery.inputmask.bundle.js',

    'assets/bootstrap-tagsinput.js',
    'assets/vendors/custom/datatables/datatables.bundle.js',

    'assets/app/custom/general/crud/datatables/basic/scrollable.js',
    'libs/jquery-extendext/jQuery.extendext.js',

    'libs/jQuery-QueryBuilder/dist/js/query-builder.standalone.js',
    'assets/js/plugins.js',
    'libs/interact/dist/interact.js',
    'js/util.js',
    'js/d3.v4.min.js',
    'js/d3-selection-multi.v1.js',

    filters='jsmin',
    output='public/js/common.js',
)

assets = Environment()

assets.register('js_all', js)
assets.register('css_all', css)
