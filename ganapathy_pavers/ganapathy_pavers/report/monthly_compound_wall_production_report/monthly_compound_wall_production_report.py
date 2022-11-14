# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt
 
import frappe
from frappe import _

def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	data = []

	cw_list = frappe.db.get_list("CW Manufacturing",filters={'molding_date':["between",[from_date,to_date]],'type':["!=","Fencing Post"]},pluck="name")
	test_data = []

	if cw_list:
		bom_item = frappe.db.sql(""" 
								select item_code,sum(qty),uom,avg(rate),sum(amount) from `tabBOM Item` where parent in {0} group by item_code """.format(tuple(cw_list)),as_list=1)
		production_qty = frappe.db.sql(""" 
								select sum(production_sqft) as production_sqft,
								avg(total_cost_per_sqft) as total_cost_per_sqft,
								sum(total_expence) as total_expence,
								sum(total_expense_for_unmolding) as total_expense_for_unmolding,
								sum(labour_expense_for_curing) as total_expense_for_curing,
								sum(labour_cost_per_sqft) as labour_cost_per_sqft,
								sum(operator_cost_per_sqft) as operator_cost_per_sqft,
								sum(strapping_cost_per_sqft) as strapping_cost_per_sqft,
								sum(additional_cost_per_sqft) as additional_cost_per_sqft,
								sum(raw_material_cost_per_sqft) as raw_material_cost_per_sqft from `tabCW Manufacturing` where name in {0} """.format(tuple(cw_list)),as_dict=1)

		test_data.append({
			"material":"-",
			"qty":"-",
			"consumption":f"<b>SQFT FT :</b> {production_qty[0]['production_sqft']:,.3f}",
			"uom":f"<b>Production Cost per SQFT :</b> ₹{production_qty[0]['total_cost_per_sqft']:,.3f}",
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
			"amount":f"<b>₹{production_qty[0]['total_expence'] + production_qty[0]['total_expense_for_unmolding'] + production_qty[0]['total_expense_for_curing']:,.2f}</b>",
			"cost_per_sqft":f"<b>₹{total_cost_per_sqft:,.3f}</b>"
		})

		abstract_cost = {"Total Raw Material Cost":production_qty[0]['raw_material_cost_per_sqft'],
				"Total Labour Cost":production_qty[0]["labour_cost_per_sqft"],
				"Total Operator Cost":production_qty[0]['operator_cost_per_sqft'],
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
				"cost_per_sqft":f"<b>₹{abstract_cost[cost]:,.2f}</b>"
			})

	if len(test_data) > 2:
		data += test_data
	columns = get_columns()
	return columns, data
 
def get_columns():
	columns = [
		_("Material") + ":Link/Item:150",
		_("QTY") + ":Data:150",
		_("Consumption") + ":Data:200",
		_("UOM") + ":Link/UOM:250",
		_("Rate") + ":Data:200",
		_("Amount") + ":Data:150",
		_("Cost Per SQFT") + ":Data:100",
		]
	
	return columns
