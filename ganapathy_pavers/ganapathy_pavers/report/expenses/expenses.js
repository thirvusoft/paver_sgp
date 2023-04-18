// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Expenses"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			width: "80",
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			width: "80",
			reqd: 1,
		},
		{
			fieldname: "expense_type",
			label: __("Expense Type"),
			fieldtype: "Select",
			width: "80",
			options: "Vehicle\nManufacturing",
			default: "Manufacturing",
			reqd: 1,
		},
		{
			fieldname: "vehicle_summary",
			label: __("Vehicle Summary"),
			fieldtype: "Check",
			width: "80"
		}
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = __(default_formatter(value, row, column, data));
		if (column.fieldname == "expense" && data.reference_data) {
			value = $(`<span ondblclick=\'ganapathy_pavers.show_reference(\"${data.total_amount}\", ${JSON.stringify(data.reference_data)}, \"${data.uom}\")\'>${value}</span>`);
			let $value = $(value);
			value = $value.wrap("<p></p>").parent().html();
		}
		else if (data.group_total || data.total) {
			value = `<div style='font-weight: bold; background: ${data.group_total?'rgb(127 221 253 / 85%)':'rgb(242 140 140 / 81%)'} !important;'>${value}</div>`
			let $value = $(value);
			value = $value.wrap("<p></p>").parent().html();
		} 
		return value
	}
};
