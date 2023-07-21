# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	fields = ['Paver', 'Compound Wall'] if not bool(filters.get('type')) else []
	dataset = [
				{"name": 'Paver', "values": [(i.get('paver') or 0) for i in data]},
				{"name": 'Compound Wall', "values": [(i.get('cw') or 0) for i in data]}
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
	return frappe.db.sql(f"""
		SELECT
			CONCAT(
				MONTHNAME(sw.completion_date),
				' ',
				YEAR(sw.completion_date)
			) as month,
			COUNT(sw.name) as count,
		    SUM(
				CASE
		      		WHEN sw.type = 'Pavers'
		      			THEN 1
		    		ELSE 0
		    	END
			) as paver,
			SUM(
				CASE
		      		WHEN sw.type = 'Compound Wall'
		      			THEN 1
		    		ELSE 0
		    	END
			) as cw
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

def get_columns(filters):
	return [
		{
			'fieldname': 'month',
			'label': 'Month',
			'fieldtype': 'Data',
			'width': 200
		},
		{
			'fieldname': 'paver',
			'label': 'Paver',
			'fieldtype': 'Int',
			'width': 200,
			'hidden': bool(filters.get('type'))
		},
		{
			'fieldname': 'cw',
			'label': 'Compound Wall',
			'fieldtype': 'Int',
			'width': 200,
			'hidden': bool(filters.get('type'))
		},
		{
			'fieldname': 'count',
			'label': 'Count',
			'fieldtype': 'Int',
			'width': 150
		}
	]