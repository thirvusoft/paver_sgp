// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Paver Production Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"width": "80",
			"reqd": 1,
			on_change: on_change
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_end(),
			"width": "80",
			"reqd": 1,
			on_change: on_change
		},
		{
			"fieldname": "item",
			"label": __("Item"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Item",
		},
		{
			"fieldname": "paver_type",
			"label": __("Paver Type"),
			"fieldtype": "Link",
			"options": "Paver Type",
			"width": "100",
		},
		{
			"fieldname": "machine",
			"label": __("Machine"),
			"fieldtype": "MultiSelectList",
			"options": "Workstation",
			default: [],
			on_change: on_change,
			get_data: async function (txt) {
				let ws = (await frappe.db.get_list("Material Manufacturing", { fields: ["work_station"], limit: 0}))
				let machines = []
				ws.forEach(data => {
					if (!machines.includes(data.work_station)) {
						machines.push(data.work_station)
					}
				});
				return frappe.db.get_link_options('Workstation', txt, {
					name: ["in", machines]
				});
			}
		},
		{
			"fieldname": "expense_summary",
			"label": __("Expense Summary"),
			"fieldtype": "Check",
		},
		{
			"fieldname": "new_method",
			"label": __("New Expense Method"),
			"fieldtype": "Check",
			"default": 1,
		},
		{
			"fieldname": "vehicle_summary",
			"label": __("Vehicle Summary"),
			"fieldtype": "Check",
			"default": 0,
		}
	],
	formatter: function (value, row, column, data, default_formatter) {
		if (column.fieldname == "qty" && data.reference_data) {
			value = __(default_formatter(value, row, column, data));
			value = $(`<span ondblclick=\'ganapathy_pavers.show_reference(\"${data.qty}\", ${JSON.stringify(data.reference_data)}, \"${data.uom}\")\'>${value}</span>`);
			var $value = $(value);
			value = $value.wrap("<p></p>").parent().html();
		} else {
			value = __(default_formatter(value, row, column, data));
		}
		return value
	}
};

async function on_change() {
	await ganapathy_pavers.apply_paver_report_filters(
		frappe.query_report.get_filter("from_date").get_value(),
		frappe.query_report.get_filter("to_date").get_value(),
		frappe.query_report.get_filter("machine").get_value(),
		frappe.query_report.get_filter("item")
		)
	frappe.query_report.refresh()
}
