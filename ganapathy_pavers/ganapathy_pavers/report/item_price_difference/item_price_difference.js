// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

let attributes = []
function get_filters() {
	let report_filters = [
		{
			reqd: 1,
			default: "",
			options: "Item",
			label: __("Item"),
			fieldname: "item",
			fieldtype: "Link",
			get_query: () => {
				return {
					// filters: { "has_variants": 1 }
				}
			},
			on_change: async () => {
				await hideAndUnhideFilters(frappe.query_report.get_filter_value("item"), attributes)
				frappe.query_report.refresh()
			}
		},
		{
			fieldname:"from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			width: "80",
			reqd:1
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			width: "80",
			reqd:1
		},
	]
	frappe.db.get_list("Item Attribute").then(res => {
		res.forEach(attr => {
			let fieldname = frappe.model.scrub(attr.name)
			attributes.push(fieldname)
			report_filters.push({
				fieldname: fieldname,
				label: __(attr.name),
				fieldtype: "MultiSelectList",
				hidden: 1,
				get_data: async function (txt) {
					let data = []
					await frappe.db.get_doc("Item Attribute", attr.name).then(attr_doc => {
						attr_doc.item_attribute_values.forEach(row => {
							if (row.attribute_value) {
								data.push({
									value: row.attribute_value,
									description: row.attribute_value
								})
							}
						})
					})
					return data
				}
			})
		})
	})
	return report_filters
}

async function hideAndUnhideFilters(item_code, attributes) {
	let unhide_attributes = []
	if (item_code) {
		await frappe.db.get_doc("Item", item_code).then(item => {
			item.attributes.forEach(row => {
				unhide_attributes.push(frappe.model.scrub(row.attribute))
			})
		})
	}
	attributes.forEach(attr => {
		if (!unhide_attributes.includes(attr)) {
			frappe.query_report.get_filter(attr).df.hidden = 1
			frappe.query_report.get_filter(attr).refresh()
		} else {
			frappe.query_report.get_filter(attr).df.hidden = 0
			frappe.query_report.get_filter(attr).refresh()
		}
	})
}

frappe.query_reports["Item Price Difference"] = {
	filters: get_filters()
};
