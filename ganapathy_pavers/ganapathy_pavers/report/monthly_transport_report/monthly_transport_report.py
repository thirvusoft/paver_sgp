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

	doc = frappe.get_all("Vehicle Log", {"date": ["between", (from_date, to_date)], "license_plate": vehicle_no, "docstatus": 1, "select_purpose": ["not in", ["Fuel", "Service"]]}, [
							'last_odometer', 'odometer', 'delivery_note', 'sales_invoice', 'today_odometer_value'], order_by="date",)
	dn_doc=frappe.get_all("Vehicle Log", {"date": ["between", (from_date, to_date)], "license_plate": vehicle_no,'delivery_note':['is','set'], "docstatus": 1, "select_purpose": ["not in", ["Fuel", "Service"]]}, pluck='delivery_note')
	si_doc=frappe.get_all("Vehicle Log", {"date": ["between", (from_date, to_date)], "license_plate": vehicle_no,'sales_invoice':['is','set'], "docstatus": 1, "select_purpose": ["not in", ["Fuel", "Service"]]}, pluck='sales_invoice')
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

	data.append({
		"item":f"Starting KM :{start_km}",
		"1":f"End KM :{end_km}",
		"3":f"Total KM :{end_km-start_km}"
	})

	data.append({
		"item":f"Paver KM :{pavers_km}",
		"1":f"CW KM :{cw_km}",
		"3":"Total Sqrft :"
	})

	if  transport_based_on == "Report":
		data.append({
			"item":"<b>Pavers Report</b>"
		})
	else:
		data.append({})
		

	if  transport_based_on == "Report":
		data.append({
			"item":"<b>Item</b>",
			"qty":"<b>Total pavers</b>",
			"1":"<b>Total Sqrft</b>"
		})


	dn_item=frappe.get_all("Delivery Note Item",{"parent":['in',dn_doc], "docstatus": 1},['item_code','item_group','sum(stock_qty) as stock_qty', 'stock_uom'],group_by='item_code')
	si_item=frappe.get_all("Sales Invoice Item",{"parent":['in',si_doc], "docstatus": 1},['item_code','item_group','sum(stock_qty) as stock_qty', 'stock_uom'],group_by='item_code')

	si_qty = lambda item_code: sum([i['stock_qty'] for i in si_item if(i['item_code']==item_code)])

	pavers_total=0
	for j in dn_item:
		if j.item_group=="Pavers":
			pavers_total+=(round(uom_conversion(j.item_code,j.stock_uom,j.stock_qty+si_qty(j.item_code),"SQF"),2))

		
			if transport_based_on == "Report":
				data.append({
					"item":j.item_code,
					"qty":round(uom_conversion(j.item_code,j.stock_uom,j.stock_qty+si_qty(j.item_code),"Nos"),2),
					"1":round(uom_conversion(j.item_code,j.stock_uom,j.stock_qty+si_qty(j.item_code),"SQF"),2),
				})
	
	if  transport_based_on == "Report":
		data.append({
			"qty":"<b>Total Sqrft :</b>",
			"1":f"<b>{pavers_total}</b>"
		})
		
		
	else:
		data.append({
			"item":"<b>Pavers Sqrft :</b>",
			"1":f"<b>{pavers_total}</b>"
		})
		
	if  transport_based_on == "Report":
		data.append({})
	

				
	if  transport_based_on == "Report":
		data.append({
			"item":"<b>Compound Wall Report</b>",
		})
	

	if  transport_based_on == "Report":
		data.append({
			"item":"<b>Item</b>",
			"qty":"<b>Total Qty</b>",
			"1":"<b>Total Sqrft</b>"
		})
		
	
	cw_total=0
	for j in dn_item:
		if j.item_group=="Compound Walls":
			cw_total+=round(uom_conversion(j.item_code,j.stock_uom,j.stock_qty+si_qty(j.item_code),"SQF"),2)
	
			if  transport_based_on == "Report":
				data.append({
					"item":j.item_code,
					"qty":round(uom_conversion(j.item_code,j.stock_uom,j.stock_qty+si_qty(j.item_code),"Nos"),2),
					"1":round(uom_conversion(j.item_code,j.stock_uom,j.stock_qty+si_qty(j.item_code),"SQF"),2),
				})
	
				
	
	if  transport_based_on == "Report":
		data.append({
			"qty":"<b>Total Sqrft :</b>",
			"1":f"<b>{cw_total}</b>"
		})
	
	else:
		data.append({
			"item":"<b>Compund Wall Total Sqrft :</b>",
			"1":f"<b>{cw_total}</b>",
		})
		
	data.append({})

	if  transport_based_on == "Report":
		data.append({
			"item":"<b>Others</b>",	
		})
		
		data.append({
			"item":"<b>Item</b>",
			"qty":"<b>Qty</b>",
			"1":"<b>Uom</b>"
	    })

		for j in dn_item:
			if j.item_group not in ["Compound Walls" , "Pavers"]:
				data.append({
					"item":j.item_code,
					"qty":round(j.stock_qty,2),
					"1":j.stock_uom
				})
				
		data.append({})

	total_sqft = 0
	if pavers_total or cw_total:
		total_sqft = pavers_total + cw_total
		data[1]["3"] = data[1]["3"] + str(pavers_total + cw_total)
    
	data.append({
		"item":"<b>Expenses Details</b>"
	})

	data.append({
		"item":"<b>Expenses Name</b>",
		"qty":"<b>Amount</b>",
		"1":"<b>Per Sqrft</b>",
		"2":"<b>Amount Pavers</b> ",
		"3":"<b>Amount CW</b>"
	})
	

	expense_details = frappe.db.sql(""" select child.maintenance as maintenance, sum(child.expense) as expense from `tabVehicle Log` as parent left outer join `tabMaintenance Details` as child on child.parent = parent.name where child.maintenance is not null and parent.date between '{0}' and '{1}' and parent.license_plate = '{2}' group by child.maintenance """.format(from_date,to_date,vehicle_no), as_dict= True)

	total_amt_pavers = 0
	total_amt_cw = 0

	for j in expense_details:
		if total_sqft:
			total_amt_pavers += round((pavers_total / total_sqft)*j['expense'],2)
			total_amt_cw += round((cw_total / total_sqft)*j['expense'],2)
			continue
			data.append({
				"item":j['maintenance'],
				"qty":round(j['expense'],2),
				"1":round(j['expense']/total_sqft,3),
				"2":round((pavers_total / total_sqft)*j['expense'],2),
				"3":round((cw_total / total_sqft)*j['expense'],2)
			})

	expense_details = get_expense_data((pavers_total+cw_total) or 1, filters, pavers_total, cw_total, ((pavers_km or 0) + (cw_km or 0)), pavers_km, cw_km)
	# if transport_based_on=="Report":
	data+=(expense_details)
	paver_total_amount=round(sum([i["2"] or 0 for i in expense_details]), 2)
	cw_total_amount=round(sum([i["3"] or 0 for i in expense_details]), 2)

	data.append({})

	data.append({
		"item":"<b>Total Amount</b>",
		"qty":f'<b>{round(sum([i["qty"] or 0 for i in expense_details]), 2)}</b>',
		"1":f'<b>{round(sum([i["1"] or 0 for i in expense_details]), 2)}</b>',
		"2":f'<b>{paver_total_amount}</b>',
		"3":f'<b>{cw_total_amount}</b>'
	})

	data.append({
		"item":"<b>Total SQFT</b>",
		"2":f'<b>{pavers_total}</b>',
		"3":f'<b>{cw_total}</b>'
	})

	data.append({
		"item":"<b>Total Cost</b>",
		"2":f'<b>{round(((paver_total_amount/pavers_total) if pavers_total else 0), 2)}</b>',
		"3":f'<b>{round(((cw_total_amount/cw_total) if cw_total else 0), 2)}</b>'
	})

	return columns, data


def get_columns():
	columns = [
        {
            "label": _("<b>Item</b>"),
            "fieldtype": "Link",
            "fieldname": "item",
            "options":"Item",
            "width": 250
        },
        {
            "label": _("<b>Qty</b>"),
            "fieldtype": "Data",
            "fieldname": "qty",
            "width": 250
        },
		 {
            "label": _("<b>1</b>"),
            "fieldtype": "Data",
            "fieldname": "1",
            "width": 150
        },
		 {
            "label": _("<b>2</b>"),
            "fieldtype": "Data",
            "fieldname": "2",
            "width": 150
        },
		 {
            "label": _("<b>3</b>"),
            "fieldtype": "Data",
            "fieldname": "3",
            "width": 150
        },
	]
	return columns

def get_expense_data(total_delivery_sqft, filters, paver_sqft, cw_sqft, total_km, paver_km, cw_km):
	exp=frappe.get_single("Expense Accounts")
	if not exp.vehicle_expense:
		return []
	exp_tree=exp.tree_node(from_date=filters.get('from_date'), to_date=filters.get('to_date'), parent=exp.vehicle_expense, vehicle=filters.get("vehicle_no"))
	res=[]
	vehicle=None
	if filters.get("vehicle_no"):
		vehicle=frappe.get_doc("Vehicle", filters.get("vehicle_no"))
	
	for i in exp_tree:
		is_km_exp=0
		paver=paver_sqft
		cw=cw_sqft
		total=total_delivery_sqft

		if i.get("expandable"):
			child=get_expense_from_child(total_delivery_sqft, i['child_nodes'], paver_sqft, cw_sqft, total_km, paver_km, cw_km, filters)
			if child:
				res+=child
		else:
			for md in vehicle.maintanence_details_:
				if md.default_expense_account == i['value'] and md.expense_calculation_per_km:
					total=(total_km)
					paver=paver_km
					cw=cw_km
					is_km_exp=1

			if i["balance"]:
				res.append({
					"item": i['value'],
					"qty": i["balance"],
					"1": (i["balance"]/total) or 0,
					"2": (i["balance"])*(paver/total) or 0,
					"3": (i["balance"])*(cw/total) or 0,
					"is_km_exp": is_km_exp,
				})	
	return res

def get_expense_from_child(total_delivery_sqft, account, paver_sqft, cw_sqft, total_km, paver_km, cw_km, filters):
	vehicle=None
	if filters.get("vehicle_no"):
		vehicle=frappe.get_doc("Vehicle", filters.get("vehicle_no"))

	res=[]
	total=total_delivery_sqft
	paver=paver_sqft
	cw=cw_sqft
	for i in account:
		paver=paver_sqft
		cw=cw_sqft
		total=total_delivery_sqft
		is_km_exp=0
		if i["balance"]:
			if vehicle:
				for md in vehicle.maintanence_details_:
					if md.default_expense_account == i['value'] and md.expense_calculation_per_km:
						total=(total_km)
						paver=paver_km
						cw=cw_km
						is_km_exp=1

			res.append({
				"item": i['value'],
				"qty": i["balance"],
				"1": (i["balance"]/total) or 0,
				"2": (i["balance"])*(paver/total) or 0,
				"3": (i["balance"])*(cw/total) or 0,
				"is_km_exp": is_km_exp,
			})
		if i['child_nodes']:
			res1=(get_expense_from_child(total_delivery_sqft, i['child_nodes'], paver_sqft, cw_sqft, total_km, paver_km, cw_km, filters))
			res+=res1
	return res
