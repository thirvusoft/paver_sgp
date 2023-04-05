// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Lego Block Production Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.month_start(),
			"reqd":1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.month_end(),
			"reqd":1
		},
		{
			"fieldname": "expense_summary",
			"label": __("Expense Summary"),
			"fieldtype": "Check",
		},
		{
			"fieldname": "new_method",
			"label": __("New Expense Method"),
			"fieldtype": "Check",
			"default": 0,
			"hidden": frappe.session.user!="Administrator"
		}
	]
};
