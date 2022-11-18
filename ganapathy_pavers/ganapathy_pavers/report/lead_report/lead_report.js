// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Lead Report"] = {
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
			"fieldname":"lead_type",
			"label": __("Lead Type"),
			"fieldtype": "Select",
			"options":"\nPaver\nCompound Wall",
			"width":"100"
		},
		{
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options":"\nLead\nOpen\nReplied\nOpportunity\nQuotation\nLost Quotation\nInterested\nConverted\nDo Not Contact",
			"width":"100"
		}

	]
};
