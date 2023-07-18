# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	chart_data = {
		"data": {
			"labels": [(i.get('item') or '') for i in data],
			"datasets": [
				{"name": "SQFT", "values": [(i.get('sqft') or 0) for i in data]},
			],
		},
		"type": "bar",
	}
	return columns, data, None, chart_data


def get_data(filters):
	return frappe.db.sql(f"""
		SELECT
		    sbi.item_name as item,
		    SUM(sbi.sqft - sbi.damages_in_sqft) as sqft
		FROM `tabShot Blast Costing` sbc
		INNER JOIN `tabShot Blast Items` sbi
		ON sbi.parent=sbc.name AND sbi.parenttype = 'Shot Blast Costing'
		WHERE
			sbc.docstatus != 2 AND
		    IFNULL(sbc.to_time, '') != '' AND
		    CASE
				WHEN IFNULL('{filters.get('from_date') or ''}', '') != ''
					THEN DATE(sbc.to_time) >= '{filters.get('from_date') or ''}'
				ELSE 1=1
			END AND
			CASE
				WHEN IFNULL('{filters.get('to_date') or ''}', '') != ''
					THEN DATE(sbc.to_time) <= '{filters.get('to_date') or ''}'
				ELSE 1=1
			END AND
			CASE
				WHEN IFNULL("{filters.get("location") or ""}", "") != ""
					THEN (
							SELECT 
								mm.work_station
							FROM `tabMaterial Manufacturing` mm
							WHERE
								mm.name = sbi.material_manufacturing
							LIMIT 1
						) in (
							SELECT 
								wrk.name
							FROM `tabWorkstation` wrk
							WHERE
								wrk.location = '{filters.get("location")}'
						)
				ELSE 1=1
			END
		GROUP BY
			sbi.item_name
	""", as_dict=True)

def get_columns(filters):
	return [
		{
			'fieldname': 'item',
			'label': 'Item',
			'fieldtype': 'Link',
			'options': 'Item',
			'width': 200
		},
		{
			'fieldname': 'sqft',
			'label': 'SQFT',
			'fieldtype': 'Float',
			'width': 150
		},
	]
