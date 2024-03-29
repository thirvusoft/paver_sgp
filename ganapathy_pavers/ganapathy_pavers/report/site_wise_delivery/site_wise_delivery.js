// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Site Wise Delivery"] = {
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
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "MultiSelectList",
			default: [],
			get_data: async function (txt) {
				let item_group = (await frappe.db.get_list("Delivery Note", { fields: ["`tabDelivery Note Item`.item_group as value", "`tabDelivery Note Item`.item_group as description"], group_by: "`tabDelivery Note Item`.item_group", limit: 0 }))
				return item_group
			}
		},
		{
			fieldname: "site_work",
			label: __("Site"),
			fieldtype: "Link",
			options: 'Project',
		},
		{
			fieldname: "work",
			label: __("Work"),
			fieldtype: "MultiSelectList",
			get_data: async function (txt) {
				let work = (await frappe.db.get_list("Sales Order", {
					// filters: [["Sales Order Item", "work", "!=", ""]],
					fields: ["`tabSales Order Item`.work as value", "`tabSales Order Item`.work as description"],
					group_by: "`tabSales Order Item`.work", limit: 0 }))
				return work
			}
		},
		{
			fieldname: "is_return",
			label: __("Is Return"),
			fieldtype: "Check",
		},
	]
};
