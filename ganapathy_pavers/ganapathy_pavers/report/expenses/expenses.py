# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import json
import frappe
from ganapathy_pavers.custom.py.expense import  expense_tree
WORKSTATIONS = {}

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_columns(filters):
	WORKSTATIONS = frappe.get_all("Workstation", {"used_in_expense_splitup": 1}, pluck="name")

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
			"fieldtype": "currency",
			"label": "Total Amount",
			"width": 150
		},
		{
			"fieldname": "paver",
			"fieldtype": "Currency",
			"label": "Paver",
			"width": 100,
			"hidden": filters.get("expense_type") == "Vehicle"
		},
		{
			"fieldname": "compound_wall",
			"fieldtype": "Currency",
			"label": "Compound Wall",
			"width": 100,
			"hidden": filters.get("expense_type") == "Vehicle"
		},
		{
			"fieldname": "fencing_post",
			"fieldtype": "Currency",
			"label": "Fencing Post",
			"width": 100,
			"hidden": filters.get("expense_type") == "Vehicle"
		},
		{
			"fieldname": "lego_block",
			"fieldtype": "Currency",
			"label": "Lego Block",
			"width": 100,
			"hidden": filters.get("expense_type") == "Vehicle"
		},
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
	for wrk in WORKSTATIONS:
		columns.append({
			"fieldname": frappe.scrub(wrk),
			"fieldtype": "Currency",
			"label": wrk,
			"width": 100,
			"hidden": filters.get("expense_type") == "Vehicle"
		})
	return columns

def get_data(filters):
	WORKSTATIONS = frappe.get_all("Workstation", {"used_in_expense_splitup": 1}, pluck="name")

	total_amount = {
		"total_amount": 0,
		"paver": 0,
		"compound_wall": 0,
		"fencing_post": 0,
		"lego_block": 0
	}
	for wrk in WORKSTATIONS:
		total_amount[frappe.scrub(wrk)] = 0

	exp_tree=expense_tree(
				from_date=filters.get('from_date'),
				to_date=filters.get('to_date'),
				expense_type=filters.get("expense_type"),
				vehicle_summary=filters.get("vehicle_summary"),
				all_expenses=True
			)
	res=[]
	for i in exp_tree:
		dic={}
		if i.get("expandable"):
			dic["expense_group"]=i['value']
			child, total_amount=get_expense_from_child(account=i['child_nodes'], WORKSTATIONS=WORKSTATIONS, total_amount=total_amount)
			if child:
				res.append(dic)
				if not filters.get("expense_summary"):
					res+=child
				res+=group_total(child, WORKSTATIONS)
		else:
			if i["balance"]:
				dic={}
				if res:
					res.append({})
				
				dic['expense']=i.get('value')

				dic['paver']=0
				dic['compound_wall']=i.get('compound_wall')
				dic['fencing_post']=i.get('fencing_post')
				dic['lego_block']=i.get('lego_block')
				
				total_amount['compound_wall']+=i.get('compound_wall') or 0
				total_amount['fencing_post']+=i.get('fencing_post') or 0
				total_amount['lego_block']+=i.get('lego_block') or 0
				total_amount['total_amount']+=i.get('balance') or 0

				for wrk in WORKSTATIONS:
					dic['paver'] += i.get(frappe.scrub(wrk)) or 0
					total_amount['paver'] += i.get(frappe.scrub(wrk)) or 0

					total_amount[frappe.scrub(wrk)] += i.get(frappe.scrub(wrk)) or 0
					dic[frappe.scrub(wrk)] = i.get(frappe.scrub(wrk)) or 0

				dic["total_amount"]=i.get("balance") or 0
				dic["reference_data"]=json.dumps(i.get("references")) if i.get("references") else ""
				
				res.append(dic)	
	res.append({})
	total_amount["expense"] = "Total"
	total_amount["total"] = 1
	res.append(total_amount)

	return res

def get_expense_from_child(account, WORKSTATIONS, total_amount):
	res=[]
	for i in account:
		if i["balance"]:
			dic={}

			dic['expense']=i.get('value')
			
			dic['paver']=0
			dic['compound_wall']=i.get('compound_wall')
			dic['fencing_post']=i.get('fencing_post')
			dic['lego_block']=i.get('lego_block')
			
			total_amount['compound_wall']+=i.get('compound_wall') or 0
			total_amount['fencing_post']+=i.get('fencing_post') or 0
			total_amount['lego_block']+=i.get('lego_block') or 0
			total_amount['total_amount']+=i.get('balance') or 0

			for wrk in WORKSTATIONS:
				dic['paver'] += i.get(frappe.scrub(wrk)) or 0
				total_amount['paver'] += i.get(frappe.scrub(wrk)) or 0

				total_amount[frappe.scrub(wrk)] += i.get(frappe.scrub(wrk)) or 0
				dic[frappe.scrub(wrk)] = i.get(frappe.scrub(wrk)) or 0

			dic["total_amount"]=i["balance"] or 0
			dic["reference_data"]=json.dumps(i.get("references")) if i.get("references") else ""
			
			res.append(dic)
		if i['child_nodes']:
			res1, total_amount=get_expense_from_child(account=i['child_nodes'], WORKSTATIONS=WORKSTATIONS, total_amount=total_amount)
			res+=res1
	return res, total_amount

def group_total(child, WORKSTATIONS):
	res=[]
	total_amount=0
	paver=0
	compound_wall=0
	fencing_post=0
	lego_block=0
	for i in child:
		paver+=(i.get('paver') or 0)
		compound_wall+=(i.get('compound_wall') or 0)
		fencing_post+=(i.get('fencing_post') or 0)
		lego_block+=(i.get('lego_block') or 0)
		total_amount+=(i.get('total_amount') or 0)
	group = {
		'expense': "Group Total",
		'total_amount': total_amount or 0,
		'paver': paver or 0,
		'compound_wall': compound_wall or 0,
		'fencing_post': fencing_post or 0,
		'lego_block': lego_block or 0,
		"group_total": 1
	}
	for wrk in WORKSTATIONS:
		group[frappe.scrub(wrk)] = sum([i.get(frappe.scrub(wrk)) for i in child])
	res.append(group)
	return res
	