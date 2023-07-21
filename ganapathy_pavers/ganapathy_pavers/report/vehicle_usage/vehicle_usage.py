# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	chart_data = {
		"data": {
			"labels": [(i.get('vehicle') or '') for i in data],
			"datasets": [
				{"name": "Distance Travelled", "values": [(i.get('distance') or 0) for i in data]},
			],
		},
		"type": "bar",
	}
	return columns, data, None, chart_data

def get_data(filters):
	return frappe.db.sql(f"""
		SELECT
			vl.license_plate as vehicle,
			SUM(vl.today_odometer_value) as distance
		FROM `tabVehicle Log` vl
		WHERE
			vl.docstatus = 1 AND
		    IFNULL(vl.today_odometer_value, 0) != 0 AND
		    CASE
				WHEN IFNULL('{filters.get('from_date') or ''}', '') != ''
					THEN vl.date >= '{filters.get('from_date') or ''}'
				ELSE 1=1
			END AND
			CASE
				WHEN IFNULL('{filters.get('to_date') or ''}', '') != ''
					THEN vl.date <= '{filters.get('to_date') or ''}'
				ELSE 1=1
			END AND
			CASE
				WHEN IFNULL({len(filters.get('purpose') or [])}, 0) != 0
					THEN vl.select_purpose in ({', '.join(f"'{i}'" for i in (filters.get('purpose') or ['', '']))})
				ELSE 1=1
			END
		GROUP BY vl.license_plate
	""", as_dict=True)

def get_columns(filters):
	return [
		{
			'fieldname': 'vehicle',
			'label': 'Vehicle',
			'fieldtype': 'Link',
			'options': 'Vehicle',
			'width': 200
		},
		{
			'fieldname': 'distance',
			'label': 'Distance Travelled',
			'fieldtype': 'Float',
			'width': 150
		}
	]