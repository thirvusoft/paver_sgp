# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	chart_data = {
		"data": {
			"labels": [(i.get('site') or '') for i in data],
			"datasets": [{"values": [(i.get('qty') or 0) for i in data]}],
		},
		"type": "bar",
	}

	return columns, data, None, chart_data

def get_data(filters):
	return frappe.db.sql(f"""
			SELECT
		      	sw.name as site,
		      	IFNULL(sw.excess_or_remaining_qty, 0) as qty
		    FROM `tabProject` sw
		    WHERE
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
				WHEN IFNULL('{1 if filters.get('status') == ['Completed'] else 0}', '0') = '1'
					THEN CASE
							WHEN IFNULL('{filters.get('from_date') or ''}', '') != ''
								THEN sw.completion_date >= '{filters.get('from_date') or ''}'
							ELSE 1=1
						END AND
						CASE
							WHEN IFNULL('{filters.get('to_date') or ''}', '') != ''
								THEN sw.completion_date <= '{filters.get('to_date') or ''}'
							ELSE 1=1
						END
				ELSE 1=1
			END
		    ORDER BY sw.excess_or_remaining_qty DESC
		""", as_dict=True)

def get_columns(filters):
	return [
		{
			"fieldname": "site",
			"label": "Site",
			"fieldtype": "Link",
			"options": 'Project',
			"width": 400
		},
		{
			"fieldname": "qty",
			"label": "Excess / Remaining Delivery Qty from Measurement Sqft",
			"fieldtype": "Float",
			"width": 150
		}
	]
