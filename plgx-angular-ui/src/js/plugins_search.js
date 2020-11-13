var $queryBuilder1;

(function ($) {
    $(function () {

        var csrftoken = $('meta[name=csrf-token]').attr('content');

        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken)
                }
            }
        });

        $(function () {
            var hash = window.location.hash;
            hash && $('ul.nav a[href="' + hash + '"]').tab('show');

            $('.nav-tabs a').click(function (e) {
                $(this).tab('show');
                window.location.hash = this.hash;
                $(window).scrollTop(0);
            });

        });


         $queryBuilder1 = $('.query-builder');

        if ($queryBuilder1.length) {
            var QueryBuilder = $.fn.queryBuilder.constructor;

            var SUPPORTED_OPERATOR_LIST = [
                'equal',
                'contains',

            ];

            var SUPPORTED_OPERATORS = SUPPORTED_OPERATOR_LIST.map(function (operator) {
                return QueryBuilder.OPERATORS[operator];
            });

            var COLUMN_OPERATORS = SUPPORTED_OPERATOR_LIST.map(function (operator) {
                return {
                    type: 'column_' + operator,
                    nb_inputs: QueryBuilder.OPERATORS[operator].nb_inputs + 1,
                    multiple: true,
                    apply_to: ['string'],        // Currently, all column operators are strings
                };
            });

            var SUPPORTED_COLUMN_OPERATORS = SUPPORTED_OPERATOR_LIST.map(function (operator) {
                return 'column_' + operator;
            });

            // Copy existing names
            var CUSTOM_LANG = {};
            SUPPORTED_OPERATOR_LIST.forEach(function (op) {
                CUSTOM_LANG['column_' + op] = QueryBuilder.regional.en.operators[op];
            });

            // Custom operators

            // Get existing rules, if any.
            var existingRules;
            try {
                var v = $('#rules-hidden').val();
                if (v) {
                    existingRules = JSON.parse(v);
                }
            } catch (e) {
                // Do nothing.
            }

            $queryBuilder1.queryBuilder({
              plugins: {
                //'bt-tooltip-errors': { delay: 100 },
                'bt-selectpicker': {
                    liveSearch: true,
                    html: true,
                    width: '200px',
                    liveSearchPlaceholder: 'Search here...'
                },
                'sortable': {
                    icon: 'glyphicon glyphicon-move',
                }
              },

                filters: [
{
                    id: 'hotfix_id',
          label: 'hotfix_id',
          type: 'string',


        },{
                    id: 'product_name',
          label: 'product_name',
          type: 'string',

        },{
                    id: 'product_signatures',
          label: 'product_signatures',
          type: 'string',

        },{
                    id: 'product_state',
          label: 'product_state',
          type: 'string',

        },{
                    id: 'product_type',
          label: 'product_type',
          type: 'string',

        },{
                    id: 'target_path',
          label: 'target_path',
          type: 'string',

        },{
                    id: 'hostnames',
          label: 'hostnames',
          type: 'string',

        },{
                    id: 'common_name',
          label: 'common_name',
          type: 'string',

        },{
                    id: 'issuer',
          label: 'issuer',
          type: 'string',

        },{
                    id: 'md5',
          label: 'md5',
          type: 'string',

        },{
                    id: 'domain_name',
          label: 'domain_name',
          type: 'string',

        },{
                    id: 'url',
          label: 'url',
          type: 'string',

        },{
                    id: 'sha1',
          label: 'sha1',
          type: 'string',

        },{
                    id: 'path',
          label: 'path',
          type: 'string',

        },{
                    id: 'process_name',
          label: 'process_name',
          type: 'string',

        },{
                    id: 'parent_path',
          label: 'parent_path',
          type: 'string',

        },{
                    id: 'issuer_name',
          label: 'issuer_name',
          type: 'string',

        },{
                    id: 'version',
          label: 'version',
          type: 'string',
          value:'kernel_version',

        },{
                    id: 'identifier',
          label: 'identifier',
          type: 'string',
          value:'chrome_identifier',

        },{
                    id: 'name',
          label: 'name',
          type: 'string',
          value:'program_name',

        }
                ],


                operators: SUPPORTED_OPERATORS,

                lang: {
                    operators: CUSTOM_LANG,
                },


                // Existing rules (if any)
                rules: existingRules,
            });

            // Set the placeholder of the first value for all 'column_*' rules to
            // 'column name'.  A bit hacky, but this seems to be the only way to
            // accomplish this.



//                          $queryBuilder1.on('getRuleInput.queryBuilder.filter', function (evt, rule, name) {
//$('.rule-value-container').find('*').each(function(){
//var elem_name=$(this).attr('name');
// if(elem_name!=undefined && elem_name.includes('value_0')&& $(this).is('select')){
//  var parent_elem=$(this).parent();
//                           parent_elem.empty();
//                          parent_elem.append( "<input type='text' placeholder='value' name='"+elem_name+"' class='form-control'/>" );
// }
//});
//            });







            $('#submit-button').on('click', function (e) {
                var $builder = $queryBuilder1;

                if (!$builder) {
                    return true;
                }

                if (!$builder.queryBuilder('validate')) {
                    e.preventDefault();
                    return false;
                }

                var rules = JSON.stringify($builder.queryBuilder('getRules'));
                alert(rules);
                $('#rules-hidden').val(rules);
                return true;
            });
        }

    });
})(jQuery);
function submitConditions(){

     var $builder = $queryBuilder1;

     if (!$builder) {
       return true;
     }

    if (!$builder.queryBuilder('validate')) {

                    return false;
   }

                var rules = JSON.stringify($builder.queryBuilder('getRules'));
                $('#rules-hidden').val(rules);
                return true;
            }
