"use strict";
var common_table;
var KTDatatablesBasicScrollable = function() {

	var initTable2 = function() {
		var table = $('#node_table');
	  if(table.DataTable != undefined)
	  {
		// begin second table
	common_table =	table.DataTable({
			// scrollY: '60vh',
			// scrollX: true,
			ordering: false,
			scrollCollapse: true,
			createdRow: function(row, data, index) {
			},
			columnDefs: [
				{
				}],
		});
	}
	};

	return {

		//main function to initiate the module
		init: function() {
			initTable2();
		},

	};

}();

jQuery(document).ready(function() {
	KTDatatablesBasicScrollable.init();
});
