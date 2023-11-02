// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Payment Report"] = {
	"filters": [
		{
			fieldname: "party",
			label: __("Party"),
			fieldtype: "Select",
			options: 'Customer\nSupplier',
			default:"Customer",
			reqd:1
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd:1

		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			reqd:1

		},
		{
			fieldname: 'branch',
			label: 'Branch',
			fieldtype: 'Link',
			options: 'Branch',
		},
		{
			fieldname: 'site_work',
			label: 'Site Work',
			fieldtype: 'Link',
			options: 'Project',
		},
		{
			fieldname: 'type',
			label: 'Type',
			fieldtype: 'Select',
			options: '\nPavers\nCompound Wall\nOthers',
		}
	]
};
