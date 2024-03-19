// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["CW Material Consumption"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
		},
		{
			fieldname: 'compound_wall_type',
			label: 'Compound Wall Type',
			fieldtype: 'MultiSelectList',
			get_data: async (txt) => {
				return frappe.db.get_link_options('Compound Wall Type', txt);
			}
		},
		{
			fieldname: 'compound_wall_sub_type',
			label: 'Compound Wall Sub Type',
			fieldtype: 'MultiSelectList',
			get_data: async (txt) => {
				return frappe.db.get_link_options('Compound Wall Sub Type', txt, {
					'compound_wall_type': ['in', frappe.query_report.get_filter_value('compound_wall_type')]
				});
			}
		},
	]
};
