// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Paver Production Register"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"width": "80",
			"reqd":1,
			on_change: on_change
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"width": "80",
			"reqd":1,
			on_change: on_change
		},
		{
			"fieldname":"item",
			"label": __("Item"),
			"fieldtype": "Link",
			"options":"Item",
			"width": "80"
		
		},
		{
			"fieldname":"machine",
			"label": __("Machine"),
			"fieldtype": "MultiSelectList",
			"options":"Workstation",
			"width": "80",
			default: [],
			on_change: on_change,
			get_data: async function (txt) {
				let ws = (await frappe.db.get_list("Material Manufacturing", { fields: ["work_station"], limit: 0 }))
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
		}

	]
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