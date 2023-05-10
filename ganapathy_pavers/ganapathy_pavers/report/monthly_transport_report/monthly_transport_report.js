// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Transport Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"width": "80",
			"reqd":1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_end(),
			"width": "80",
			"reqd":1
		},
		{
			"fieldname":"vehicle_no",
			"label": __("Vehicle No"),
			"fieldtype": "Link",
			"options": "Vehicle",
			"width": "100",
			"reqd":1
		},
		{
			"fieldname":"transport_based_on",
			"label": __("Monthly Transport Based On"),
			"fieldtype": "Select",
			"options": "Report\nSummary",
			"width": "200",
			"default":"Report"
		},
		{
			"fieldname": "new_method",
			"label": __("New Expense Method"),
			"fieldtype": "Check",
			"default": 1,
		}
	],
	formatter: function (value, row, column, data, default_formatter) {
		if (column.fieldname == "item" && data.reference_data) {
			value = $(`<span ondblclick=\'ganapathy_pavers.show_reference(\"${data.item}\", ${JSON.stringify(data.reference_data)}, \"${data.qty}\")\'>${value}</span>`);
			var $value = $(value);
			value = $value.wrap("<p></p>").parent().html();
		} else {
			value = __(default_formatter(value, row, column, data));
		}
		return value
	}
};
