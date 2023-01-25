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
	transport_based_on = filters.get("transport_based_on")

	doc = frappe.get_all("Vehicle Log", {"date": ["between", (from_date, to_date)], "license_plate": vehicle_no}, [
							'last_odometer', 'odometer', 'delivery_note', 'sales_invoice', 'today_odometer_value'], order_by="date",)
	dn_doc=frappe.get_all("Vehicle Log", {"date": ["between", (from_date, to_date)], "license_plate": vehicle_no,'delivery_note':['is','set']}, pluck='delivery_note')
	si_doc=frappe.get_all("Vehicle Log", {"date": ["between", (from_date, to_date)], "license_plate": vehicle_no,'sales_invoice':['is','set']}, pluck='sales_invoice')
	start_km = 0
	end_km = 0
	pavers_km = 0
	cw_km = 0

	if not doc:
		return columns, data
	start_km = (doc[0]["last_odometer"])
	end_km = (doc[-1]['odometer'])

	for i in doc:
		if i.delivery_note:
			dn_type = frappe.get_value(
				"Delivery Note", i.delivery_note, 'type')
			if dn_type == "Pavers":
				pavers_km += i['today_odometer_value']
			elif dn_type == "Compound Wall":
				cw_km += i['today_odometer_value']

		elif i.sales_invoice:
			si_type = frappe.get_value(
				"Sales Invoice", i.sales_invoice, 'type')
			if si_type == "Pavers":
				pavers_km += i['today_odometer_value']
			elif si_type == "Compound Wall":
				cw_km += i['today_odometer_value']

	sub_list = []
	sub_list.append(f"Starting KM :{start_km}")
	sub_list.append("")
	sub_list.append(f"End KM :{end_km}")
	sub_list.append("")
	sub_list.append(f"Total KM :{pavers_km + cw_km}")
	data.append(sub_list)

	sub_list = []
	sub_list.append(f"Paver KM :{pavers_km}")
	sub_list.append("")
	sub_list.append(f"CW KM :{cw_km}")
	sub_list.append("")
	sub_list.append("Total Sqrft :")
	data.append(sub_list)
	if  transport_based_on == "Report":
		sub_list = []
		sub_list.append("<b>Pavers Report</b>")
		sub_list.append("")
		sub_list.append("")
		sub_list.append("")
		sub_list.append("")
		data.append(sub_list)
	else:
		sub_list = []
		sub_list.append("")
		sub_list.append("")
		sub_list.append("")
		sub_list.append("")
		sub_list.append("")
		data.append(sub_list)

	if  transport_based_on == "Report":
		sub_list = []
		sub_list.append("<b>Item</b>")
		sub_list.append("<b>Total pavers</b>")
		sub_list.append("<b>Total Sqrft</b>")
		sub_list.append("")
		sub_list.append("")
		data.append(sub_list)

	dn_item_list=[]
	si_item_list=[]
	dn_item=frappe.get_all("Delivery Note Item",{"parent":['in',dn_doc]},['item_code','item_group','sum(stock_qty) as stock_qty', 'stock_uom'],group_by='item_code')
	si_item=frappe.get_all("Sales Invoice Item",{"parent":['in',si_doc]},['item_code','item_group','sum(stock_qty) as stock_qty', 'stock_uom'],group_by='item_code')

	si_qty = lambda item_code: sum([i['stock_qty'] for i in si_item if(i['item_code']==item_code)])

	pavers_total=0
	for j in dn_item:
		if j.item_group=="Pavers":
			sub_list = []
			sub_list.append(j.item_code)
			sub_list.append(round(uom_conversion(j.item_code,j.stock_uom,j.stock_qty+si_qty(j.item_code),"Nos"),2))
			sub_list.append(round(uom_conversion(j.item_code,j.stock_uom,j.stock_qty+si_qty(j.item_code),"SQF"),2))
			pavers_total+=(round(uom_conversion(j.item_code,j.stock_uom,j.stock_qty+si_qty(j.item_code),"SQF"),2))
			sub_list.append("")
			sub_list.append("")
			if transport_based_on == "Report":
				data.append(sub_list)
	
	if  transport_based_on == "Report":
		sub_list = []
		sub_list.append("")
		sub_list.append("<b>Total Sqrft :</b>")
		sub_list.append(f"<b>{pavers_total}</b>")
		sub_list.append("")
		sub_list.append("")
		data.append(sub_list)
		
	else:
		sub_list = []
		sub_list.append("<b>Pavers Sqrft :</b>")
		sub_list.append("")
		sub_list.append(f"<b>{pavers_total}</b>")
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
				
	if  transport_based_on == "Report":
		sub_list = []
		sub_list.append("<b>Compound Wall Report</b>")
		sub_list.append("")
		sub_list.append("")
		sub_list.append("")
		sub_list.append("")
		data.append(sub_list)

	if  transport_based_on == "Report":
		sub_list = []
		sub_list.append("<b>Item</b>")
		sub_list.append("<b>Total Qty</b>")
		sub_list.append("<b>Total Sqrft</b>")
		sub_list.append("")
		sub_list.append("")
		data.append(sub_list)
	
	cw_total=0
	for j in dn_item:
		if j.item_group=="Compound Walls":
			sub_list = []
			sub_list.append(j.item_code)
			sub_list.append(round(uom_conversion(j.item_code,j.stock_uom,j.stock_qty+si_qty(j.item_code),"Nos"),2))
			sub_list.append(round(uom_conversion(j.item_code,j.stock_uom,j.stock_qty+si_qty(j.item_code),"SQF"),2))
			cw_total+=round(uom_conversion(j.item_code,j.stock_uom,j.stock_qty+si_qty(j.item_code),"SQF"),2)
			sub_list.append("")
			sub_list.append("")
			if  transport_based_on == "Report":
				data.append(sub_list)
	
	if  transport_based_on == "Report":
		sub_list = []
		sub_list.append("")
		sub_list.append("<b>Total Sqrft :</b>")
		sub_list.append(f"<b>{cw_total}</b>")
		sub_list.append("")
		sub_list.append("")
		data.append(sub_list)
	else:
		sub_list = []
		sub_list.append("<b>Compund Wall Total Sqrft :</b>")
		sub_list.append("")
		sub_list.append(f"<b>{cw_total}</b>")
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

	if  transport_based_on == "Report":

		sub_list = []
		sub_list.append("<b>Others</b>")
		sub_list.append("")
		sub_list.append("")
		sub_list.append("")
		sub_list.append("")
		data.append(sub_list)

		sub_list = []
		sub_list.append("<b>Item</b>")
		sub_list.append("<b>Qty</b>")
		sub_list.append("<b>Uom</b>")
		sub_list.append("")
		sub_list.append("")
		data.append(sub_list)

		for j in dn_item:
			if j.item_group not in ["Compound Walls" , "Pavers"]:
				sub_list = []
				sub_list.append(j.item_code)
				sub_list.append(round(j.stock_qty,2))
				sub_list.append(j.stock_uom)
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

	total_sqft = 0
	if pavers_total or cw_total:
		total_sqft = pavers_total + cw_total
		data[1][4] = data[1][4] + str(pavers_total + cw_total)

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
	sub_list.append("<b>Per Sqrft</b>")
	sub_list.append("<b>Amount Pavers</b>")
	sub_list.append("<b>Amount CW</b>")
	data.append(sub_list)

	expense_details = frappe.db.sql(""" select child.maintenance as maintenance, sum(child.expense) as expense from `tabVehicle Log` as parent left outer join `tabMaintenance Details` as child on child.parent = parent.name where child.maintenance is not null and parent.date between '{0}' and '{1}' and parent.license_plate = '{2}' group by child.maintenance """.format(from_date,to_date,vehicle_no), as_dict= True)

	total_amt_pavers = 0
	total_amt_cw = 0

	for j in expense_details:
		if total_sqft:
			sub_list = []
			sub_list.append(j['maintenance'])
			sub_list.append(round(j['expense'],2))
			sub_list.append(round(j['expense']/total_sqft,3))
			sub_list.append(round((pavers_total / total_sqft)*j['expense'],2))
			total_amt_pavers += round((pavers_total / total_sqft)*j['expense'],2)
			sub_list.append(round((cw_total / total_sqft)*j['expense'],2))
			total_amt_cw += round((cw_total / total_sqft)*j['expense'],2)
			# data.append(sub_list)

	expense_details = get_expense_data((pavers_total+cw_total) or 1, filters, pavers_total, cw_total)
	data+=(expense_details)
	paver_total_amount=round(sum([i[3] or 0 for i in expense_details]), 2)
	cw_total_amount=round(sum([i[4] or 0 for i in expense_details]), 2)

	sub_list = []
	sub_list.append(i.maintanence)
	sub_list.append("")
	sub_list.append("")
	sub_list.append("")
	sub_list.append("")
	data.append(sub_list)

	sub_list = []
	sub_list.append("<b>Total Amount</b>")
	sub_list.append(f'<b>{round(sum([i[1] or 0 for i in expense_details]), 2)}</b>')
	sub_list.append(f'<b>{round(sum([i[2] or 0 for i in expense_details]), 2)}</b>')
	sub_list.append(f'<b>{paver_total_amount}</b>')
	sub_list.append(f'<b>{cw_total_amount}</b>')
	data.append(sub_list)

	sub_list = []
	sub_list.append("<b>Total SQFT</b>")
	sub_list.append("")
	sub_list.append("")
	sub_list.append(f'<b>{pavers_total}</b>')
	sub_list.append(f'<b>{cw_total}</b>')
	data.append(sub_list)

	sub_list = []
	sub_list.append("<b>Total Cost</b>")
	sub_list.append("")
	sub_list.append("")
	sub_list.append(f'<b>{round(paver_total_amount/pavers_total,2) if pavers_total else "0.0"}</b>')
	sub_list.append(f'<b>{round(cw_total_amount/cw_total,2) if cw_total else "0.0"}</b>')
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

def get_expense_data(total_delivery_sqft, filters, paver_sqft, cw_sqft):
	exp=frappe.get_single("Expense Accounts")
	if not exp.vehicle_expense:
		return [], 0, 0
	exp_tree=exp.tree_node(from_date=filters.get('from_date'), to_date=filters.get('to_date'), parent=exp.vehicle_expense, vehicle=filters.get("vehicle_no"))
	res=[]
	for i in exp_tree:
		if i.get("expandable"):
			child=get_expense_from_child(total_delivery_sqft, i['child_nodes'], paver_sqft, cw_sqft)
			if child:
				if not filters.get("expense_summary"):
					res+=child
		else:
			if i["balance"]:
				sub_list=[]
				
				sub_list.append(i['value'])
				sub_list.append(i["balance"])
				sub_list.append((i["balance"]/total_delivery_sqft) or 0)
				sub_list.append((i["balance"])*(paver_sqft/total_delivery_sqft) or 0)
				sub_list.append((i["balance"])*(cw_sqft/total_delivery_sqft) or 0)

				res.append(sub_list)	
	return res

def get_expense_from_child(total_delivery_sqft, account, paver_sqft, cw_sqft):
	res=[]
	for i in account:
		if i["balance"]:
			sub_list=[]
			
			sub_list.append(i['value'])
			sub_list.append(i["balance"])
			sub_list.append((i["balance"]/total_delivery_sqft) or 0)
			sub_list.append((i["balance"])*(paver_sqft/total_delivery_sqft) or 0)
			sub_list.append((i["balance"])*(cw_sqft/total_delivery_sqft) or 0)

			res.append(sub_list)
		if i['child_nodes']:
			res1=(get_expense_from_child(i['child_nodes'], paver_sqft, cw_sqft))
			res+=res1
	return res
