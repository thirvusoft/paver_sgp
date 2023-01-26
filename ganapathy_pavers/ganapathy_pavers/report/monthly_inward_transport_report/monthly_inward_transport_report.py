# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from ganapathy_pavers import uom_conversion

def execute(filters=None):
	columns = get_columns()
	data = []
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	vehicle_no = filters.get("vehicle_no")

	doc = frappe.get_all("Vehicle Log", {"date": ["between", (from_date, to_date)], "license_plate": vehicle_no}, ['name',
							'last_odometer', 'odometer', 'purchase_invoice', 'purchase_receipt', 'today_odometer_value'], order_by="date",)
	pr_doc=frappe.get_all("Vehicle Log", {"date": ["between", (from_date, to_date)], "license_plate": vehicle_no,'purchase_receipt':['is',"set"]}, pluck='purchase_receipt')
	pi_doc=frappe.get_all("Vehicle Log", {"date": ["between", (from_date, to_date)], "license_plate": vehicle_no,'purchase_invoice':['is',"set"]}, pluck='purchase_invoice')
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

	receipt_grand_total = frappe.get_list("Purchase Receipt",{"name":["in",pr_doc]},['sum(grand_total) as grand_total'],pluck="grand_total")
	invoice_grand_total = frappe.get_list("Purchase Invoice",{"name":["in",pi_doc]},['sum(grand_total) as grand_total'],pluck="grand_total")

	if not receipt_grand_total[0]:
		receipt_grand_total=[0]
	if not invoice_grand_total[0]:
		invoice_grand_total = [0]
	
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
	data.append({})

	data.append({
		"item": "<b>Inward Report</b>",
	})

	data.append({
		"item": "<b>Item</b>",
		"qty": "<b>Total Load</b>",
		"1": "<b>Total Unit</b>",
	})

	pr_item=frappe.get_all("Purchase Receipt Item",{"parent":['in',pr_doc],"uom":"Unit"},['item_code','count(item_code) as count','sum(stock_qty) as stock_qty','stock_uom'],group_by='item_code')
	pi_item=frappe.get_all("Purchase Invoice Item",{"parent":['in',pi_doc],"uom":"Unit"},['item_code','count(item_code) as count','sum(stock_qty) as stock_qty','stock_uom'],group_by='item_code')
	

	from collections import Counter
	purchase_uom = Counter()
	purchase_count = Counter()
	purchase_qty = Counter()
	for d in pr_item:
		purchase_count[d['item_code']] += d['count']
		purchase_uom[d['item_code']] = d['stock_uom']
		purchase_qty[d['item_code']] += d['stock_qty']

	for d in pi_item:
		purchase_count[d['item_code']] += d['count']
		purchase_uom[d['item_code']] = d['stock_uom']
		purchase_qty[d['item_code']] += d['stock_qty']

 
	total_load =0
	total_unit= 0
	for j in purchase_count:
		total_load += purchase_count[j]
		total_unit += (round(uom_conversion(j,purchase_uom[j],purchase_qty[j],"Unit"),2))
		
		data.append({
			"item": j,
			"qty": purchase_count[j],
			"1": round(uom_conversion(j,purchase_uom[j],purchase_qty[j],"Unit"),2),
		})

	data.append({
		"item": "<b>Total</b>",
		"qty": f"{total_load}",
		"1": f"{total_unit}",
	})

	data.append({
		"item": "<b>Total Amount</b>",
		"1": f"<b>{receipt_grand_total[0]+invoice_grand_total[0] }</b>",
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

	expense_details = frappe.db.sql(""" select child.maintenance as maintenance, sum(child.expense) as expense from `tabVehicle Log` as parent left outer join `tabMaintenance Details` as child on child.parent = parent.name where child.maintenance is not null and parent.date between '{0}' and '{1}' and parent.license_plate = '{2}' group by child.maintenance """.format(from_date,to_date,vehicle_no), as_dict= True)

	total_amount = 0

	for j in expense_details:
		if total_unit:
			total_amount += round(j['expense'],2)
			continue
			data.append({
				"item": j['maintenance'],
				"qty": round(j['expense'],2),
				"1": round(j['expense']/total_unit,3),
			})
	expense_details = get_expense_data(total_unit or 1, filters) or []
	total_amount=sum([i['qty'] for i in expense_details])
	data += expense_details

	data.append({})

	data.append({
		"item": "<b>Total Amount</b>",
		"1": f"<b>{total_amount}</b>",
	})

	data.append({
		"item": "<b>Profit</b>",
		"1": f"<b>{(receipt_grand_total[0]+invoice_grand_total[0])-total_amount}</b>",
	})

	return columns, data

def get_expense_data(total_purchase_unit, filters):
	exp=frappe.get_single("Expense Accounts")
	if not exp.vehicle_expense:
		return [], 0, 0
	exp_tree=exp.tree_node(from_date=filters.get('from_date'), to_date=filters.get('to_date'), parent=exp.vehicle_expense, vehicle=filters.get("vehicle_no"))
	res=[]
	for i in exp_tree:
		if i.get("expandable"):
			child=get_expense_from_child(total_purchase_unit, i['child_nodes'])
			if child:
				if not filters.get("expense_summary"):
					res+=child
		else:
			if i["balance"]:
				res.append({
					"item": i['value'],
					"qty": i["balance"],
					"1": (i["balance"]/total_purchase_unit) or 0,
				})	
	return res

def get_expense_from_child(total_purchase_unit, account):
	res=[]
	for i in account:
		if i["balance"]:
			res.append({
				"item": i['value'],
				"qty": i["balance"],
				"1": (i["balance"]/total_purchase_unit) or 0,
			})
		if i['child_nodes']:
			res1=(get_expense_from_child(total_purchase_unit, i['child_nodes']))
			res+=res1
	return res

def get_columns():
	columns = [
		{
			"fieldname": "item",
			"label": _("<b>Item</b>"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname": "qty",
			"label": _("<b>Qty</b>"),
			"fieldtype": "Data",
		},
		{
			"fieldname": "1",
			"label": _("<b>1</b>"),
			"fieldtype": "Data",
		},
		{
			"fieldname": "2",
			"label": _("<b>2</b>"),
			"fieldtype": "Data",
		},
		{
			"fieldname": "3",
			"label": _("<b>3</b>"),
			"fieldtype": "Data",
		},
	]
	return columns
