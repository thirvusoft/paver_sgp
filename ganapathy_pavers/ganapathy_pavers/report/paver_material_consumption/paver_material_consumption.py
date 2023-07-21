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
	return frappe.db.sql(f"""
				SELECT
					bom.item_code as item,
					sum(bom.qty) as qty
				FROM `tabMaterial Manufacturing` mm
				INNER JOIN `tabBOM Item` bom ON
		      	bom.parenttype = 'Material Manufacturing' AND bom.parent = mm.name
		      	WHERE
		      		mm.total_production_sqft > 0 AND
		      		CASE
		      			WHEN IFNULL('{filters.get('from_date') or ''}', '') != ''
					    	THEN DATE(mm.from_time) >= '{filters.get('from_date') or ''}'
						ELSE 1=1
					END AND
					CASE
		      			WHEN IFNULL('{filters.get('to_date') or ''}', '') != ''
					    	THEN DATE(mm.from_time) <= '{filters.get('to_date') or ''}'
						ELSE 1=1
					END AND
					CASE
		      			WHEN IFNULL('{filters.get('paver_type') or ''}', '') != ''
					    	THEN mm.paver_type = '{filters.get('paver_type') or ''}'
						ELSE 1=1
					END AND
					CASE
		      			WHEN IFNULL('{filters.get('only_shot_blast') or ''}', '') != ''
					    	THEN mm.is_shot_blasting = '{filters.get('only_shot_blast') or ''}'
						ELSE 1=1
					END AND
					CASE
		      			WHEN IFNULL('{filters.get('only_sample') or ''}', '') != ''
					    	THEN mm.is_sample = '{filters.get('only_sample') or ''}'
						ELSE 1=1
					END AND
					CASE
		      			WHEN IFNULL({len(filters.get('machine') or [])}, 0) != 0
					    	THEN mm.work_station in ({', '.join(f"'{i}'" for i in (filters.get('machine') or ['', '']))})
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
