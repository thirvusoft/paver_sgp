# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import json
import frappe, erpnext
from ganapathy_pavers.custom.py.expense import expense_tree


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
			"label": "Freight",
			"fieldname": "freight",
			"fieldtype": "Currency",
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
			"label": "Profit/Loss",
			"fieldname": "profit_loss",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": "Mileage",
			"fieldname": "mileage",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"fieldname": "bold",
			"fieldtype": "Check",
			"hidden": 1
		},
		{
			"label": 'Reference',
			"fieldname": "reference",
			"fieldtype": "Data",
			"hidden": 1
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
	vehicle_exp = get_vehicle_expenses(filters)
	res = get_transport_vehicle_details(
			vehicle_details=vehicle_details,
			vehicle_exp=vehicle_exp,
			filters=filters
		)
	
	return res

def get_vehicle_expenses(filters):
	exp_tree = expense_tree(
					from_date=filters.get('from_date'),
					to_date=filters.get('to_date'),
					expense_type="Vehicle",
					vehicle_summary=1,
					all_expenses=True,
					group_two_wheeler=False
				)
	vehicle_wise_exp = {}
	vehicle_wise_exp = calculate_expenses(exp_tree=exp_tree, vehicle_wise_exp=vehicle_wise_exp)
	return vehicle_wise_exp

def calculate_expenses(exp_tree, vehicle_wise_exp):
	for acc in exp_tree:
		if acc.get("expandable"):
			vehicle_wise_exp = calculate_expenses(acc.get("child_nodes"), vehicle_wise_exp)
		else:
			if acc.get("value") not in vehicle_wise_exp:
				vehicle_wise_exp[acc.get("value")]=0
			vehicle_wise_exp[acc.get("value")]+=(acc.get("balance") or 0)
	return vehicle_wise_exp

def get_transport_vehicle_details(vehicle_details, vehicle_exp, filters):
	paver = []
	cw = []
	rm = []
	data = []
	paver_exp, paver_sqf, paver_sqf_cost = 0, 0, 0
	cw_exp, cw_sqf, cw_sqf_cost = 0, 0, 0
	inward_freight, inward_exp, inward_sqf, inward_profit_loss = 0, 0, 0, 0
	for row in vehicle_details:
		exp = (vehicle_exp.get(row.get("vehicle")) or 0) / (((row.delivered_paver or 0) + (row.delivered_cw or 0) + (row.inward or 0)) or 1)
		if (row.delivered_paver):
			paver_exp += ((exp * (row.delivered_paver or 0)) or 0)
			paver_sqf += (row.delivered_paver or 0)
			paver_sqf_cost += ((exp * (row.delivered_paver or 0) or 0) / (row.delivered_paver or 1) or 0)
			paver.append({
				"vehicle": row.vehicle,
				"expense": exp * (row.delivered_paver or 0),
				"sqft": row.delivered_paver,
				"sqft_cost": (exp * (row.delivered_paver or 0) or 0) / (row.delivered_paver or 1),
				"mileage": row.mileage
			})
		
		if (row.delivered_cw):
			cw_exp += ((exp * (row.delivered_cw or 0)) or 0)
			cw_sqf += (row.delivered_cw or 0)
			cw_sqf_cost += ((exp * (row.delivered_cw or 0) or 0) / (row.delivered_cw or 1) or 0)
			cw.append({
				"vehicle": row.vehicle,
				"expense": exp * (row.delivered_cw or 0),
				"sqft": row.delivered_cw,
				"sqft_cost": (exp * (row.delivered_cw or 0) or 0) / (row.delivered_cw or 1),
				"mileage": row.mileage
			})

		pi_doc=frappe.get_all("Vehicle Log", {"date": ["between", (filters.get("from_date"), filters.get("to_date"))], "license_plate": row.vehicle,'purchase_invoice':['is',"set"]}, pluck='purchase_invoice')
		freight = sum(frappe.get_list("Purchase Invoice",{"name":["in",pi_doc], 'purpose': ["!=", "Service"]}, pluck='ts_total_amount'))
		
		if (row.inward):
			inward_profit_loss += ((freight - (exp * (row.inward or 0) or 0)) or 0)
			inward_exp += (exp * (row.inward or 0)) or 0
			inward_freight += freight or 0
			inward_sqf += row.inward or 0
			rm.append({
				"vehicle": row.vehicle,
				"freight": freight,
				"expense": exp * (row.inward or 0),
				"sqft": row.inward,
				"profit_loss": freight - (exp * (row.inward or 0) or 0),
				"mileage": row.mileage
			})

	if paver:
		data.append({
			"vehicle": "PAVER",
			"bold": 1
		})
		data += paver
		data.append({
			"vehicle": "TOTAL",
			"expense": paver_exp,
			"sqft": paver_sqf,
			"sqft_cost": paver_sqf_cost,
			"bold": 1
		})
		data.append({
			"vehicle": "AVERAGE",
			"sqft": paver_exp / (paver_sqf or 1),
			"sqft_cost": paver_sqf_cost / len(paver),
			"bold": 1
		})
	if cw:
		if paver:
			data.append({})
		data.append({
			"vehicle": "COMPOUND WALL",
			"bold": 1
		})
		data += cw
		data.append({
			"vehicle": "TOTAL",
			"expense": cw_exp,
			"sqft": cw_sqf,
			"sqft_cost": cw_sqf_cost,
			"bold": 1
		})
		data.append({
			"vehicle": "AVERAGE",
			"sqft": cw_exp / (cw_sqf or 1),
			"sqft_cost": cw_sqf_cost / len(cw),
			"bold": 1
		})

	rental_sqft = get_rental_vehicle_sqft(filters=filters)
	rental_exp_details = get_rental_vehicle_expense(filters=filters)
	rental_exp = rental_exp_details.get("amount") or 0
	rental_exp_reference = rental_exp_details.get("reference") or []
	data.append({})
	data.append({
			"vehicle": "RENTAL VEHICLE",
			"bold": 1,
			"reference": json.dumps(rental_exp_reference)
		})
	for row in rental_sqft:
		exp = (rental_exp or 0) * (rental_sqft[row] or 0) / (sum(rental_sqft.values()) or 1)
		data.append({
			"vehicle": row,
			"expense": exp,
			"sqft": rental_sqft[row],
			"sqft_cost": (exp or 0) / (rental_sqft[row] or 1)
		})
	if len(rental_sqft) > 1:
		data.append({
			"vehicle": "TOTAL",
			"expense": rental_exp,
			"sqft": sum(rental_sqft.values()),
			"sqft_cost": (rental_exp or 0) / (sum(rental_sqft.values()) or 1),
			"bold": 1
		})

	if rm:
		data.append({})
		data.append({
			"vehicle": "INWARD",
			"bold": 1
		})
		data += rm
		data.append({
			"vehicle": "TOTAL",
			"freight": inward_freight,
			"expense": inward_exp,
			"sqft": inward_sqf,
			"profit_loss": inward_profit_loss,
			"bold": 1
		})
	return data

def get_rental_vehicle_sqft(filters, uom="SQF"):
	query = f"""
		select 
			sum(child.stock_qty*
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
				) as qty,
			child.item_group
		from `tabDelivery Note Item` child
		inner join `tabDelivery Note` parent
		on child.parent=parent.name and child.parenttype='Delivery Note'
		where
			parent.docstatus=1 and
			parent.posting_date between '{filters.get('from_date')}' and '{filters.get("to_date")}' and
			child.item_group in ("Pavers", "Compound Walls") and
			ifnull(parent.transporter, '') not in ("", "Own Transporter") and
			ifnull(parent.vehicle_no, "")!=""
		group by child.item_group
	"""

	res = frappe.db.sql(query=query, as_dict=True)
	sqf = {"PAVER": 0, "COMPOUND WALL": 0}
	for row in res:
		if row.get("item_group") == "Compound Walls":
			sqf["COMPOUND WALL"] += (row.get("qty")) or 0
		if row.get("item_group") == "Pavers":
			sqf["PAVER"] += (row.get("qty")) or 0

	return sqf

def get_rental_vehicle_expense(filters):
	return get_account_balance_on(
				account="TRANSPORT - GP", 
				company=erpnext.get_default_company(), 
				from_date=filters.get("from_date"), 
				to_date=filters.get("to_date"))

def get_account_balance_on(account, company, from_date, to_date):
	query=f"""
		select 
			*
		from `tabGL Entry` gl 
		where 
			gl.company='{company}' and
			gl.debit > 0 and
			ifnull(gl.expense_type, "")="" and
			date(gl.posting_date)>='{from_date}' and 
			date(gl.posting_date)<='{to_date}' and 
			gl.is_cancelled=0 and
			gl.account="{account}"
	"""
	gl_entries=frappe.db.sql(query, as_dict=True)
	res = {
		"reference": [{
			'doctype': gl.voucher_type,
			'docname': gl.voucher_no,
			'amount': gl.debit
		} for gl in gl_entries],
		"amount": sum([gl.get("debit") or 0 for gl in gl_entries])
	}
	return res
