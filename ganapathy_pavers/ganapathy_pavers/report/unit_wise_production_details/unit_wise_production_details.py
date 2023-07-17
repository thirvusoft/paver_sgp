# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	chart_data = {
		"data": {
			"labels": [(i.get('unit') or '') for i in data],
			"datasets": [{"values": [(i.get('qty') or 0) for i in data]}],
		},
		"type": "percentage",
	}
	return columns, data, None, chart_data

def get_data(filters):
	return frappe.db.sql(f"""
			SELECT 
				SUM(res.qty) as qty,
				res.unit
			FROM (
				(
					SELECT
							IFNULL((SELECT wrk.location FROM `tabWorkstation` wrk WHERE wrk.name = IFNULL(mm.work_station, '') limit 1), '') as unit,
							sum(mm.total_production_sqft) as qty
						FROM `tabMaterial Manufacturing` mm
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
							END 
						GROUP BY IFNULL((SELECT wrk.location FROM `tabWorkstation` wrk WHERE wrk.name = IFNULL(mm.work_station, '') limit 1), '')
				) UNION ALL
				(
					SELECT
						IFNULL((SELECT wrk.location FROM `tabWorkstation` wrk WHERE wrk.name = IFNULL(cw_item.workstation, '') limit 1), '') as unit,
						sum(cw_item.production_sqft) as qty
					FROM `tabCW Manufacturing` cw
					INNER JOIN `tabCW Items` cw_item ON
					cw_item.parenttype = 'CW Manufacturing' AND cw_item.parent = cw.name
					WHERE
						cw_item.production_sqft > 0 AND
						CASE
							WHEN IFNULL('{filters.get('from_date') or ''}', '') != ''
								THEN DATE(cw.molding_date) >= '{filters.get('from_date') or ''}'
							ELSE 1=1
						END AND
						CASE
							WHEN IFNULL('{filters.get('to_date') or ''}', '') != ''
								THEN DATE(cw.molding_date) <= '{filters.get('to_date') or ''}'
							ELSE 1=1
						END
					GROUP BY
						IFNULL((SELECT wrk.location FROM `tabWorkstation` wrk WHERE wrk.name = IFNULL(cw_item.workstation, '') limit 1), '')
				)
			) res
			GROUP BY res.unit
		""", as_dict=True)

def get_columns(filters):
	return [
		{
			"fieldname": "unit",
			"label": "unit",
			"fieldtype": "Link",
			"options": "Location",
			"width": 500
		},
		{
			"fieldname": "qty",
			"label": "Qty",
			"fieldtype": "Float",
			"width": 100
		}
	]
