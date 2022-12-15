// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Job Worker - Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -7),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"width": "80"
		},
		{
			"fieldname":"site_name",
			"label": __("Site Name"),
			"fieldtype": "Link",
			"options": "Project",
			"width": "100"
		},
		{
			"fieldname":"employee",
			"label": __("Job Worker"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": "100"
		},
		{
			"fieldname": "group_site_work",
			"label": "Group Site Work",
			"fieldtype": "Check",
			"default": 1
		}
	]
};
