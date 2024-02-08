// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Report"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1

		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			reqd: 1

		},
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "MultiSelectList",
			default: [],
			get_data: async function (txt) {
				let filters = {}
				if (frappe.query_report.get_filter_value("from_date")) {
					filters['posting_date'] = [">=", frappe.query_report.get_filter_value("from_date")]
				}
				if (frappe.query_report.get_filter_value("to_date")) {
					filters['posting_date'] = ["<=", frappe.query_report.get_filter_value("to_date")]
				}
				if (frappe.query_report.get_filter_value("from_date") && frappe.query_report.get_filter_value("to_date")) {
					filters['posting_date'] = ["between", [frappe.query_report.get_filter_value("from_date"), frappe.query_report.get_filter_value("to_date")]]
				}

				let item_group = (await frappe.db.get_list("Purchase Invoice", {
					filters: filters,
					fields: ["`tabPurchase Invoice Item`.item_group as value", "`tabPurchase Invoice Item`.item_group as description"],
					group_by: "`tabPurchase Invoice Item`.item_group",
					limit: 0
				}))
				return item_group
			}
		},
		{
			fieldname: "supplier_group",
			label: __("Supplier Group"),
			fieldtype: "MultiSelectList",
			default: [],
			get_data: async function (txt) {
				return frappe.db.get_link_options("Supplier Group", txt);
			}
		},
	],
	formatter: function (value, row, column, data, default_formatter) {
		if (data.row_info == 'bold') {
			value = __(default_formatter(value, row, column, data))
			value = `<b>${[undefined, null].includes(value) ? '' : value}</b>`;
			var $value = $(value);
			value = $value.wrap("<p></p>").parent().html();
		}
		else if (['Item', 'Supplier'].includes(data.row_info) && column.fieldname == 'name') {
			let obj = Object.assign({}, column);
			obj.fieldtype = 'Link'
			obj.options = data.row_info
			value = __(default_formatter(value, row, obj, data));
			var $value = $(value);
			value = $value.wrap("<p></p>").parent().html();
		}
		else if (data.row_info == "item_head") {
			value = `<b>${[undefined, null].includes(value) ? '' : value}</b>`
			var $value = $(value);
			value = $value.wrap("<p></p>").parent().html();
		}
		else {
			value = __(default_formatter(value, row, column, data));
		}
		return value;
	}
};
