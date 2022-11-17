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
	mileage = frappe.db.sql(""" select avg(mileage) as mileage from `tabVehicle Log` where purchase_receipt is not null or purchase_invoice is not null""",as_dict=True)

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

	sub_list = []
	sub_list.append(f"Starting KM :{start_km}")
	sub_list.append(f"End KM :{end_km}")
	sub_list.append(f"Total KM :{end_km-start_km}")
	sub_list.append("")
	sub_list.append(f"Mileage :{mileage[0]['mileage']}")

	data.append(sub_list)

	sub_list = []
	sub_list.append("<b>Inward Report</b>")
	sub_list.append("")
	sub_list.append("")
	sub_list.append("")
	sub_list.append("")
	data.append(sub_list)

	sub_list = []
	sub_list.append("<b>Item</b>")
	sub_list.append("<b>Total Load</b>")
	sub_list.append("<b>Total Unit</b>")
	sub_list.append("")
	sub_list.append("")
	data.append(sub_list)

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
		sub_list = []
		sub_list.append(j)
		sub_list.append(purchase_count[j])
		total_load += purchase_count[j]
		sub_list.append(round(uom_conversion(j,purchase_uom[j],purchase_qty[j],"Unit"),2))
		total_unit += (round(uom_conversion(j,purchase_uom[j],purchase_qty[j],"Unit"),2))
		sub_list.append("")
		sub_list.append("")
		data.append(sub_list)
	sub_list = []
	sub_list.append("<b>Total</b>")
	sub_list.append(f"{total_load}")
	sub_list.append(f"{total_unit}")
	sub_list.append("")
	sub_list.append("")
	data.append(sub_list)

	sub_list = []
	sub_list.append("<b>Total Amount</b>")
	sub_list.append("")
	sub_list.append(f"<b>{receipt_grand_total[0]+invoice_grand_total[0] }</b>")
	sub_list.append("")
	sub_list.append("")
	data.append(sub_list)

	sub_list = []
	sub_list.append("")
	sub_list.append("")
	sub_list.append("")
	sub_list.append("")
	sub_list.append("")
	data.append(sub_list)

	sub_list = []
	sub_list.append("<b>Expenses Details</b>")
	sub_list.append("")
	sub_list.append("")
	sub_list.append("")
	sub_list.append("")
	data.append(sub_list)

	sub_list = []
	sub_list.append("<b>Expenses Name</b>")
	sub_list.append("<b>Amount</b>")
	sub_list.append("<b>Per Unit</b>")
	sub_list.append("")
	sub_list.append("")
	data.append(sub_list)

	expense_details = frappe.db.sql(""" select child.maintenance as maintenance, sum(child.expense) as expense from `tabVehicle Log` as parent left outer join `tabMaintenance Details` as child on child.parent = parent.name where child.maintenance is not null and parent.date between '{0}' and '{1}' and parent.license_plate = '{2}' group by child.maintenance """.format(from_date,to_date,vehicle_no), as_dict= True)

	total_amount = 0

	for j in expense_details:
		if total_unit:
			sub_list = []
			sub_list.append(j['maintenance'])
			sub_list.append(round(j['expense'],2))
			total_amount += round(j['expense'],2)
			sub_list.append(round(j['expense']/total_unit,3))
			sub_list.append("")
			sub_list.append("")
			data.append(sub_list)

	sub_list = []
	sub_list.append("")
	sub_list.append("")
	sub_list.append("")
	sub_list.append("")
	sub_list.append("")
	data.append(sub_list)


	sub_list = []
	sub_list.append("<b>Total Amount</b>")
	sub_list.append("")
	sub_list.append(f"<b>{total_amount}</b>")
	sub_list.append("")
	sub_list.append("")
	data.append(sub_list)

	sub_list = []
	sub_list.append("<b>Profit</b>")
	sub_list.append("")
	sub_list.append(f"<b>{(receipt_grand_total[0]+invoice_grand_total[0])-total_amount}</b>")
	sub_list.append("")
	sub_list.append("")
	data.append(sub_list)


	return columns, data


def get_columns():
	columns = [
		_("<b>Item</b>") + ":Link/Item:150",
		_("<b>Qty</b>") + ":Data:150",
		_("<b>1</b>") + ":Data:150",
		_("<b>2</b>") + ":Data:150",
		_("<b>3</b>") + ":Data:150",
	]
	return columns
