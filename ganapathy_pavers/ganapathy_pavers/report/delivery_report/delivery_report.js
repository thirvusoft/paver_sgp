// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Delivery Report"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"finance_book",
			"label": __("Finance Book"),
			"fieldtype": "Link",
			"options": "Finance Book",
			"hidden" : 1
		},
		{
			"fieldname":"party",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			on_change: () => {
				var party = frappe.query_report.get_filter_value('party');
				if (party) {
					frappe.db.get_value('Customer', party, ["tax_id", "customer_name"], function(value) {
						frappe.query_report.set_filter_value('tax_id', value["tax_id"]);
						frappe.query_report.set_filter_value('customer_name', value["customer_name"]);
					});
				} else {
					frappe.query_report.set_filter_value('tax_id', "");
					frappe.query_report.set_filter_value('customer_name', "");
				}
			}
		},
		{
			"fieldname":"project",
			"label": __("Site Work"),
			"fieldtype": "Link",
			"options": "Project",
			"get_query": function() {
				var party = frappe.query_report.get_filter_value('party');
				return{
					filters: {
						"customer":party
					}
				};
			}
		},
		{
			"fieldname":"sw_status",
			"label": __("Site Work Status to don't fetch"),
			"fieldtype": "MultiSelectList",
			"options": "\nOpen\nCompleted\nTo Bill\nBilled\nCancelled\nStock Pending at Site\nRework",
			"default": "Billed",
			"get_data": function () {
				return [
					{value: "Open", description: ''},
					{value: "Completed", description: ''},
					{value: "To Bill", description: ''},
					{value: "Billed", description: ''},
					{value: "Cancelled", description: ''},
					{value: "Stock Pending at Site", description: ''},
					{value: "Rework", description: ''},
				]
			}
		},
		{
			"fieldname":"type",
			"label": __("Type"),
			"fieldtype": "Select",
			"options": "\nPavers\nCompound Wall",
		},
		{
			"fieldname":"customer_group",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group"
		},
		{
			"fieldname":"payment_terms_template",
			"label": __("Payment Terms Template"),
			"fieldtype": "Link",
			"options": "Payment Terms Template",
			"hidden" : 1
		},
		{
			"fieldname":"territory",
			"label": __("Territory"),
			"fieldtype": "Link",
			"options": "Territory"
		},
		{
			"fieldname":"sales_partner",
			"label": __("Sales Partner"),
			"fieldtype": "Link",
			"options": "Sales Partner",
			"hidden" : 1
		},
		{
			"fieldname":"sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person",
			"hidden" : 1
		},
		{
			"fieldname":"tax_id",
			"label": __("Tax Id"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname":"customer_name",
			"label": __("Customer Name"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname":"no_fetch_empty_site",
			"label": __("Don't Fetch Records with no Site"),
			"fieldtype": "Check",
			"default": 1,
		},
		{
			"fieldname":"show_invoice_amount",
			"label": __("Show Invoice Amount"),
			"fieldtype": "Check",
			"default": 0
		},
		{
			"fieldname":"invoiced_delivery",
			"label": __("Don't Show Invoiced Deliveries and their Paid Amount"),
			"fieldtype": "Check",
			"default": 1
		}
	]
};
