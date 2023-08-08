// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Wise Purchase"] = {
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
			fieldname: "supplier",
			label: __("Supplier"),
			fieldtype: "Link",
			options: "Supplier"
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "MultiSelectList",
			get_data: function () {
				let filters = [
					['Purchase Invoice Item', 'warehouse', 'is', 'set'],
					['Purchase Invoice', 'update_stock', '=', 1]
				];
				if (frappe.query_report.get_filter_value("from_date")) {
					filters.push(['Purchase Invoice', 'posting_date', '>=', frappe.query_report.get_filter_value("from_date")]);
				}
				if (frappe.query_report.get_filter_value("to_date")) {
					filters.push(['Purchase Invoice', 'posting_date', '<=', frappe.query_report.get_filter_value("to_date")]);
				}
				if (frappe.query_report.get_filter_value("supplier")) {
					filters.push(['Purchase Invoice', 'supplier', '=', frappe.query_report.get_filter_value("supplier")]);
				}
				return frappe.db.get_list("Purchase Invoice", {
					filters: filters,
					fields: [
						'`tabPurchase Invoice Item`.warehouse as value',
						'`tabPurchase Invoice Item`.warehouse as description'
					],
					group_by: '`tabPurchase Invoice Item`.warehouse',
					limit: 0
				})
			}
		},
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "MultiSelectList",
			get_data: function () {
				return frappe.db.get_list("Purchase Invoice", {
					filters: [
						['Purchase Invoice Item', 'item_group', 'is', 'set'],
						['Purchase Invoice', 'update_stock', '=', 1]
					],
					fields: [
						'`tabPurchase Invoice Item`.item_group as value',
						'`tabPurchase Invoice Item`.item_group as description'
					],
					group_by: '`tabPurchase Invoice Item`.item_group',
					limit: 0
				})
			}
		},
	]
};
