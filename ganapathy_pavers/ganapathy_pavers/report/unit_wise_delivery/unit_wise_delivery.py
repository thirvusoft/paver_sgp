# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	chart_data = {
		"data": {
			"labels": [[(i.get('location') or ''), *(filters.get('item_group') or [])] for i in data],
			"datasets": [
				{"name": "Total Qty", "values": [(i.get('qty') or 0) for i in data]},
				*[
					{"name": item_group, "values": [(i.get(frappe.scrub(item_group)) or 0) for i in data]}
					for item_group in (filters.get('item_group') or [])
				]
			],
		},
		"type": "bar",
	}
	return columns, data, None, chart_data

def get_data(filters):
	locations = frappe.get_all("Location", {"warehouse": ["is", "set"]}, ["warehouse", "name"])
	warehouse = {}

	def get_child_warehouses(warehouse):
		res = []
		for w in frappe.get_all("Warehouse", {"parent_warehouse": warehouse}, ['name', 'is_group']):
			if not w.is_group:
				res.append(w.name)
			else:
				res += get_child_warehouses(w.name)
		
		return res

	for unit_warehouse in locations:
		warehouse[unit_warehouse.name] = get_child_warehouses(unit_warehouse.warehouse)

	location_query = f"""
		CASE
			{
				' '.join([f'''
							WHEN dni.warehouse in ({', '.join([f"'{i}'"  for i in (warehouse[unit])])})
								THEN '{unit}'
						'''
					for unit in warehouse
				])
			}
			{
				f'''
					WHEN IFNULL(dni.warehouse, '') != ''
						THEN dni.warehouse
				'''
				if not warehouse else ''
			}
			ELSE IFNULL(dni.warehouse, '')
		END
	"""

	return frappe.db.sql(f"""
		SELECT
			{location_query} as location,
		    {
				", ".join([
					f'''
						SUM(
							CASE 
								WHEN dni.item_group = '{item_group}'
									THEN dni.qty
								ELSE 0
							END
						) as {frappe.scrub(item_group)}
					'''
					for item_group in (filters.get('item_group') or [])
				]) + f"{', ' if filters.get('item_group') else ''}"
			}
		      SUM(dni.qty) as qty
		FROM `tabDelivery Note` dn
		INNER JOIN `tabDelivery Note Item` dni
		ON dn.name = dni.parent AND dni.parenttype = 'Delivery Note'
		WHERE
		    dn.docstatus = 1 AND
		    CASE
				WHEN IFNULL('{filters.get('from_date') or ''}', '') != ''
					THEN dn.posting_date >= '{filters.get('from_date') or ''}'
				ELSE 1=1
			END AND
			CASE
				WHEN IFNULL('{filters.get('to_date') or ''}', '') != ''
					THEN dn.posting_date <= '{filters.get('to_date') or ''}'
				ELSE 1=1
			END AND
			CASE
				WHEN IFNULL({len(filters.get('item_group') or [])}, 0) != 0
					THEN dni.item_group in ({', '.join(f"'{i}'" for i in (filters.get('item_group') or ['', '']))})
				ELSE 1=1
			END AND
			CASE
				WHEN IFNULL('{filters.get('site_work') or ''}', '') != ''
					THEN dn.site_work = '{filters.get('site_work') or ''}'
				ELSE 1=1
			END AND
			CASE
				WHEN IFNULL({filters.get('is_return') or 0}, 0) = 1
					THEN dn.is_return = 1
				ELSE dn.is_return = 0
			END
		GROUP BY {location_query}
	""", as_dict=True)

def get_columns(filters):
	return [
		{
			'fieldname': 'location',
			'label': 'Unit',
			'fieldtype': 'Link',
			'options': 'Project',
			'width': 200
		},
		*[
			{
				'fieldname': frappe.scrub(i),
				'label': i,
				'fieldtype': 'Data',
				'width': 150
			}
			for i in (filters.get('item_group') or [])
		],
		{
			'fieldname': 'qty',
			'label': 'Qty',
			'fieldtype': 'Float',
			'width': 150
		}
	]