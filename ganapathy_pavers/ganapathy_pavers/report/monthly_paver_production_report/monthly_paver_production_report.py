# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _
from ganapathy_pavers.custom.py.journal_entry import get_production_details

def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	item=filters.get("item")
	data = []

	paver_list = frappe.db.get_list("Material Manufacturing",filters={'from_time':["between",[from_date,to_date]],"item_to_manufacture":item },pluck="name")
	test_data = []

	if paver_list:
		condition=f" in {tuple(paver_list)}"
		if len(paver_list)==1:
			condition=f" = '{paver_list[0]}'"
		bom_item = frappe.db.sql(""" 
								select item_code,sum(qty),uom,avg(rate),sum(amount) from `tabBOM Item` where parent {0} group by item_code """.format(condition),as_list=1)
		production_qty = frappe.db.sql(""" 
								select sum(production_sqft) as production_sqft,
								item_to_manufacture as item_to_manufacture,
								avg(item_price) as item_price,
								sum(rack_shifting_total_expense1) as rack_shifting_total_expense1,
								sum(total_expense) as total_expense,
								sum(labour_expense) as labour_expense,
								avg(strapping_cost_per_sqft) as strapping_cost_per_sqft,
								avg(shot_blast_per_sqft) as shot_blast_per_sqft,
								sum(labour_cost_manufacture) as labour_cost_manufacture,
								sum(labour_cost_in_rack_shift) as labour_cost_in_rack_shift,
								sum(labour_cost_per_sqft) as labour_cost_per_sqft,
								sum(operators_cost_in_manufacture) as operators_cost_in_manufacture,
								sum(operators_cost_in_rack_shift) as operators_cost_in_rack_shift
								from `tabMaterial Manufacturing` where name  {0} """.format(condition),as_dict=1)

		
		
		test_data.append({
			"material":"-",
			"qty":f"<b>Item:</b> {production_qty[0]['item_to_manufacture']}",
			"sqft":f"<b>SQFT :</b> {production_qty[0]['production_sqft']:,.3f}",
			"uom":f"<b>Production Cost per SQFT :</b> ₹{production_qty[0]['item_price']:,.3f}",
			"rate":None,
			"amount":None,
			"cost_per_sqft":None
		})
		test_data.append({
			"material":None,
			"qty":None,
			"sqft":None,
			"uom":None,
			"rate":None,
			"amount":None,
			"cost_per_sqft":None
		})
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
			"material":None,
			"qty":None,
			"sqft":None,
			"uom":None,
			"rate":"<b>Total Production Cost</b>",
			"amount":f"<b>₹{production_qty[0]['rack_shifting_total_expense1'] + production_qty[0]['total_expense'] + production_qty[0]['labour_expense']:,.2f}</b>",
			"cost_per_sqft":f"<b>₹{total_cost_per_sqft:,.3f}</b>"
		})
		test_data.append({
			"material":None,
			"qty":None,
			"sqft":None,
			"uom":None,
			"rate":"<b>Total Labour Cost</b>",
	 		"amount":None,
			"cost_per_sqft":f"<b>₹{production_qty[0]['labour_cost_manufacture']/production_qty[0]['production_sqft'] + production_qty[0]['labour_cost_in_rack_shift']/production_qty[0]['production_sqft']+ production_qty[0]['labour_cost_per_sqft']:,.2f}</b>"
		})
		test_data.append({
			"material":None,
			"qty":None,
			"sqft":None,
			"uom":None,
			"rate":"<b>Total Operator Cost</b>",
	 		"amount":None,
			"cost_per_sqft":f"<b>₹{production_qty[0]['operators_cost_in_manufacture']/production_qty[0]['production_sqft'] + production_qty[0]['operators_cost_in_rack_shift']/production_qty[0]['production_sqft']:,.2f}</b>"
		})


		abstract_cost = {
				
				"Strapping Cost":production_qty[0]['strapping_cost_per_sqft'],
				"Shot Blasting Cost":production_qty[0]['shot_blast_per_sqft']}

		for cost in abstract_cost:
			test_data.append({
				"material":None,
				"qty":None,
				"consumption":None,
				"uom":None,
				"rate":f"<b>{cost}</b>",
				"amount":None,
				"cost_per_sqft":f"<b>₹{abstract_cost[cost]:,.2f}</b>"
			})

		if len(test_data) > 2:
			data += test_data
		total_sqf=0
		total_amt=0
		prod_details=get_production_details(from_date=filters.get('from_date'), to_date=filters.get('to_date'))
		if prod_details.get('paver'):
			exp, total_sqf, total_amt=get_expense_data(prod_details.get('paver'), filters, production_qty[0]['production_sqft'], total_sqf, total_amt)
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
					"sqft": f"<b style='background: rgb(242 140 140 / 81%)'>{round(total_sqf, 3)}</b>",
					"uom": f"<b style='background: rgb(242 140 140 / 81%)'>{round(total_amt, 3)}</b>"
				})
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
		]

	return columns

def get_expense_data(prod_sqft, filters, sqft, total_sqf, total_amt):
	exp=frappe.get_single("Expense Accounts")
	if not exp.paver_group:
		return [], 0, 0
	exp_tree=exp.tree_node(from_date=filters.get('from_date'), to_date=filters.get('to_date'), parent=exp.paver_group)
	res=[]
	for i in exp_tree:
		dic={}
		if i.get("expandable"):
			dic["material"]=i['value']
			child, total_sqf, total_amt=get_expense_from_child(prod_sqft, i['child_nodes'], sqft, total_sqf, total_amt)
			if child:
				res.append(dic)
				res+=child
				res+=group_total(child)
		else:
			if i["balance"]:
				dic={}
				if res:
					res.append({})
				dic['qty']=i['value']
				dic["sqft"]=round((i["balance"]/prod_sqft)*sqft, 3) if sqft else 0
				total_sqf+=(round((i["balance"]/prod_sqft)*sqft, 3) if sqft else 0)
				dic["uom"]=round(i["balance"]/prod_sqft, 3)
				total_amt+=(round(i["balance"]/prod_sqft, 3) or 0)
				res.append(dic)	
	return res, total_sqf, total_amt

def get_expense_from_child(prod_sqft, account, sqft, total_sqf, total_amt):
	res=[]
	for i in account:
		if i["balance"]:
			dic={}
			dic['qty']=i['value']
			dic["sqft"]=round((i["balance"]/prod_sqft)*sqft, 3) if sqft else 0
			total_sqf+=(round((i["balance"]/prod_sqft)*sqft, 3) if sqft else 0)
			dic["uom"]=round(i["balance"]/prod_sqft, 3)
			total_amt+=(round(i["balance"]/prod_sqft, 3) or 0)
			res.append(dic)
		if i['child_nodes']:
			res1, total_sqf, total_amt=(get_expense_from_child(i['child_nodes'], sqft, total_sqf, total_amt))
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
		'sqft': f"<b style='background: rgb(127 221 253 / 85%)'>{round(sqf, 3)}</b>",
		'uom': f"<b style='background: rgb(127 221 253 / 85%)'>{round(amt, 3)}</b>",
	})
	return res