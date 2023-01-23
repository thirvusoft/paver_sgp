# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None, _type=["Post", "Slab"]):
	columns = get_columns()

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	doc = frappe.get_all("CW Manufacturing", {"molding_date":["between", (from_date, to_date)],"type":["in",_type],"production_sqft":["!=",0],"docstatus":["!=",2]}, order_by = 'molding_date')
	days_count = {}
	data = {}

	if doc:
		labour_operator_cost=get_labour_operator_cost(doc)
		for doc_name in doc:		
			doc_details = frappe.get_doc("CW Manufacturing",doc_name.name)
			for material in doc_details.item_details:
				
				if(f'{doc_details.molding_date.strftime("%B")}{material.item}.+.+.+.{material.parent}' not in days_count):days_count[f'{doc_details.molding_date.strftime("%B")}{material.item}.+.+.+.{material.parent}'] = 1
				else:days_count[f'{doc_details.molding_date.strftime("%B")}{material.item}.+.+.+.{material.parent}'] += 1
				data_key=f"""{material.item}----{doc_details.molding_date.strftime("%B")}"""
				if data_key not in data:
					data[data_key]={
						"month": doc_details.molding_date.strftime("%B"),
						"item": material.item,
						"production_sqft": material.production_sqft,
						"no_of_days": None,
						"production_cost": None,
						"expense": get_expense_cost(doc),
						"labour_operator_cost": labour_operator_cost.get(data_key, {}).get("labour_operator_cost"),
						"total_cost_per_sqft": None,
					}
				else:
					data[data_key]["production_sqft"] += material.production_sqft

		data=list(data.values())
		
	days_count=sorted(days_count, key=lambda x:x)
	key = {i.split('.+.+.+.')[0]:0 for i in days_count}
	for i in days_count:
		key[i.split('.+.+.+.')[0]] += 1
	for i in data:
		i["no_of_days"] = key[i["month"]+i["item"]]
	return columns, data

def get_labour_operator_cost(doc_list):
	doc_list=[i.name for i in doc_list]
	query=f"""
	SELECT
		CONCAT(item.item, '----', MONTHNAME(cw.molding_date)) as data_key,
		count(item.item) as count,
		SUM(item.production_sqft),
		SUM(cw.total_labour_wages + cw.labour_expense_for_curing + cw.total_operator_wages)/SUM(cw.production_sqft)/2 as labour_operator_cost
	FROM `tabCW Manufacturing` cw
	LEFT OUTER JOIN 
		(
			SELECT
			cw_item.item,
			cw_item.parent,
			SUM(cw_item.production_sqft) as production_sqft
			from `tabCW Items` cw_item
			GROUP BY cw_item.item, cw_item.parent
		) item
	ON cw.name=item.parent
	where cw.name {f" in {tuple(doc_list)}" if len(doc_list)>1 else f" = '{doc_list[0]}'"}
	GROUP BY item.item, MONTHNAME(cw.molding_date)
	ORDER BY item.item
	"""

	res=frappe.db.sql(query, as_dict=True)
	ret={}
	for row in res:
		ret[row.get("data_key")]=row
	return ret

def get_expense_cost(doc_list):
	pass

def get_production_cost(doc_list):
	pass

def get_columns():

	columns = [
		{
			"fieldname":"month",
			"label":_("Month"),
			"width":100,
			"fieldtype":"Data"
		},
		{
			"fieldname":"item",
			"label":_("Item"),
			"width":300,
			"fieldtype":"Link",
			"options": "Item"
		},
		{
			"fieldname":"production_sqft",
			"label":_("Sqft"),
			"width":120,
			"fieldtype":"Float"
		},
		{
			"fieldname":"no_of_days",
			"label":_("No Of Days"),
			"width":120,
			"fieldtype":"Int"
		},
		{
			"fieldname":"production_cost",
			"label":_("Prod Cost"),
			"width":120,
			"fieldtype":"Currency"
		},
		{
			"fieldname":"labour_operator_cost",
			"label":_("Labour and Operator Cost"),
			"width":190,
			"fieldtype":"Currency"
		},
		{
			"fieldname":"expense",
			"label":_("Expense Cost"),
			"width":120,
			"fieldtype":"Currency"
		},
		{
			"fieldname":"total_cost_per_sqft",
			"label":_("Total Cost"),
			"width":120,
			"fieldtype":"Currency"
		}
	]

	return columns