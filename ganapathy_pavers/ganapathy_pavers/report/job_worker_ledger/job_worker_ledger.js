// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Job Worker Ledger"] = {
	filters: [
		{
			label: __("From Date"),
			fieldname: "from_date",
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			label: __("To Date"),
			fieldname: "to_date",
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "employee",
			label: __("Job Worker"),
			fieldtype: "Link",
			reqd: 1,
			options: "Employee",
			get_query: function () {
				return {
					"filters": {
						"designation": "Job Worker",
					}
				}
			}
		},
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = __(default_formatter(value, row, column, data));
		if (data.bold == 1) {
			value = $(`<span>${value}</span>`);
			var $value = $(value).css("font-weight", "bold");
			value = $value.wrap("<p></p>").parent().html();
		}

		return value;
	},
};
