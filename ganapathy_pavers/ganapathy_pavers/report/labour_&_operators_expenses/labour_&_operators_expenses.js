// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Labour & Operators Expenses"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"width": "80",
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",			
			"default": frappe.datetime.month_end(),
			"width": "80",
			"reqd": 1
		},
		{
			"fieldname": "machine",
			"label": __("Machine"),
			"fieldtype": "MultiSelectList",
			"options": "Workstation",
			default: [],
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
