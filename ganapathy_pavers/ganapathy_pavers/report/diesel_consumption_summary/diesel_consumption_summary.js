// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Diesel Consumption Summary"] = {
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
			"fieldname":"fuel_type",
			"label": __("Fuel Type"),
			"fieldtype": "Select",
			"options":"\nPetrol\nDiesel\nNatural Gas\nElectric",
			"width":"100"
		},
		{
			"fieldname":"from_barrel",
			"label": __("From Barrel"),
			"fieldtype": "Check",
		}
	]
};
