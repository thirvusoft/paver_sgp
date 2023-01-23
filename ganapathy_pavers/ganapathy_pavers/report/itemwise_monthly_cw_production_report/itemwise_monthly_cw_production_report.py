# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

from ganapathy_pavers.custom.py.journal_entry import get_production_details
import frappe
from frappe import _
from ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing import uom_conversion


def execute(filters=None, _type=["Post", "Slab"], prod_exp_sqft="cw", exp_group="cw_group"):
	columns = get_columns()

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	doc = frappe.get_all("CW Manufacturing", {"molding_date":["between", (from_date, to_date)],"type":["in",_type],"production_sqft":["!=",0],"docstatus":["!=",2]}, order_by = 'molding_date')
	data = []

	if doc:
		data = get_cw_cost(doc)
	sqf_exp=get_sqft_expense(filters, exp_group)
	prod_details=get_production_details(from_date=filters.get('from_date'), to_date=filters.get('to_date'), machines=filters.get("machine", []))
	for row in  data:
    row['pieces']=uom_conversion(item=row['item'], from_uom="SQF", from_qty=row['production_sqft'], to_uom="Nos")
		row["expense"]=sqf_exp/prod_details.get(prod_exp_sqft, 1)
		row['total_cost_per_sqft']=(row.get("labour_operator_cost", 0) or 0)+(row.get("prod_cost", 0) or 0)+(row.get("strapping_cost", 0) or 0)+(row.get("additional_cost", 0) or 0)+(row.get("expense", 0) or 0)
	return columns, data

def get_cw_cost(doc_list):
	doc_list=[i.name for i in doc_list]
	query=f"""
	SELECT
		MONTHNAME(cw.molding_date) as month,
		item.item,
		sum(item.production_sqft) as production_sqft,
		COUNT(item.item) as no_of_days,
		CONCAT(item.item, '----', MONTHNAME(cw.molding_date)) as data_key,
		SUM((cw.total_labour_wages + cw.labour_expense_for_curing + cw.total_operator_wages)*item.production_sqft/cw.production_sqft)/SUM(item.production_sqft)/2 as labour_operator_cost,
		SUM(cw.raw_material_cost*item.production_sqft/cw.production_sqft)/SUM(item.production_sqft) as prod_cost,
		AVG(strapping_cost_per_sqft) as strapping_cost,
		AVG(additional_cost_per_sqft) as additional_cost
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
	return res

def get_sqft_expense(filters, exp_group):
	exp=frappe.get_single("Expense Accounts")
	paver_exp_tree=exp.tree_node(from_date=filters.get('from_date'), to_date=filters.get('to_date'), parent=exp.get(exp_group))
	total_sqf=0
	for i in paver_exp_tree:
		if i.get("child_nodes"):
			total_sqf+=get_expense_from_child(i['child_nodes'], 0)
		else:
			if i["balance"]:
				total_sqf+=i["balance"] or 0
	return total_sqf

def get_expense_from_child(account, total_sqf):
	for i in account:
		if i['child_nodes']:
			total_sqf+=(get_expense_from_child(i['child_nodes'], 0))
		elif i["balance"]:
			total_sqf+=i["balance"] or 0
	return total_sqf

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
		_("pieces") + ":Float:100",
		{
			"fieldname":"no_of_days",
			"label":_("No Of Days"),
			"width":120,
			"fieldtype":"Int"
		},
		{
			"fieldname":"prod_cost",
			"label":_("Prod Cost(Raw Material)"),
			"width":150,
			"fieldtype":"Currency"
		},
		{
			"fieldname":"labour_operator_cost",
			"label":_("Labour and Operator Cost"),
			"width":190,
			"fieldtype":"Currency"
		},
		{
			"fieldname":"strapping_cost",
			"label":_("Strapping Cost"),
			"width":120,
			"fieldtype":"Currency"
		},
		{
			"fieldname":"additional_cost",
			"label":_("Additional Cost"),
			"width":120,
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