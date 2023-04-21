# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": "Vehicle",
			"fieldname": "vehicle",
			"fieldtype": "Link",
			"options": "Vehicle",
			"width": 150,
		},
		{
			"label": "Expense",
			"fieldname": "expense",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": "SQFT",
			"fieldname": "sqft",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": "SQFT Cost",
			"fieldname": "sqft_cost",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": "Mileage",
			"fieldname": "mileage",
			"fieldtype": "Float",
			"width": 150,
		}
	]
	return columns

def get_data(filters):
	res = []

	conditions = ""
	conditions+=f""" and vl.select_purpose in ('Goods Supply', 'Raw Material') """
	if filters.get("from_date"):
		conditions += f""" and vl.date>="{filters.get("from_date")}" """
	if filters.get("to_date"):
		conditions += f""" and vl.date<="{filters.get("to_date")}" """

	delivery_query = lambda item_group, uom, parent, child, vl_field: f"""
		select sum(child.stock_qty*
					ifnull((
						SELECT
							uom.conversion_factor
						FROM `tabUOM Conversion Detail` uom
						WHERE
							uom.parenttype='Item' and
							uom.parent=child.item_code and
							uom.uom=child.stock_uom
					)
                	, 0)/
					ifnull((
						SELECT
							uom.conversion_factor
						FROM `tabUOM Conversion Detail` uom
						WHERE
							uom.parenttype='Item' and
							uom.parent=child.item_code and
							uom.uom='{uom}'
					)    
					, 0)
				) as qty
		from `tab{child}` child
		inner join `tab{parent}` parent
		on child.parent=parent.name and child.parenttype='{parent}'
		where
			parent.docstatus=1 and
			parent.name=vl.{vl_field} and
			child.item_group='{item_group}'
	"""

	query = f"""
		select
			vl.license_plate as vehicle,
			avg(vl.mileage) as mileage,
			sum(case when ifnull(vl.delivery_note, '') != ''
				then ifnull(({delivery_query(item_group="Pavers", uom="SQF", parent="Delivery Note", child="Delivery Note Item", vl_field="delivery_note")}), 0)
				else 0
			end) as delivered_paver,
			sum(case when ifnull(vl.delivery_note, '') != ''
				then ifnull(({delivery_query(item_group="Compound Walls", uom="SQF", parent="Delivery Note", child="Delivery Note Item", vl_field="delivery_note")}), 0)
				else 0
			end) as delivered_cw,
			sum(case when ifnull(vl.purchase_invoice, '') != ''
				then ifnull(({delivery_query(item_group="Raw Material", uom="Unit", parent="Purchase Invoice", child="Purchase Invoice Item", vl_field="purchase_invoice")}), 0)
				else 0
			end) as inward
		from  (
			SELECT *
			FROM `tabVehicle Log` _vl 
			where
				_vl.docstatus=1
				{conditions.replace("vl.", '_vl.')}
			group by _vl.delivery_note, _vl.purchase_invoice
			) vl
		where
			vl.docstatus=1
			{conditions}
		group by vl.license_plate
	"""

	vehicle_details = frappe.db.sql(query, as_dict=True)

	res = get_transport_vehicle_details(vehicle_details)
	return res

def get_transport_vehicle_details(vehicle_details):
	paver = []
	cw = []
	rm = []
	data = []

	for row in vehicle_details:
		if (row.delivered_paver):
			paver.append({
				"vehicle": row.vehicle,
				"sqft": row.delivered_paver,
				"mileage": row.mileage
			})
		
		if (row.delivered_cw):
			cw.append({
				"vehicle": row.vehicle,
				"sqft": row.delivered_cw,
				"mileage": row.mileage
			})
		
		if (row.inward):
			rm.append({
				"vehicle": row.vehicle,
				"sqft": row.inward,
				"mileage": row.mileage
			})

	if paver:
		data.append({
			"vehicle": "Paver"
		})
		data += paver
	if cw:
		if paver:
			data.append({})
		data.append({
			"vehicle": "Compound Wall"
		})
		data += cw
	if rm:
		if cw:
			data.append({})
		data.append({
			"vehicle": "Inward Report"
		})
		data += rm
	return data
