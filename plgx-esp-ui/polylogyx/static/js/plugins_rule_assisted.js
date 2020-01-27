// place any jQuery/helper plugins in here, instead of separate, slower script files.

$(function() {
  var csrftoken = $('meta[name=csrf-token]').attr('content')

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  })

  $(function(){
    var hash = window.location.hash;
    hash && $('ul.nav a[href="' + hash + '"]').tab('show');
    $('.nav-tabs a').click(function (e) {
      $(this).tab('show');
      window.location.hash = this.hash;
      $(window).scrollTop(0);
    });
  });

  $('.glyphicon-trash').on('click', function(event) {
    var tr = $(this).parents('tr');
    $.ajax({
      url: $(this).data('uri'),
      contentType: "application/json",
      type: "DELETE"
    }).done(function (data, textStatus, jqXHR) {
      $(tr).remove();
      console.log(jqXHR.status);
    });
  })

  $('.activate-node').on('click', function(event) {
     if ($(this).data('uri') == null || $(this).data('uri') == '') {
        return;
      }
    var el = $(this);
    $.post($(this).data('uri'), {
      is_active: $(this).hasClass('glyphicon-unchecked') || null
    }).done(function (data, textStatus, jqXHR) {
      $(el).toggleClass('glyphicon-check glyphicon-unchecked');
    });
  })

  var qryBuilder = $('#rule_assist');
  if (qryBuilder.length) {
    var QueryBuilder = $.fn.queryBuilder.constructor;
    var event_types = [
      'STARTING_UP',
      'SHUTTING_DOWN',
      'CONNECTED',
      'CLOUD_NOTIFICATION',
      'RECEIPT',
      'NEW_PROCESS',
      'TERMINATE_PROCESS',
      'DNS_REQUEST',
      'CODE_IDENTITY',
      'NEW_TCP4_CONNECTION',
      'NEW_UDP4_CONNECTION',
      'NEW_TCP6_CONNECTION',
      'NEW_UDP6_CONNECTION',
      'TERMINATE_TCP4_CONNECTION',
      'TERMINATE_UDP4_CONNECTION',
      'TERMINATE_TCP6_CONNECTION',
      'TERMINATE_UDP6_CONNECTION',
      'NETWORK_CONNECTIONS',
      'HIDDEN_MODULE_DETECTED',
      'MODULE_LOAD',
      'FILE_CREATE',
      'FILE_DELETE',
      'NETWORK_SUMMARY',
      'FILE_GET_REP',
      'FILE_DEL_REP',
      'FILE_MOV_REP',
      'FILE_HASH_REP',
      'FILE_INFO_REP',
      'DIR_LIST_REP',
      'DIR_FINDHASH_REP',
      'MEM_MAP_REP',
      'MEM_READ_REP',
      'MEM_HANDLES_REP',
      'MEM_FIND_HANDLES_REP',
      'MEM_STRINGS_REP',
      'MEM_FIND_STRING_REP',
      'OS_SERVICES_REP',
      'OS_DRIVERS_REP',
      'OS_KILL_PROCESS_REP',
      'OS_PROCESSES_REP',
      'OS_AUTORUNS_REP',
      'HISTORY_DUMP_REP',
      'EXEC_OOB',
      'MODULE_MEM_DISK_MISMATCH',
      'YARA_DETECTION',
      'SERVICE_CHANGE',
      'DRIVER_CHANGE',
      'AUTORUN_CHANGE',
      'FILE_MODIFIED',
      'NEW_DOCUMENT',
      'GET_DOCUMENT_REP',
      'USER_OBSERVED',
      'FILE_TYPE_ACCESSED',
      'NEW_REMOTE_THREAD',
      'OS_PACKAGES_REP',
      'REGISTRY_CREATE',
      'REGISTRY_DELETE',
      'REGISTRY_WRITE',
      'REMOTE_PROCESS_HANDLE',
      'REGISTRY_LIST_REP',
      'VOLUME_MOUNT',
      'VOLUME_UNMOUNT',
      'FIM_LIST_REP',
      'FIM_HIT',
      'NETSTAT_REP',
      'THREAD_INJECTION',
      'SENSITIVE_PROCESS_ACCESS',
      'NEW_NAMED_PIPE',
      'OPEN_NAMED_PIPE',
      'DATA_DROPPED',
      'HTTP_REQUEST',
    ];
    var SUPPORTED_OPERATOR_NAMES = ['less','greater'];
    var SUPPORTED_OPERATORS = SUPPORTED_OPERATOR_NAMES.map(function (operator) {
      return QueryBuilder.OPERATORS[operator];
    });
    var COLUMN_OPERATORS = SUPPORTED_OPERATOR_NAMES.map(function (operator) {
      return {
        type: 'column_' + operator,
        nb_inputs: QueryBuilder.OPERATORS[operator].nb_inputs + 1,
        multiple: true,
        apply_to: ['string'],
      };
    });
    var SUPPORTED_COLUMN_OPERATORS = SUPPORTED_OPERATOR_NAMES.map(function (operator) {
      return 'column_' + operator;
    });
    var existingRules;
      try {
      var v = $('#rules-hidden').val();
        if (v) {
          existingRules = JSON.parse(v);
          console.log(existingRules);
        }
      } catch (e) {
        console.log(e);
      }
      qryBuilder.queryBuilder({
        plugins: {
          'bt-selectpicker': {
            width: '200px'
          }
        },
        filters: [{
            id: 'query_name',
            type: 'string',
            label: 'Name',
            operators: SUPPORTED_OPERATOR_NAMES,
        },{
            id: 'event_name',
            type: 'string',
            label: 'Event',
            input: 'select',
            value: event_types,
            // operators: event_types,
        }, {
    id: 'category',
    label: 'Category',
    type: 'integer',
    input: 'select',
    values: {
      1: 'Books',
      2: 'Movies',
      3: 'Music',
      4: 'Tools',
      5: 'Goodies',
      6: 'Clothes'
    },
    operators: ['equal', 'not_equal', 'in', 'not_in', 'is_null', 'is_not_null']
  },
      ],
        operators: SUPPORTED_OPERATORS.concat(COLUMN_OPERATORS),

        rules: existingRules,
      });
      qryBuilder.on('getRuleInput.queryBuilder.filter', function (evt, rule, name) {
        if (rule.operator.type.match(/^column_/) && name.match(/value_0$/)) {
          var el = $(evt.value);
          $(el).attr('placeholder', 'column name');
          ;evt.value = el[0].outerHTML;
        }
      });
      $('#submit-button').on('click', function (e) {
        var $builder = qryBuilder;
        if (!$builder) {
          return true;
        }
        if (!$builder.queryBuilder('validate')) {
          e.preventDefault();
          return false;
        }
        var rules = JSON.stringify($builder.queryBuilder('getRules'));
        $('#rules-hidden').val(rules);
        return true;
      });
    }
})
