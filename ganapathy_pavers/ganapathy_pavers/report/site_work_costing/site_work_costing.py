# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from ganapathy_pavers import get_buying_rate, uom_conversion
from ganapathy_pavers import get_valuation_rate



def execute(filters={}):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data


def get_data(filters={}):

	square_foot="SQF"
	data=[]
	ts_filters={}
	for i in filters:
		if i!="item_group":
			ts_filters[i]=filters[i]
	sw_docs=frappe.get_all("Project", ts_filters, pluck="name")
	for doc in sw_docs:
		sw_data=[]
		sw_doc=frappe.get_doc("Project", doc)
		sw_data.append({
			"customer": sw_doc.customer,
			"site_work": sw_doc.name,
			"sqft_supplied": None,
			"measurement_sqft": None,
			"man_buy_cost": None,
			"transportation_cost": None,
			"jw_cost": None,
			"additional_cost": None,
			"actual_cost": None,
			"bill_cost": None,
			"profit": None,
		})
		item_details=[]
		valuation_rate=[]

		for row in sw_doc.item_details:
			if filters.get("item_group") and frappe.get_value("Item", row.item, "item_group") not in (filters.get('item_group') or []):
				continue
			if row.item in item_details:
				continue
			stock_qty=0
			for i in sw_doc.item_details:
				if row.item==i.item:
					stock_qty+=i.stock_qty
			item_details.append(row.item)
			sqft_supplied=0
			for row1 in sw_doc.delivery_detail:
				if(row1.item==row.item):
					sqft_supplied+=uom_conversion(row1.item, row1.stock_uom, row1.delivered_stock_qty, square_foot)
			vr=get_valuation_rate(item_code=row.item, warehouse=row.warehouse, posting_date=frappe.utils.get_date_str(sw_doc.creation))
			valuation_rate.append((vr or 0) * (stock_qty or 0))
			sw_data.append({
				"item_code": row.item,
				"sqft_supplied":sqft_supplied,
				"man_buy_cost": (vr or 0) * (stock_qty or 0),
			})
		item_details_compound_wall=[]

		for row in sw_doc.item_details_compound_wall:
			if filters.get("item_group") and frappe.get_value("Item", row.item, "item_group") not in (filters.get('item_group') or []):
				continue
			if row.item in item_details_compound_wall:
				continue
			stock_qty=0
			for i in sw_doc.item_details_compound_wall:
				if row.item==i.item:
					stock_qty+=i.stock_qty
			item_details_compound_wall.append(row.item)
			sqft_supplied=0
			for row1 in sw_doc.delivery_detail:
				if(row1.item==row.item):
					sqft_supplied+=uom_conversion(row1.item, row1.stock_uom, row1.delivered_stock_qty, square_foot)
			vr=get_valuation_rate(item_code=row.item, warehouse=row.warehouse, posting_date=frappe.utils.get_date_str(sw_doc.creation))
			valuation_rate.append((vr or 0) * (stock_qty or 0))
			sw_data.append({
				"item_code": row.item,
				"sqft_supplied":sqft_supplied,
				"man_buy_cost": (vr or 0) * (stock_qty or 0),
			})
		raw_material=[]
		buying_rate=[]

		for row in sw_doc.raw_material:
			if filters.get("item_group") and frappe.get_value("Item", row.item, "item_group") not in (filters.get('item_group') or []):
				continue
			if row.item in raw_material:
				continue
			stock_qty=0
			sqft_supplied=0
			for i in sw_doc.raw_material:
				if row.item==i.item:
					stock_qty+=i.stock_qty
					sqft_supplied+=i.delivered_quantity
			raw_material.append(row.item)
			warehouse=frappe.get_value("Sales Order Item", {"item_code":row.item, "parent":row.sales_order}, "warehouse")
			if not warehouse:
				warehouse=frappe.get_all("Sales Order Item", {"parent":"SGP-SO-0722-00004", "warehouse":["is", "set"]}, pluck="warehouse")
				if warehouse:
					warehouse=warehouse[0]
			vr=get_buying_rate(item_code=row.item, warehouse=warehouse, posting_date=frappe.utils.get_date_str(sw_doc.creation))
			buying_rate.append((vr or 0) * (stock_qty or 0))
			sw_data.append({
				"item_code": row.item,
				"sqft_supplied":sqft_supplied,
				"man_buy_cost": (vr or 0) * (stock_qty or 0),
			})

		sw_data.append({
			"sqft_supplied": sum([uom_conversion(row.item, row.stock_uom, row.delivered_stock_qty, square_foot) or 0 for row in sw_doc.delivery_detail]+[row.delivered_quantity for row in sw_doc.raw_material]),
			"measurement_sqft": sw_doc.get("measurement_sqft"),
			"man_buy_cost": sum(buying_rate) + sum(valuation_rate),
			"transportation_cost": sw_doc.get("transporting_cost"),
			"jw_cost": sw_doc.get("total_job_worker_cost"),
			"additional_cost": sw_doc.get("total"),
			"actual_cost": sw_doc.get("actual_site_cost_calculation"),
			"bill_cost": sw_doc.get("total_expense_amount"),
			"profit": sw_doc.get("site_profit_amount")
		})
		if len(sw_data)>2:
			data+=sw_data#+[{}, {}]
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
			"width": 250,
			"fieldtype": "Link",
			"options": "Item",
		},
		{
			"fieldname": "sqft_supplied",
			"label": "Sqft / Qty Supplied",
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