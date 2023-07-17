# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	chart_data = {
		"data": {
			"labels": [(i.get('item') or '') for i in data],
			"datasets": [{"values": [(i.get('qty') or 0) for i in data]}],
		},
		"type": "pie",
	}
	return columns, data, None, chart_data

def get_data(filters):
	compound_wall_type = []
	for i in (filters.get('compound_wall_type') or []):
		if (i == "Compound Wall"):
			compound_wall_type += ['Post', 'Slab']
		else:
			compound_wall_type.append(i)

	return frappe.db.sql(f"""
				SELECT
					bom.item_code as item,
					sum(bom.qty) as qty
				FROM `tabCW Manufacturing` cw
				INNER JOIN `tabBOM Item` bom ON
		      	bom.parenttype = 'CW Manufacturing' AND bom.parent = cw.name
		      	WHERE
		      		CASE
		      			WHEN IFNULL('{filters.get('from_date') or ''}', '') != ''
					    	THEN DATE(cw.molding_date) >= '{filters.get('from_date') or ''}'
						ELSE 1=1
					END AND
					CASE
		      			WHEN IFNULL('{filters.get('to_date') or ''}', '') != ''
					    	THEN DATE(cw.molding_date) <= '{filters.get('to_date') or ''}'
						ELSE 1=1
					END AND
					CASE
		      			WHEN IFNULL('{len(compound_wall_type)}', 0) != 0
					    	THEN cw.type in ({', '.join([f"'{i}'" for i in compound_wall_type or ['']])})
						ELSE 1=1
					END
				GROUP BY
					bom.item_code
	""", as_dict=True)

def get_columns(filters):
	return [
		{
			"fieldname": "item",
			"label": "Item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 500
		},
		{
			"fieldname": "qty",
			"label": "Qty",
			"fieldtype": "Float",
			"width": 100
		}
	]
