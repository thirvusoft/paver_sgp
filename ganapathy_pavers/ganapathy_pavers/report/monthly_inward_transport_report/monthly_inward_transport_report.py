# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from ganapathy_pavers import uom_conversion
from ganapathy_pavers.custom.py.expense import  expense_tree

def execute(filters=None):
	columns = get_columns()
	data = []
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	vehicle_no = filters.get("vehicle_no")
	insurance_filter="INSURANCE"
	pending_due_filter="VEHICLE DUE"

	no_of_days=frappe.db.sql(""" select count(distinct(vl.date)) as days from `tabVehicle Log` vl where vl.select_purpose="Raw Material" and vl.date between '{0}' and '{1}' and vl.license_plate='{2}'  and docstatus=1 """.format(from_date,to_date,vehicle_no),as_dict=1) 
	no_of_trips=frappe.db.sql(""" select count(distinct(vl.name)) as trips from `tabVehicle Log` vl where vl.select_purpose="Raw Material" and vl.date between '{0}' and '{1}' and vl.license_plate='{2}'  and docstatus=1 """.format(from_date,to_date,vehicle_no),as_dict=1) 
	
	due_months=frappe.db.sql(""" select TIMESTAMPDIFF(MONTH,'{1}',md.to_date) as date from `tabMaintenance Details` md where parent='{0}' and md.maintenance='{2}'""".format(vehicle_no,from_date,pending_due_filter),as_dict=1) 
	insurance=frappe.db.sql(""" select TIMESTAMPDIFF(MONTH,'{1}',md.to_date) as date from `tabMaintenance Details` md where parent='{0}' and md.maintenance='{2}'""".format(vehicle_no,from_date,insurance_filter),as_dict=1) 
	days=no_of_days[0]["days"] if no_of_days else 0
	trips=no_of_trips[0]["trips"] if no_of_trips else 0
	
	due=due_months[0]["date"] if due_months else 0
	insurance=insurance[0]["date"] if insurance else 0

	doc = frappe.get_all("Vehicle Log", {"date": ["between", (from_date, to_date)], "license_plate": vehicle_no, "docstatus": 1}, ['name',
							'last_odometer', 'odometer', 'purchase_invoice', 'purchase_receipt', 'today_odometer_value'], order_by="date",)
	pi_doc=frappe.get_all("Vehicle Log", {"date": ["between", (from_date, to_date)], "license_plate": vehicle_no,'purchase_invoice':['is',"set"], "docstatus": 1}, pluck='purchase_invoice')
	start_km = 0
	end_km = 0
	mileage = 0
	try:
		mileage_doc= frappe.get_last_doc("Vehicle Log",{"date": ["between", (from_date, to_date)], "license_plate": vehicle_no,"mileage":['>',0]},order_by="date desc, creation desc")
		mileage = mileage_doc.mileage
	except:		
		try:
			mileage_doc= frappe.get_last_doc("Vehicle Log",{"date": ["<", from_date], "license_plate": vehicle_no,"mileage":['>',0]},order_by="date asc")
			mileage = mileage_doc.mileage
		except:
			pass

	invoice_grand_total = sum(frappe.get_list("Purchase Invoice",{"name":["in",pi_doc], 'purpose': ["!=", "Service"], 'docstatus': 1}, pluck='ts_total_amount'))
	if not invoice_grand_total:
		invoice_grand_total = 0
	
	if not doc:
		return columns, data
	start_km = (doc[0]["last_odometer"])
	end_km = (doc[-1]['odometer'])

	data.append({
		"item": f"Starting KM :{start_km}",
		"qty": f"End KM :{end_km}",
		"1": f"Total KM :{end_km-start_km}",
		"3": f"Mileage :{mileage}",
	})
	data.append({
		"item":f"No Of Days :{days}",
		"1":f"No Of Trips :{trips}",
			
	})
	data.append({
		"item":f"Insurance Due(Months) :{insurance}",
		"1":f"Vehicle Due(Months):{due}",	
	})

	data.append({})

	data.append({
		"item": "<b>Inward Report</b>",
	})

	data.append({
		"item": "<b>Item</b>",
		"qty": "<b>Total Load</b>",
		"1": "<b>Total Unit</b>",
	})

	pi_item=frappe.get_all("Purchase Invoice Item",{"parent":['in',pi_doc], "docstatus": 1},['item_code','count(item_code) as count','sum(stock_qty) as stock_qty','stock_uom'],group_by='item_code')
	
	from collections import Counter
	purchase_uom = Counter()
	purchase_count = Counter()
	purchase_qty = Counter()

	for d in pi_item:
		purchase_count[d['item_code']] += d['count']
		purchase_uom[d['item_code']] = d['stock_uom']
		purchase_qty[d['item_code']] += d['stock_qty']

 
	total_load =0
	total_unit= 0
	for j in purchase_count:
		total_load += purchase_count[j]
		total_unit += (round(uom_conversion(j, purchase_uom[j], purchase_qty[j], "Unit", False), 2))
		
		data.append({
			"item": j,
			"qty": purchase_count[j],
			"1": round(uom_conversion(j, purchase_uom[j], purchase_qty[j], "Unit", False), 2),
		})

	data.append({
		"item": "<b>Total</b>",
		"qty": f"{total_load}",
		"1": f"{total_unit}",
	})

	data.append({
		"item": "<b>Total Amount</b>",
		"1": f"<b>{invoice_grand_total or 0 }</b>",
	})

	data.append({})

	data.append({
		"item": "<b>Expenses Details</b>",
	})

	data.append({
		"item": "<b>Expenses Name</b>",
		"qty": "<b>Amount</b>",
		"1": "<b>Per Unit</b>",
	})

	# expense_details = frappe.db.sql(""" select child.maintenance as maintenance, sum(child.expense) as expense from `tabVehicle Log` as parent left outer join `tabMaintenance Details` as child on child.parent = parent.name where child.maintenance is not null and parent.date between '{0}' and '{1}' and parent.license_plate = '{2}' group by child.maintenance """.format(from_date,to_date,vehicle_no), as_dict= True)

	# total_amount = 0

	# for j in expense_details:
	# 	if total_unit:
	# 		total_amount += round(j['expense'],2)
	# 		continue
	# 		data.append({
	# 			"item": j['maintenance'],
	# 			"qty": round(j['expense'],2),
	# 			"1": round(j['expense']/total_unit,3),
	# 		})
	expense_details = get_expense_data(total_unit or 1, filters) or []
	total_amount=sum([i['qty'] for i in expense_details]) or 0
	total_per_unit=sum([i['1'] for i in expense_details])
	data += expense_details

	data.append({})

	data.append({
		"item": "<b>Total Amount</b>",
		"qty": f"<b>{round(total_amount, 2)}</b>",
		"1": f"{total_per_unit}",
	})

	data.append({
		"item": "<b>Difference</b>",
		"qty": f"<b>{round(((invoice_grand_total or 0)-(total_amount or 0)), 2)}</b>",
	})

	return columns, data

def get_expense_data(total_purchase_unit, filters):
	exp=frappe.get_single("Expense Accounts")
	if not exp.vehicle_expense:
		return []
	
	inward_km, delivered_km = frappe.db.sql(f"""
		select
			sum(case when ifnull(vl.purchase_invoice, '') != ''
				then ifnull(vl.today_odometer_value, 0)
				else 0
			end) as inward_km,
			sum(case when ifnull(vl.delivery_note, '') != ''
				then ifnull(vl.today_odometer_value, 0)
				else 0
			end) as delivered_km
		from `tabVehicle Log` vl
		where
			vl.license_plate = "{filters.get("vehicle_no")}" and
			vl.docstatus = 1 and
			vl.date between "{filters.get('from_date')}" and "{filters.get('to_date')}"
	""")[0] or (0, 0)
	
	if filters.get("new_method"):
		exp_tree=expense_tree(
							from_date=filters.get('from_date'),
							to_date=filters.get('to_date'),
							expense_type="Vehicle",
							vehicle=filters.get("vehicle_no")
							)
	else:
		exp_tree=exp.tree_node(from_date=filters.get('from_date'), to_date=filters.get('to_date'), parent=exp.vehicle_expense, vehicle=filters.get("vehicle_no"))
	res=[]
	for i in exp_tree:
		if i.get("expandable"):
			child=get_expense_from_child(total_purchase_unit, i['child_nodes'], inward_km, delivered_km)
			if child:
				res+=child
		else:
			if i["balance"]:
				i["balance"] *= inward_km / ((inward_km + delivered_km) or 1)
				res.append({
					"item": i['value'],
					"qty": i["balance"],
					"1": (i["balance"]/total_purchase_unit) or 0,
					"reference_data": json.dumps(i.get("references")) if i.get("references") else ""
				})	
	return res

def get_expense_from_child(total_purchase_unit, account, inward_km, delivered_km):
	res=[]
	for i in account:
		if i["balance"]:
			i["balance"] *= inward_km / ((inward_km + delivered_km) or 1)
			res.append({
				"item": i['value'],
				"qty": i["balance"],
				"1": (i["balance"]/total_purchase_unit) or 0,
				"reference_data": json.dumps(i.get("references")) if i.get("references") else ""
			})
		if i['child_nodes']:
			res1=(get_expense_from_child(total_purchase_unit, i['child_nodes'], inward_km, delivered_km))
			res+=res1
	return res

def get_columns():
	columns = [
		{
			"fieldname": "item",
			"label": _("<b>Item</b>"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 200
		},
		{
			"fieldname": "qty",
			"label": _("<b>Qty</b>"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "1",
			"label": _("<b>1</b>"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "2",
			"label": _("<b>2</b>"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "3",
			"label": _("<b>3</b>"),
			"fieldtype": "Data",
			"width": 150
		},
		{
            "label": _("Reference Data"),
            "fieldtype": "Data",
            "fieldname": "reference_data",
            "hidden": 1
        },
	]
	return columns
