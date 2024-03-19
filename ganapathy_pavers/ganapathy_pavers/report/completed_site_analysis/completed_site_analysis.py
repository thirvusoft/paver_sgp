# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	data, types_with_data = get_data(filters)
	columns = get_columns(filters, types_with_data) 
	fields = types_with_data if not bool(filters.get('type')) else []
	dataset = [
				{"name": type, "values": [(i.get(frappe.scrub(type)) or 0) for i in data]}
				for type in types_with_data
			]  if not bool(filters.get('type')) else []
	
	chart_data = {
		"data": {
			"labels": [[(i.get('month') or ''), *fields] for i in data],
			"datasets": [
				{"name": 'Total Count', "values": [(i.get('count') or 0) for i in data]},
				*dataset
				],
		},
		"type": "bar",
	}
	return columns, data, None, chart_data

def get_data(filters):
	types = frappe.db.get_all('Types', pluck="name")
	data = frappe.db.sql(f"""
		SELECT
			CONCAT(
				MONTHNAME(sw.completion_date),
				' ',
				YEAR(sw.completion_date)
			) as month,
			COUNT(sw.name) as count,
			{
				', '.join([f'''
					SUM(
						CASE
							WHEN sw.type = '{type}'
								THEN 1
							ELSE 0
						END
					) as {frappe.scrub(type)}
				''' for type in types])
			}
		FROM `tabProject` sw
		WHERE
		    sw.status = "Completed" AND
			CASE
				WHEN IFNULL('{filters.get('from_date') or ''}', '') != ''
					THEN sw.completion_date >= '{filters.get('from_date') or ''}'
				ELSE 1=1
			END AND
			CASE
				WHEN IFNULL('{filters.get('to_date') or ''}', '') != ''
					THEN sw.completion_date <= '{filters.get('to_date') or ''}'
				ELSE 1=1
			END AND
			CASE
				WHEN IFNULL('{filters.get('type') or ''}', '') != ''
					THEN sw.type = '{filters.get('type') or ''}'
				ELSE 1=1
			END AND
			CASE
				WHEN IFNULL('{filters.get('customer') or ''}', '') != ''
					THEN (
							sw.customer = '{filters.get('customer') or ''}'
							OR
							'{filters.get('customer') or ''}' in (
								SELECT
									cus.customer
								FROM `tabTS Customer` cus
								WHERE
									cus.parenttype = "Project" AND
									cus.parent = sw.name
							)
						)
				ELSE 1=1
			END
		GROUP BY CONCAT(
				MONTHNAME(sw.completion_date),
				' ',
				YEAR(sw.completion_date)
			)
		ORDER BY YEAR(sw.completion_date), MONTH(sw.completion_date)
	""", as_dict=True)

	types_with_data = []
	for i in data:
		for type in types:
			if (type in types_with_data):
				continue

			if i.get(frappe.scrub(type)) and type not in types_with_data:
				types_with_data.append(type)

	return data, types_with_data

def get_columns(filters, types_with_data):
	return [
		{
			'fieldname': 'month',
			'label': 'Month',
			'fieldtype': 'Data',
			'width': 200
		},
		*[
			{
				'fieldname': frappe.scrub(type),
				'label': type,
				'fieldtype': 'Int',
				'width': 200,
				'hidden': bool(filters.get('type'))
			}
			for type in types_with_data
		],
		{
			'fieldname': 'count',
			'label': 'Count',
			'fieldtype': 'Int',
			'width': 150
		}
	]