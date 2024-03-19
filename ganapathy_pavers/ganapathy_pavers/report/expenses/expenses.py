# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import json
import frappe
from ganapathy_pavers.custom.py.expense import  expense_tree
from ganapathy_pavers.custom.py.journal_entry import get_ITEM_TYPES
WORKSTATIONS = {}

def execute(filters=None):
	ITEM_TYPES = get_ITEM_TYPES()
	columns, data = get_columns(filters, ITEM_TYPES), get_data(filters, ITEM_TYPES)
	return columns, data

def get_columns(filters, ITEM_TYPES):
	WORKSTATIONS = frappe.get_all("Workstation", filters={"used_in_expense_splitup": 1}, fields=["name", "location"], order_by="name",)
	columns = [
		{
			"fieldname": "expense_group",
			"fieldtype": "Data",
			"label": "Expense Group",
			"width": 150
		},
		{
			"fieldname": "expense",
			"fieldtype": "Data",
			"label": "Expense",
			"width": 250
		},
		{
			"fieldname": "total_amount",
			"fieldtype": "Currency",
			"label": "Total Amount",
			"width": 150
		},
		*[
			{
				"fieldname": frappe.scrub(i_type),
				"fieldtype": "Currency",
				"label": i_type,
				"width": 100,
				"hidden": filters.get("expense_type") == "Vehicle"
			}
			for i_type in ITEM_TYPES
		],
		{
			"fieldname": "group_total",
			"fieldtype": "Check",
			"hidden": 1,
		},
		{
			"fieldname": "total",
			"fieldtype": "Check",
			"hidden": 1,
		},
		{
			"fieldname": "reference_data",
			"fieldtype": "Data",
			"hidden": 1,
		}
	]
	if filters.get("all_machines"):
		for wrk in WORKSTATIONS:
			columns.append({
				"fieldname": frappe.scrub(wrk.name),
				"fieldtype": "Currency",
				"label": wrk.name,
				"width": 100,
				"hidden": filters.get("expense_type") == "Vehicle"
			})
	else:
		location = []
		for wrk in WORKSTATIONS:
			if wrk.location and wrk.location in location:
				continue
			elif wrk.location:
				location.append(wrk.location)
			columns.append({
				"fieldname": frappe.scrub(wrk.location or wrk.name),
				"fieldtype": "Currency",
				"label": wrk.location or wrk.name,
				"width": 100,
				"hidden": filters.get("expense_type") == "Vehicle"
			})
	return columns

def get_data(filters, ITEM_TYPES):
	WORKSTATIONS = frappe.get_all("Workstation", filters={"used_in_expense_splitup": 1}, fields=["name", "location"], order_by="name")

	total_amount = {
		"total_amount": 0,
		**{
			frappe.scrub(i_type): 0
			for i_type in ITEM_TYPES
		}
	}
	for wrk in WORKSTATIONS:
		total_amount[frappe.scrub(wrk.name or "")] = 0
		if wrk.location:
			total_amount[frappe.scrub(wrk.location)] = 0

	exp_tree=expense_tree(
				from_date=filters.get('from_date'),
				to_date=filters.get('to_date'),
				expense_type=filters.get("expense_type"),
				vehicle_summary=filters.get("vehicle_summary"),
				all_expenses=True
			)
	exp_tree+=get_labour_operator_expense(filters)
	res=[]
	for i in exp_tree:
		dic={}
		if i.get("expandable"):
			dic["expense_group"]=i['value']
			child, total_amount=get_expense_from_child(account=i['child_nodes'], WORKSTATIONS=WORKSTATIONS, total_amount=total_amount, ITEM_TYPES=ITEM_TYPES)
			if child:
				res.append(dic)
				if not filters.get("expense_summary"):
					res+=child
				res+=group_total(child, WORKSTATIONS, ITEM_TYPES)
		else:
			if i["balance"]:
				dic={}
				if res:
					res.append({})
				
				dic['expense']=i.get('value')
				dic['paver']=0
				for i_type in ITEM_TYPES:
					if (frappe.scrub(i_type)) != "paver":
						dic[frappe.scrub(i_type)] = i.get(frappe.scrub(i_type))
						total_amount[frappe.scrub(i_type)]+=i.get(frappe.scrub(i_type)) or 0
					
				total_amount['total_amount']+=i.get('balance') or 0

				for wrk in WORKSTATIONS:
					dic['paver'] += i.get(frappe.scrub(wrk.name)) or 0
					total_amount['paver'] += i.get(frappe.scrub(wrk.name)) or 0

					total_amount[frappe.scrub(wrk.name)] += i.get(frappe.scrub(wrk.name)) or 0
					dic[frappe.scrub(wrk.name)] = i.get(frappe.scrub(wrk.name)) or 0

					if wrk.location:
						total_amount[frappe.scrub(wrk.location)] += i.get(frappe.scrub(wrk.name)) or 0
						if not dic.get(frappe.scrub(wrk.location)):
							dic[frappe.scrub(wrk.location)] = 0
						dic[frappe.scrub(wrk.location)] += i.get(frappe.scrub(wrk.name)) or 0

				dic["total_amount"]=i.get("balance") or 0
				dic["reference_data"]=json.dumps(i.get("references")) if i.get("references") else ""
				
				res.append(dic)	
	res.append({})
	total_amount["expense"] = "Total"
	total_amount["total"] = 1
	res.append(total_amount)

	return res

def get_expense_from_child(account, WORKSTATIONS, total_amount, ITEM_TYPES):
	res=[]
	for i in account:
		if i["balance"]:
			dic={}

			dic['expense']=i.get('value')
			dic['paver']=0
			for i_type in ITEM_TYPES:
				if (frappe.scrub(i_type)) != "paver":
					dic[frappe.scrub(i_type)] = i.get(frappe.scrub(i_type))
					total_amount[frappe.scrub(i_type)]+=i.get(frappe.scrub(i_type)) or 0

			total_amount['total_amount']+=i.get('balance') or 0

			for wrk in WORKSTATIONS:
				dic['paver'] += i.get(frappe.scrub(wrk.name)) or 0
				total_amount['paver'] += i.get(frappe.scrub(wrk.name)) or 0

				total_amount[frappe.scrub(wrk.name)] += i.get(frappe.scrub(wrk.name)) or 0
				dic[frappe.scrub(wrk.name)] = i.get(frappe.scrub(wrk.name)) or 0

				if wrk.location:
					total_amount[frappe.scrub(wrk.location)] += i.get(frappe.scrub(wrk.name)) or 0
					if not dic.get(frappe.scrub(wrk.location)):
						dic[frappe.scrub(wrk.location)] = 0
					dic[frappe.scrub(wrk.location)] += i.get(frappe.scrub(wrk.name)) or 0

			dic["total_amount"]=i["balance"] or 0
			dic["reference_data"]=json.dumps(i.get("references")) if i.get("references") else ""
			
			res.append(dic)
		if i['child_nodes']:
			res1, total_amount=get_expense_from_child(account=i['child_nodes'], WORKSTATIONS=WORKSTATIONS, total_amount=total_amount, ITEM_TYPES=ITEM_TYPES)
			res+=res1
	return res, total_amount

def group_total(child, WORKSTATIONS, ITEM_TYPES):
	res=[]
	total_amount=0
	total = {frappe.scrub(i_type):0 for i_type in ITEM_TYPES}
	for i in child:
		for i_type in ITEM_TYPES:
			total[frappe.scrub(i_type)] += (i.get(frappe.scrub(i_type)) or 0)
		total_amount+=(i.get('total_amount') or 0)
	group = {
		'expense': "Group Total",
		'total_amount': total_amount or 0,
		**{
			frappe.scrub(i_type): total.get(frappe.scrub(i_type)) or 0
			for i_type in ITEM_TYPES
		},
		"group_total": 1
	}
	for wrk in WORKSTATIONS:
		group[frappe.scrub(wrk.name)] = sum([i.get(frappe.scrub(wrk.name)) for i in child])
		if wrk.location:
			group[frappe.scrub(wrk.location)] = sum([i.get(frappe.scrub(wrk.location)) for i in child])
	res.append(group)
	return res

def get_labour_operator_expense(filters):
	paver_labour_query = f"""
				SELECT 
					work_station as fieldname,
					SUM(labour_cost_manufacture+labour_cost_in_rack_shift+labour_expense) as value
				from `tabMaterial Manufacturing`
				WHERE
					from_time between '{filters.get("from_date")}' and '{filters.get("to_date")}'
				group by work_station
				"""
	paver_operator_query=f"""
				SELECT 
					work_station as fieldname,
					SUM(operators_cost_in_manufacture+operators_cost_in_rack_shift) as value
				from `tabMaterial Manufacturing`
				WHERE 
					from_time between '{filters.get("from_date")}' and '{filters.get("to_date")}'
				group by work_station
				"""
	cw_labour_query=f"""
				SELECT 
					type as fieldname,
					SUM(total_labour_wages + labour_expense_for_curing) as value
				from `tabCW Manufacturing`
				WHERE 
					molding_date between '{filters.get("from_date")}' and '{filters.get("to_date")}'
				group by type
				"""
	cw_operator_query=f"""
				SELECT 
					type as fieldname,
					SUM(total_operator_wages) as value
				from `tabCW Manufacturing`
				WHERE 
					molding_date between '{filters.get("from_date")}' and '{filters.get("to_date")}'
				group by type
				"""
	paver_labour_cost = frappe.db.sql(paver_labour_query, as_dict=True)
	paver_operator_cost = frappe.db.sql(paver_operator_query, as_dict=True)
	cw_labour_cost = frappe.db.sql(cw_labour_query, as_dict=True)
	cw_operator_cost = frappe.db.sql(cw_operator_query, as_dict=True)

	total_labour_cost = {
			frappe.scrub(r.get('fieldname') or ''): r.get('value')
			for r in paver_labour_cost+cw_labour_cost
		}
	total_labour_cost["balance"] = sum([i.get("value") or 0 for i in (paver_labour_cost+cw_labour_cost)])
	total_labour_cost["value"] = "Labour Expense"
	total_labour_cost["account_name"] = "Labour Expense"
	total_labour_cost["expandable"] = 0
	total_labour_cost["child_nodes"] = []

	total_operator_cost = {
			frappe.scrub(r.get('fieldname') or ''): r.get('value')
			for r in paver_operator_cost+cw_operator_cost
		}
	total_operator_cost["balance"] = sum([i.get("value") or 0 for i in (paver_operator_cost+cw_operator_cost)])
	total_operator_cost["value"] = "Operator Expense"
	total_operator_cost["account_name"] = "Operator Expense"
	total_operator_cost["expandable"] = 0
	total_operator_cost["child_nodes"] = []

	labour_opr_exp = {
				"value": "Labour & Operator",
				"account_name": "Labour & Operator",
				"expandable": 1,
				"balance": 0,
				"child_nodes": [
					total_labour_cost,
					total_operator_cost
				]
			}
	
	return [labour_opr_exp]
