# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt
 
import frappe
from frappe import _
from ganapathy_pavers.custom.py.journal_entry import get_production_details

def execute(filters=None, _type=["Post", "Slab"], exp_group="cw_group", prod="cw"):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	data = []

	cw_list = frappe.db.get_list("CW Manufacturing",filters={'molding_date':["between",[from_date,to_date]],'type':["in",_type]},pluck="name")
	test_data = []

	if cw_list:
		bom_item = frappe.db.sql(""" 
								select item_code,sum(qty),uom,avg(rate),sum(amount) from `tabBOM Item` where parent {0} group by item_code """.format(f" in {tuple(cw_list)}" if len(cw_list)>1 else f" = '{cw_list[0]}'"),as_list=1)
		production_qty = frappe.db.sql(""" 
								select sum(production_sqft) as production_sqft,
								avg(total_cost_per_sqft) as total_cost_per_sqft,
								sum(total_expence) as total_expence,
								sum(raw_material_cost) as raw_material_cost,
								sum(total_expense_for_unmolding) as total_expense_for_unmolding,
								sum(labour_expense_for_curing) as total_expense_for_curing,
								AVG(total_labour_wages + labour_expense_for_curing)/AVG(production_sqft) as labour_cost_per_sqft,
								AVG(total_operator_wages)/AVG(production_sqft) as operator_cost_per_sqft,
								avg(strapping_cost_per_sqft) as strapping_cost_per_sqft,
								avg(additional_cost_per_sqft) as additional_cost_per_sqft,
								avg(raw_material_cost_per_sqft) as raw_material_cost_per_sqft from `tabCW Manufacturing` where name {0}""".format(f" in {tuple(cw_list)}" if len(cw_list)>1 else f" = '{cw_list[0]}'"),as_dict=1)

		
		total_cost_per_sqft = 0
		for item in bom_item:
			total_cost_per_sqft += item[4] / production_qty[0]['production_sqft']


		test_data.append({
			"material":"-",
			"qty":"-",
			"consumption":f"<b>SQFT :</b> {production_qty[0]['production_sqft']:,.3f}",
			"uom":f"<b>Production Cost per SQFT :</b> ₹{(production_qty[0]['total_cost_per_sqft'] - production_qty[0]['raw_material_cost_per_sqft'] + total_cost_per_sqft):,.3f}",
			"rate":None,
			"amount":None,
			"cost_per_sqft":None
		})
		test_data.append({
			"material":None,
			"qty":None,
			"consumption":None,
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
				"consumption":f"{item[1] / production_qty[0]['production_sqft']:,.3f}",
				"uom":item[2],
				"rate":f'₹{item[3]:,.2f}',
				"amount":f'₹{item[4]:,.2f}',
				"cost_per_sqft":f"₹{item[4] / production_qty[0]['production_sqft']:,.3f}",
			})
			total_cost_per_sqft += item[4] / production_qty[0]['production_sqft']
		
		test_data.append({
			"material":None,
			"qty":None,
			"consumption":None,
			"uom":None,
			"rate":"<b>Total Production Cost</b>",
			"amount": f"<b>₹{production_qty[0]['raw_material_cost']:,.2f}</b>",
			# "amount":f"<b>₹{production_qty[0]['total_expence'] + production_qty[0]['total_expense_for_unmolding'] + production_qty[0]['total_expense_for_curing']:,.2f}</b>",
			"cost_per_sqft":f"<b>₹{total_cost_per_sqft:,.3f}</b>"
		})

		abstract_cost = {#"Total Raw Material Cost":production_qty[0]['raw_material_cost_per_sqft'],
				"Total Labour Cost":production_qty[0]["labour_cost_per_sqft"],
				"Total Operator Cost":production_qty[0]['operator_cost_per_sqft'],
				"<span style='color:rgb(255 82 0);'>Labour and Operator Cost</span>": f"""<b style='color:rgb(255 82 0);'>₹{(((production_qty[0]["labour_cost_per_sqft"] or 0) + (production_qty[0]['operator_cost_per_sqft'] or 0))):,.2f}</b>""",
				"Total Strapping Cost":production_qty[0]['strapping_cost_per_sqft'],
				"Total Additional Cost":production_qty[0]['additional_cost_per_sqft']}

		for cost in abstract_cost:
			test_data.append({
				"material":None,
				"qty":None,
				"consumption":None,
				"uom":None,
				"rate":f"<b>{cost}</b>",
				"amount":None,
				"cost_per_sqft":f"<b>₹{abstract_cost[cost]:,.2f}</b>" if isinstance(abstract_cost[cost], int) or isinstance(abstract_cost[cost], float) else abstract_cost[cost]
			})

		if len(test_data) > 2:
			data += test_data
		total_sqf=0
		total_amt=0
		prod_details=get_production_details(from_date=filters.get('from_date'), to_date=filters.get('to_date'))
		if prod_details.get(prod):
			exp, total_sqf, total_amt=get_expense_data(prod_details.get(prod),filters, (production_qty[0]['production_sqft']), total_sqf, total_amt, exp_group)
			if exp:
				data.append({
					"material":"<b style='background: rgb(242 140 140 / 81%)'>Expense Details</b>"
				})
				data.append({
					"material":"<b style='background: rgb(242 140 140 / 81%)'>Expense Type</b>",
					"qty": "<b style='background: rgb(242 140 140 / 81%)'>Expense</b>",
					"consumption": "<b style='background: rgb(242 140 140 / 81%)'>Per Sqft</b>",
					"uom": "<b style='background: rgb(242 140 140 / 81%)'>Amount</b>"
				})
				data+=exp
				data.append({})
				data.append({
					"qty": "<b style='background: rgb(242 140 140 / 81%)'>Total</b>",
					"consumption": f"<b style='background: rgb(242 140 140 / 81%)'>{round(total_sqf, 4)}</b>",
					"uom": f"<b style='background: rgb(242 140 140 / 81%)'>{round(total_amt, 4)}</b>"
				})
		if data and len(data)>0:
			data[0]['uom']=f"""<b>Production Cost per SQFT :</b> ₹{(production_qty[0]['strapping_cost_per_sqft'] + production_qty[0]['additional_cost_per_sqft'] + total_cost_per_sqft + round(total_sqf, 4) + (((production_qty[0]["labour_cost_per_sqft"] or 0) + (production_qty[0]['operator_cost_per_sqft'] or 0)))):,.3f}"""
	columns = get_columns()
	return columns, data
 
def get_columns():
	columns = [{
		"fieldtype":"Link",
		"fieldname":"material",
		"label":"<b>Date</b>",
		"width":150,
		"options":"Item"
		},
		{
		"fieldtype":"Data",
		"fieldname":"qty",
		"label":"<b>QTY</b>",
		"width":150
		},
		{
		"fieldtype":"Data",
		"fieldname":"consumption",
		"label":"<b>Consumption</b>",
		"width":160
		},
		{
		"fieldtype":"Data",
		"fieldname":"uom",
		"label":"<b>UOM</b>",
		"width":250
		},
		{
		"fieldtype":"Data",
		"fieldname":"rate",
		"label":"<b>Rate</b>",
		"width":230
		},
		{
		"fieldtype":"Data",
		"fieldname":"amount",
		"label":"<b>Amount</b>",
		"width":150
		},
		{
		"fieldtype":"Data",
		"fieldname":"cost_per_sqft",
		"label":"<b>Cost Per SQFT</b>",
		"width":100
		}
	
	
	]
	
	return columns


def get_expense_data(prod_sqft, filters, sqft, total_sqf, total_amt, exp_group):
	exp=frappe.get_single("Expense Accounts")
	if not exp.get(exp_group):
		return [], 0, 0
	exp_tree=exp.tree_node(from_date=filters.get('from_date'), to_date=filters.get('to_date'), parent=exp.get(exp_group))
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
				dic["uom"]=round(i["balance"], 4)
				total_amt+=(dic["uom"] or 0)
				dic["consumption"]=round(i["balance"]/prod_sqft, 4)
				total_sqf+=(dic["consumption"] or 0)
				res.append(dic)	
	return res, total_sqf, total_amt

def get_expense_from_child(prod_sqft, account, sqft, total_sqf, total_amt):
	res=[]
	for i in account:
		if i["balance"]:
			dic={}
			dic['qty']=i['value']
			dic["uom"]=round(i["balance"], 4)
			total_amt+=(dic["uom"] or 0)
			dic["consumption"]=round(i["balance"]/prod_sqft, 4)
			total_sqf+=(dic["consumption"] or 0)
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
		sqf+=(i.get('consumption') or 0)
		amt+=(i.get('uom') or 0)
	res.append({
		'qty': "<b style='background: rgb(127 221 253 / 85%)'>Group Total</b>",
		'consumption': f"<b style='background: rgb(127 221 253 / 85%)'>{round(sqf, 4)}</b>",
		'uom': f"<b style='background: rgb(127 221 253 / 85%)'>{round(amt, 4)}</b>",
	})
	return res