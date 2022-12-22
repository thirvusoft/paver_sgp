// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */
 
frappe.query_reports["Site Work Wise Delivery Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -7),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"width": "80"
		},
		{
			"fieldname":"site_name",
			"label": __("Site Name"),
			"fieldtype": "Link",
			"options": "Project",
			"width": "100",
			// "filters":  {
			// 			"customer": frappe.query_report.get_filter_value("customer")
			// 		}
				
		},
		{
			"fieldname":"sales_type",
			"label": __("Sales Type"),
			"fieldtype": "Select",
			"options": "\nPavers\nCompound Wall",
			"width": "100"
		},
		{
			"fieldname":"customer",
			"label": __("Custome Name"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": "100"
		},
		{
			"fieldname":"item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": "100"
		},
		{
			"fieldname":"group_by",
			"label": __("Group By"),
			"fieldtype": "Select",
			"options": "Date\nItem Wise\nCustomer Wise",
			"default": "Date",
			"width": "100"
		},
		{
			"fieldname":"group_total",
			"label": __("Group Total"),
			"fieldtype": "Check",
			"default": "1",
		}
	]
 };
 