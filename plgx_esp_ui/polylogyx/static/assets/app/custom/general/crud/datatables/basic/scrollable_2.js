"use strict";
var KTDatatablesScrollable = function() {

	var initTable = function() {
		var tab = $('#node_table');

		// begin second table
		tab.DataTable({
			scrollY: '55vh',
			// scrollX: true,
			ordering: false,
			scrollCollapse: true,
			createdRow: function(row, data, index) {
			},
			columnDefs: [
				{
				}],
		});
	};

	return {

		//main function to initiate the module
		init: function() {
			initTable();
		},

	};

}();

jQuery(document).ready(function() {
	KTDatatablesScrollable.init();
});
