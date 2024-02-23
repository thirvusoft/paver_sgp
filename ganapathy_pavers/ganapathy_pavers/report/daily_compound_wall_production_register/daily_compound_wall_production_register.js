// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Compound Wall Production Register"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"width": "80",
			"reqd":1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"width": "80",
			"reqd":1
		},
		{
			"fieldname": "compound_wall_type",
			"label": __("Compound Wall Type"),
			"fieldtype": "Link",
			"options": "Compound Wall Type",
			"default": "Compound Wall",
			"width": "80",
			"reqd": 1
		}
	]
 };
 