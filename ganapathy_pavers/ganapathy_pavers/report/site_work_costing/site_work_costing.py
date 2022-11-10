# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from ganapathy_pavers import uom_conversion

def execute(filters={}):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data


def get_data(filters={}):
	square_foot="SQF"
	data=[]
	sw_docs=frappe.get_all("Project", filters, pluck="name")
	for doc in sw_docs:
		sw_doc=frappe.get_doc("Project", doc)
		sw_data={
			"customer": sw_doc.customer,
			"site_work": sw_doc.name,
			"item_code": "Item",
			"sqft_supplied": sum([uom_conversion(row.item, row.stock_uom, row.delivered_stock_qty, square_foot) or 0 for row in sw_doc.delivery_detail]),
			"measurement_sqft": "0",
			"man_buy_cost": "1",
			"transportation_cost": "2",
			"jw_cost": "3",
			"additional_cost": "4",
			"actual_cost": "5",
			"bill_cost": "6",
			"profit": "7"
		}
		data.append(sw_data)
	return data


def get_columns(filters):
	columns=[
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Link",
			"options": "Customer",
		},
		{
			"fieldname": "site_work",
			"label": "Site Name",
			"fieldtype": "Link",
			"options": "Project",
		},
		{
			"fieldname": "item_code",
			"label": "Item",
			"fieldtype": "Link",
			"options": "Item",
		},
		{
			"fieldname": "sqft_supplied",
			"label": "Sqft Supplied",
			"fieldtype": "Float",
		},
		{
			"fieldname": "measurement_sqft",
			"label": "Measurement Sqft",
			"fieldtype": "Float",
		},
		{
			"fieldname": "man_buy_cost",
			"label": "Manufacturing / Buying Cost",
			"fieldtype": "Currency",
		},
		{
			"fieldname": "transportation_cost",
			"label": "Transportation Cost",
			"fieldtype": "Currency",
		},
		{
			"fieldname": "jw_cost",
			"label": "Job Worker Cost",
			"fieldtype": "Currency",
		},
		{
			"fieldname": "additional_cost",
			"label": "Additional Cost at Site",
			"fieldtype": "Currency",
		},
		{
			"fieldname": "actual_cost",
			"label": "Actual Cost at Site",
			"fieldtype": "Currency",
		},
		{
			"fieldname": "bill_cost",
			"label": "Billed Amount",
			"fieldtype": "Currency",
		},
		{
			"fieldname": "profit",
			"label": "Profit Amount",
			"fieldtype": "Currency",
		},
	]
	return columns