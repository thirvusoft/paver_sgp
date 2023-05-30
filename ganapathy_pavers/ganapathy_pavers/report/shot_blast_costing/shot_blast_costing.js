// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */
let ponnusamy = 0;
var currentDate = moment();
var prevMonthStart = moment(currentDate).subtract(1, 'month').startOf('month').format();
var prevMonthEnd = moment(currentDate).subtract(1, 'month').endOf('month').format();

frappe.query_reports["Shot Blast Costing"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: prevMonthStart,
			reqd: 1,
			on_change: on_change
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: prevMonthEnd,
			reqd: 1,
			on_change: on_change
		},
		{
			fieldname: "item_code",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
		},
		{
			fieldname: "material_manufacturing",
			label: __("Material Manufacturing"),
			fieldtype: "Link",
			options: "Material Manufacturing",
		},
		{
			fieldname: "group_by",
			label: __("Group By"),
			fieldtype: "Select",
			options: "Date\nItem",
			default: "Item",
		}
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = __(default_formatter(value, row, column, data));
		if (data && ["Group Total", "Total"].includes(data.item_code)) {
			value = `<b>${value}</b>`
		}

		return value
	}
};

async function on_change() {
	await ganapathy_pavers.apply_sbc_report_filters(
		frappe.query_report.get_filter("from_date").get_value(),
		`${frappe.query_report.get_filter("to_date").get_value()} 23:59:59`,
		frappe.query_report.get_filter("item_code")
	)
	frappe.query_report.refresh()
}