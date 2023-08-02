# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	chart_data = {
		"data": {
			"labels": [(i.get('name') or '') for i in data],
			"datasets": [{"values": [(i.get('qty') or 0) for i in data]}],
		},
		"type": "bar",
	}

	return columns, data, None, chart_data

def get_data(filters):
	fieldname = {
		'Job Worker': 'jw.employee_name',
		'Item': 'jw.item',
		'Site': 'sw.name'
	}
	if not filters.get('group_by'):
		filters["group_by"] = 'Job Worker'
		
	return frappe.db.sql(f"""
			SELECT
		      	IFNULL({fieldname.get(filters.get('group_by'))}, '-') as name,
		      	SUM(jw.sqft_allocated) as qty
		    FROM `tabProject` sw
		    INNER JOIN `tabTS Job Worker Details` jw
			ON sw.name = jw.parent AND jw.parenttype = "Project"
			WHERE
				jw.sqft_allocated != 0 AND
				CASE
					WHEN IFNULL('{filters.get('type') or ''}', '') != ''
						THEN sw.type = '{filters.get('type') or ''}'
					ELSE 1=1
				END AND
				CASE
					WHEN IFNULL({len(filters.get('status') or [])}, 0) != 0
						THEN sw.status in ({', '.join(f"'{i}'" for i in (filters.get('status') or ['', '']))})
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
				END AND
				CASE
					WHEN IFNULL('{filters.get('from_date') or ''}', '') != ''
						THEN jw.start_date >= '{filters.get('from_date') or ''}'
					ELSE 1=1
				END AND
				CASE
					WHEN IFNULL('{filters.get('to_date') or ''}', '') != ''
						THEN jw.end_date <= '{filters.get('to_date') or ''}'
					ELSE 1=1
				END AND
				CASE
					WHEN IFNULL('{filters.get('job_worker') or ''}', '') != ''
						THEN jw.name1 = '{filters.get('job_worker') or ''}'
					ELSE 1=1
				END AND
				CASE
					WHEN IFNULL('{filters.get('site') or ''}', '') != ''
						THEN sw.name = '{filters.get('site') or ''}'
					ELSE 1=1
				END AND
				CASE
					WHEN IFNULL('{filters.get('item') or ''}', '') != ''
						THEN jw.item = '{filters.get('item') or ''}'
					ELSE 1=1
				END AND
				CASE
					WHEN IFNULL('{filters.get('show_only_other_work') or 0}', '0') != '0'
						THEN jw.other_work = 1
					ELSE 1=1
				END AND
				CASE
					WHEN IFNULL('{filters.get('hide_other_work') or 0}', '0') != '0'
						THEN jw.other_work = 0
					ELSE 1=1
				END
			GROUP BY IFNULL({fieldname.get(filters.get('group_by'))}, '')
			ORDER BY SUM(jw.sqft_allocated) DESC
		""", as_dict=True)

def get_columns(filters):
	return [
		{
			"fieldname": "name",
			"label": filters.get('group_by'),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "qty",
			"label": "Qty",
			"fieldtype": "Float",
			"width": 150
		}
	]
