// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Site Work Wise Delivery Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -7),
			"width": "80"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"width": "80"
		},
		{
			"fieldname": "site_name",
			"label": __("Site Name"),
			"fieldtype": "Link",
			"options": "Project",
			"width": "100",
			"get_query": function () {
				var customer = frappe.query_report.get_filter_value('customer');
				if (!customer) {
					return {}
				}
				return {
					filters: {
						"customer": customer
					}
				};
			}

		},
		{
			"fieldname": "sales_type",
			"label": __("Type"),
			"fieldtype": "Link",
			"options": "Types",
			"width": "100"
		},
		{
			"fieldname": "customer",
			"label": __("Custome Name"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": "100"
		},
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": "100"
		},
		{
			"fieldname": "group_by",
			"label": __("Group By"),
			"fieldtype": "Select",
			"options": "Date\nItem Wise\nCustomer Wise",
			"default": "Date",
			"width": "100"
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "MultiSelectList",
			get_data: async function (txt) {
				let r = [];
				let item_groups = (await frappe.db.get_list("Delivery Note Item", { fields: ['item_group'], limit: 0 }))
				item_groups.forEach(t => {
					if (!r.includes(t.item_group)) {
						 r.push(t.item_group) }
				})
				return frappe.db.get_link_options("Item Group", txt, {name: ["in", r]})
			},
			"width": "100"
		},
		{
			"fieldname": "vehicle_no",
			"label": __("Vehicle"),
			"fieldtype": "MultiSelectList",
			get_data: async function (txt) {
				let r = [];
				let customer = frappe.query_report.get_filter_value("customer")
				let site = frappe.query_report.get_filter_value("site_name")
				let from_date = frappe.query_report.get_filter_value("from_date")
				let to_date = frappe.query_report.get_filter_value("to_date")

				let filters = {"docstatus": 1}
				if (customer) {
					filters["customer"] = customer
				}
				if (site) {
					filters["site_work"] = site
				}
				if (from_date) {
					filters['posting_date'] = ['>=', from_date]
				}
				if (to_date) {
					filters['posting_date'] = ['<=', to_date]
				}
				if (from_date && to_date) {
					filters['posting_date'] = ['between', [from_date, to_date]]
				}
				let vehicles = (await frappe.db.get_list("Delivery Note", { filters: filters, fields: ['own_vehicle_no', 'vehicle_no'], limit: 0 }))
				vehicles.forEach(t => {
					if ((t.own_vehicle_no?t.own_vehicle_no:t.vehicle_no) && !r.includes(t.own_vehicle_no?t.own_vehicle_no:t.vehicle_no)) { 
						r.push(t.own_vehicle_no?t.own_vehicle_no:t.vehicle_no) 
					}
				})
				var result=[]
				r.forEach(t => {
					result.push({value:t,description:t})
				})
				return result
			},
		},
		{
			"fieldname": "group_total",
			"label": __("Group Total"),
			"fieldtype": "Check",
			"default": "1",
		},
		{
			"fieldname": "summary",
			"label": __("Summary"),
			"fieldtype": "Check",
		}
	]
};
