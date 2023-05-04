# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

maintenance = ["INSURANCE", "VEHICLE DUE"]

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
		}
	]
	for m in maintenance:
		columns.append({
			"label": m,
			"fieldname": frappe.scrub(m),
			"fieldtype": "Float",
			"width": 100,
		})
		columns.append({
			"label": f"{m} End Date",
			"fieldname": f"""{frappe.scrub(m)}_end_date""",
			"fieldtype": "Date",
			"width": 170,
		})

	return columns

def get_data(filters):
	date=filters.get("date") or frappe.utils.nowdate()
	maintenance_query=[
		f"""
		(
			select 
				TIMESTAMPDIFF(MONTH,'{date}',md.to_date) as date 
			from `tabMaintenance Details` md 
			where parent=vl.name and md.maintenance='{m}'
			limit 1
		) as {frappe.scrub(m)},
		(
			select 
				md.to_date
			from `tabMaintenance Details` md 
			where parent=vl.name and md.maintenance='{m}'
			limit 1
		) as {frappe.scrub(m)}_end_date
		""" 
		for m in maintenance
	]

	query=f"""
		select
			vl.name as vehicle
			{(", " + ", ".join(maintenance_query)) if maintenance_query else ""}
		from `tabVehicle` vl
	"""
	data = frappe.db.sql(query, as_dict=True)
	data = [d for d in data if sum([1 for m in maintenance if d.get(f"{frappe.scrub(m)}_end_date")])]
	return data
