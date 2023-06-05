# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

# import frappe
import frappe
import json
from frappe import _
from ganapathy_pavers.custom.py.journal_entry import get_production_details
from ganapathy_pavers.custom.py.expense import  expense_tree

def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	item=filters.get("item")
	data = []
	filters1={'from_time':["between",[from_date,to_date]] }
	if filters.get("machine"):
		filters1["work_station"] = ["in", filters.get("machine", [])]
	lo_paver_list=frappe.db.get_list("Material Manufacturing", filters1,pluck="name")

	lo_paver_list=frappe.db.get_list("Material Manufacturing", filters1,pluck="name")

	lo_paver_list=frappe.db.get_list("Material Manufacturing", filters1,pluck="name")
	
	if item:
		filters1["item_to_manufacture"]=item
	paver_list = frappe.db.get_list("Material Manufacturing", filters1,pluck="name")
	test_data = []

	if paver_list:
		lo_condition=f" in {tuple(lo_paver_list)}"
		condition=f" in {tuple(paver_list)}"
		if len(paver_list)==1:
			condition=f" = '{paver_list[0]}'"
		if len(lo_paver_list)==1:
			lo_condition=f" = '{lo_paver_list[0]}'"
		bom_item = frappe.db.sql(""" 
								select item_code,sum(qty),uom,avg(rate),sum(amount) from `tabBOM Item` where parent {0} group by item_code """.format(condition),as_list=1)
		production_qty = frappe.db.sql(""" 
								select sum(total_production_sqft) as production_sqft,
								item_to_manufacture as item_to_manufacture,
								avg(item_price) as item_price,
								sum(rack_shifting_total_expense1) as rack_shifting_total_expense1,
								sum(total_raw_material) as total_raw_material,
								sum(total_expense) as total_expense,
								sum(labour_expense) as labour_expense,
								avg(strapping_cost_per_sqft) as strapping_cost_per_sqft,
								avg(shot_blast_per_sqft) as shot_blast_per_sqft,
								(
									SELECT SUM(labour_cost_manufacture+labour_cost_in_rack_shift+labour_expense)
									from `tabMaterial Manufacturing`
									WHERE name {1}
								) as labour_cost,
								(
									SELECT SUM(operators_cost_in_manufacture+operators_cost_in_rack_shift)
									from `tabMaterial Manufacturing`
									WHERE name {1}
								) as operator_cost
								from `tabMaterial Manufacturing` where name  {0} """.format(condition, lo_condition),as_dict=1)

		

		test_data.append({
			"material":"-",
			"qty":f"""<b>Item:</b> {production_qty[0]['item_to_manufacture']}"""   if filters.get("item") else "",
			"sqft":f"<b>SQFT :</b> {production_qty[0]['production_sqft']:,.3f}",
			"uom":f"<b>Production Cost per SQFT :</b> ₹{production_qty[0]['item_price']:,.3f}",
		})
		test_data.append({})
		total_cost_per_sqft = 0
		for item in bom_item:
			test_data.append({
				"material":item[0],
				"qty":float(item[1]),
				"sqft":f"{item[1] / production_qty[0]['production_sqft']:,.3f}",
				"uom":item[2],
				"rate":f'₹{item[3]:,.2f}',
				"amount":f'₹{item[4]:,.2f}',
				"cost_per_sqft":f"₹{item[4] / production_qty[0]['production_sqft']:,.3f}",
			})
			total_cost_per_sqft += item[4] / production_qty[0]['production_sqft']

		test_data.append({
			"rate":"<b>Production Cost</b>",
			"amount":f"<b>₹{production_qty[0]['total_raw_material']:,.2f}</b>",
			"cost_per_sqft":f"<b>₹{total_cost_per_sqft:,.3f}</b>"
		})

		abstract_cost = {
				"Strapping Cost":production_qty[0]['strapping_cost_per_sqft'],
				"Shot Blasting Cost":production_qty[0]['shot_blast_per_sqft']
		}

		for cost in abstract_cost:
			test_data.append({
				"rate":f"<b>{cost}</b>",
				"cost_per_sqft":f"<b>₹{abstract_cost[cost]:,.2f}</b>"
			})
		production_cost_per_sqft= (
				total_cost_per_sqft+
				sum([abstract_cost[cost] or 0 for cost in abstract_cost]))

		test_data.append({
			"rate":"<b style='color:rgb(255 82 0);'>Total Production Cost</b>",
			"cost_per_sqft":f"""<b style='color:rgb(255 82 0);'>₹{(production_cost_per_sqft):,.3f}</b>"""
		})

		if test_data and len(test_data)>0:
				test_data[0]["uom"] = f"<b>Production Cost per SQFT :</b> ₹{(production_cost_per_sqft or 0):,.3f}"
		
		if len(test_data) > 2:
			data += test_data
		total_sqf=0
		total_amt=0
		prod_details=get_production_details(from_date=filters.get('from_date'), to_date=filters.get('to_date'), machines=filters.get("machine", []), item=filters.get("item"))
		prod_details=get_production_details(from_date=filters.get('from_date'), to_date=filters.get('to_date'), machines=filters.get("machine", []))
		prod_details=get_production_details(from_date=filters.get('from_date'), to_date=filters.get('to_date'), machines=filters.get("machine", []), item=filters.get("item"))
		if prod_details.get('paver'):
			labour_exp = {
				"value": "Labour & Operator",
				"account_name": "Labour & Operator",
				"expandable": 1,
				"balance": 0,
				"child_nodes": [
					{
						"value": "Labour Expense",
						"account_name": "Labour Expense",
						"expandable": 0,
						"balance": production_qty[0]["labour_cost"],
						"child_nodes": []
					},
					{
						"value": "Operator Expense",
						"account_name": "Operator Expense",
						"expandable": 0,
						"balance": production_qty[0]["operator_cost"],
						"child_nodes": []
					}
				]
			}
			exp, total_sqf, total_amt=get_expense_data(prod_details.get('paver'), filters, production_qty[0]['production_sqft'], total_sqf, total_amt, labour_exp)
			if exp:
				data.append({
					"material":"<b style='background: rgb(242 140 140 / 81%)'>Expense Details</b>"
				})
				data.append({
					"material":"<b style='background: rgb(242 140 140 / 81%)'>Expense Type</b>",
					"qty": "<b style='background: rgb(242 140 140 / 81%)'>Expense</b>",
					"sqft": "<b style='background: rgb(242 140 140 / 81%)'>Per Sqft</b>",
					"uom": "<b style='background: rgb(242 140 140 / 81%)'>Amount</b>"
				})
				data+=exp
				data.append({})
				data.append({
					"qty": "<b style='background: rgb(242 140 140 / 81%)'>Total</b>",
					"sqft": f"<b style='background: rgb(242 140 140 / 81%)'>{round(total_sqf, 4)}</b>",
					"uom": f"<b style='background: rgb(242 140 140 / 81%)'>{round(total_amt, 4)}</b>"
				})
				if data and len(data)>0:
					data[0]["uom"] = f"<b>Production Cost per SQFT :</b> ₹{((production_cost_per_sqft or 0)+(total_sqf or 0)):,.3f}"
	columns = get_columns()
	return columns, data

def get_columns():
	columns = [
		_("Material") + ":Link/Item:150",
		_("QTY") + ":Data:200",
		_("Sqft") + ":Data:200",
		_("UOM") + ":Link/UOM:250",
		_("Rate") + ":Data:200",
		_("Amount") + ":Data:150",
		_("Cost Per SQFT") + ":Data:100",
		{
			"fieldname": "reference_data",
			"label": "Reference Data",
			"fieldtype": "Data",
			"hidden": 1,
		}
		]

	return columns

def get_expense_data(prod_sqft, filters, sqft, total_sqf, total_amt, labour_exp=[]):
	machine=None
	if ("Machine1" in filters.get("machine", []) or "Machine2" in filters.get("machine", [])) and "Machine3 Day" in filters.get("machine", []):
		pass
	elif "Machine1" in filters.get("machine", []) or "Machine2" in filters.get("machine", []):
		machine="machine_12"
	elif filters.get("machine", []):
		machine="machine_3"
	if filters.get("new_method"):
		exp_tree=expense_tree(
							from_date=filters.get('from_date'),
							to_date=filters.get('to_date'),
							prod_details="Paver",
							expense_type="Manufacturing",
							machine = filters.get("machine", []) or [],
							vehicle_summary = filters.get("vehicle_summary")
							)
	else:
		exp=frappe.get_single("Expense Accounts")
		if not exp.paver_group:
			return [], 0, 0
		exp_tree=exp.tree_node(from_date=filters.get('from_date'), to_date=filters.get('to_date'), parent=exp.paver_group, machine=machine )
	
	exp_tree.append(labour_exp)
	res=[]
	for i in exp_tree:
		dic={}
		if i.get("expandable"):
			dic["material"]=i['value']
			child, total_sqf, total_amt=get_expense_from_child(prod_sqft, i['child_nodes'], sqft, total_sqf, total_amt)
			if child:
				res.append(dic)
				if not filters.get("expense_summary"):
					res+=child
				res+=group_total(child)
		else:
			if i["balance"]:
				dic={}
				if res:
					res.append({})
				dic['qty']=i['value']
				dic["sqft"]=(round(i["balance"]/prod_sqft, 4) or 0)
				total_sqf+=(round(i["balance"]/prod_sqft, 4) or 0)
				dic["uom"]=(round((i["balance"]/prod_sqft)*sqft, 4) if prod_sqft else 0)
				total_amt+=(round((i["balance"]/prod_sqft)*sqft, 4) if prod_sqft else 0)
				dic["reference_data"]=json.dumps(i.get("references")) if i.get("references") else ""
				res.append(dic)	
	return res, total_sqf, total_amt

def get_expense_from_child(prod_sqft, account, sqft, total_sqf, total_amt):
	res=[]
	for i in account:
		if i["balance"]:
			dic={}
			dic['qty']=i['value']
			dic["sqft"]=(round(i["balance"]/prod_sqft, 4) or 0)
			total_sqf+=(round(i["balance"]/prod_sqft, 4) or 0)
			dic["uom"]=(round((i["balance"]/prod_sqft)*sqft, 4) if prod_sqft else 0)
			total_amt+=(round((i["balance"]/prod_sqft)*sqft, 4) if prod_sqft else 0)
			dic["reference_data"]=json.dumps(i.get("references")) if i.get("references") else ""
			res.append(dic)
		if i['child_nodes']:
			res1, total_sqf, total_amt=(get_expense_from_child(prod_sqft, i['child_nodes'], sqft, total_sqf, total_amt))
			res+=res1
	return res, total_sqf, total_amt

def group_total(child):
	res=[]
	sqf=0
	amt=0
	for i in child:
		sqf+=(i.get('sqft') or 0)
		amt+=(i.get('uom') or 0)
	res.append({
		'qty': "<b style='background: rgb(127 221 253 / 85%)'>Group Total</b>",
		'sqft': f"<b style='background: rgb(127 221 253 / 85%)'>{round(sqf, 4)}</b>",
		'uom': f"<b style='background: rgb(127 221 253 / 85%)'>{round(amt, 4)}</b>",
	})
	return res