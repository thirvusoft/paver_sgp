# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": "Vehicle",
			"fieldname": "vehicle",
			"fieldtype": "Link",
			"options": "Vehicle",
			"width": 150,
		},
		{
			"label": "Due Amount",
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": "Start Date",
			"fieldname": "start_date",
			"fieldtype": "Date",
			"width": 150,
		},
		{
			"label": "Total no of dues",
			"fieldname": "total_due",
			"fieldtype": "Int",
			"width": 150,
		},
		{
			"label": "Balance Due",
			"fieldname": "balance_due",
			"fieldtype": "Int",
			"width": 150,
		},
		{
			"label": "End Date",
			"fieldname": "end_date",
			"fieldtype": "Date",
			"width": 150,
		}
	]

	return columns

def get_data(filters):
	maintenance = filters.get("maintenance_type")
	date=filters.get("date") or frappe.utils.nowdate()
	if not maintenance or not date:
		return []

	query=f"""
		select
			vl.name as vehicle,
			md.expense as amount,
			md.from_date as start_date,
			TIMESTAMPDIFF(MONTH, md.from_date, md.to_date) as total_due,
			TIMESTAMPDIFF(MONTH, '{date}', md.to_date) as balance_due,
			md.to_date as end_date
		from `tabVehicle` vl
		inner join `tabMaintenance Details` md
		on md.parent=vl.name and md.parenttype="Vehicle"
		where
			md.maintenance='{maintenance}' and
			ifnull(md.from_date, "")!="" and
			ifnull(md.to_date, "")!=""
	"""
	data = frappe.db.sql(query, as_dict=True)
	return data
