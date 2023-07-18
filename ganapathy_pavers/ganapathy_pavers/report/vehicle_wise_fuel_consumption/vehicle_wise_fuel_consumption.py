# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

# import frappe
from frappe import _
from ganapathy_pavers.ganapathy_pavers.report.fuel_consumption_summary.fuel_consumption_summary import get_data as get_fuel_consumption

def execute(filters=None):
	columns, data = get_columns(filters), get_fuel_consumption(filters=filters, add_total=False)
	if data:
		data=data[1:]
	chart_data = {
		"data": {
			"labels": [i.get('license_plate') for i in data],
			"datasets": [
				{"name": "Qty", "values": [(i.get('fuel_qty') or 0) for i in data]},
			],
		},
		"type": "bar",
	}
	return columns, data, None, chart_data

def get_columns(filters):
	columns = [
		{
			"label": _("Vehicle"),
			"fieldtype": "Link",
			"fieldname": "license_plate",
			"options":"Vehicle",
			"width": 150
		},
		{
			"label": _("Qty"),
			"fieldtype": "Float",
			"fieldname": "fuel_qty",
			"width": 100
		},
		{
			"label": _("Amount"),
			"fieldtype": "Float",
			"fieldname": "total_fuel",
			"width": 100
		},
	]
	return columns
