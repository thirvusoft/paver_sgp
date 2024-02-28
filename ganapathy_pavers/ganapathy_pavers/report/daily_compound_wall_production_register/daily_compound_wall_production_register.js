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
			"label": __("Type"),
			"fieldtype": "Link",
			"options": "Compound Wall Type",
			"default": "Compound Wall",
			"width": "80",
			"reqd": 1,
			"on_change": function() {
				let value = frappe.query_report.get_filter_value("compound_wall_type");
				frappe.query_report.page.set_title(`Daily ${value || 'Compound Wall'} Production Register`)
				frappe.query_report.refresh()
			}
		}
	]
 };
 
 frappe.query_report.get_columns_for_print = function (print_settings, custom_format) {
    let columns = [];

    if (print_settings && print_settings.columns) {
        columns = frappe.query_report.get_visible_columns().filter(column =>
            print_settings.columns.includes(column.fieldname)
        );
    } else {
        columns = frappe.query_report.get_visible_columns();
    }

    return columns;
}
