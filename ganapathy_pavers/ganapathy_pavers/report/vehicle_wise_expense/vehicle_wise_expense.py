# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from ganapathy_pavers.ganapathy_pavers.report.vehicle_summary.vehicle_summary import get_rental_vehicle_expense, get_vehicle_expenses

def execute(filters={}):
	if not filters.get('from_date'):
		frappe.throw('Please choose <b>From Date</b>')
	
	if not filters.get('to_date'):
		frappe.throw('Please choose <b>To Date</b>')
	
	columns, data = get_columns(filters), get_data(filters)
	chart_data = {
		"data": {
			"labels": [(i.get('vehicle') or '') for i in data],
			"datasets": [
				{"name": "Expense", "values": [(i.get('expense') or 0) for i in data]},
			],
		},
		"type": "bar",
	}
	return columns, data, None, chart_data

def get_data(filters):
	rental = get_rental_vehicle_expense(filters=filters)
	vehicle_exp = get_vehicle_expenses(filters=filters)

	res = []

	if rental.get('amount'):
		res.append(
			{
				'vehicle': "RENTAL",
				'expense': rental.get('amount')
			}
		)
	for veh in vehicle_exp:
		res.append({
			'vehicle': veh,
			'expense': vehicle_exp.get(veh) or 0
		})
	
	return res

def get_columns(filters):
	return [
		{
			"label": "Vehicle",
			"fieldname": "vehicle",
			"fieldtype": "Link",
			"options": "Vehicle",
			"width": 200,
		},
		{
			"label": "Expense",
			"fieldname": "expense",
			"fieldtype": "Currency",
			"width": 150,
		},
	]
