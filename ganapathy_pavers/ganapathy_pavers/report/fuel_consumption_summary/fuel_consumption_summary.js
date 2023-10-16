// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Fuel Consumption Summary"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"width": "80",
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_end(),
			"width": "80",
			"reqd": 1
		},
		{
			"fieldname": "fuel_type",
			"label": __("Fuel Type"),
			"fieldtype": "Select",
			"options": "\nPetrol\nDiesel\nNatural Gas\nElectric",
			"width": "100"
		},
		{
			"fieldname": "unit",
			"label": __("Unit"),
			"fieldtype": "Link",
			"options": "Location",
			"width": "100"
		},
		{
			"fieldname": "from_barrel",
			"label": __("From Barrel"),
			"fieldtype": "Check",
		}
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = __(default_formatter(value, row, column, data));
		if (column.fieldname == "license_plate" && data?.bold) {
			value = `<div style='font-weight: bold; background: rgb(127 221 253 / 85%) !important;'>${value}</div>`
		} else if (data?.only_bold) {
			value = `<div style='font-weight: bold;'>${value}</div>`
		}
		let $value = $(value);
		value = $value.wrap("<p></p>").parent().html();
		return value
	}
};



