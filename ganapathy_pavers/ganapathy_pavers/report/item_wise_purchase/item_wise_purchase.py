# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	chart_data = {
		"data": {
			"labels": [[(i.get('item') or ''), *(filters.get('item_group') or [])] for i in data],
			"datasets": [
				{"name": "Qty", "values": [(i.get('qty') or 0) for i in data]},
				{"name": "Amount", "values": [(i.get('amount') or 0) for i in data]},
			],
		},
		"type": "bar",
	}
	return columns, data, None, chart_data

def get_data(filters):
	return frappe.db.sql(f"""
			SELECT
				pii.item_code as item,
				sum(pii.stock_qty) * (
					IFNULL((
						SELECT
							uom.conversion_factor
						FROM `tabUOM Conversion Detail` uom
						WHERE
							uom.parenttype='Item' and
							uom.parent=pii.item_code and
							uom.uom=pii.stock_uom
						LIMIT 1
					)    
					, 0)
					/
					IFNULL((
						SELECT
							uom.conversion_factor
						FROM `tabUOM Conversion Detail` uom
						WHERE
							uom.parenttype='Item' and
							uom.parent=pii.item_code and
							uom.uom = (
								SELECT
		      						IFNULL(item.dsm_uom, item.stock_uom)
		      					FROM `tabItem` item
		      					WHERE
		      						item.name = pii.item_code
		      					LIMIT 1
							)
						LIMIT 1
					)    
					, 0)
				) as qty,
				sum(pii.amount) as amount
		    FROM `tabPurchase Invoice` pi
		    INNER JOIN `tabPurchase Invoice Item` pii
		    ON pii.parent = pi.name AND pii.parenttype = "Purchase Invoice"
		    WHERE
		      	pi.update_stock = 1 AND
				pi.docstatus = 1 AND
		      	CASE
		      		WHEN IFNULL('{filters.get('supplier') or ""}', '') != ''
				    	THEN pi.supplier = "{filters.get('supplier')}"
					ELSE 1=1
				END AND
				CASE
					WHEN IFNULL('{filters.get('from_date') or ''}', '') != ''
						THEN pi.posting_date >= '{filters.get('from_date') or ''}'
					ELSE 1=1
				END AND
				CASE
					WHEN IFNULL('{filters.get('to_date') or ''}', '') != ''
						THEN pi.posting_date <= '{filters.get('to_date') or ''}'
					ELSE 1=1
				END AND
				CASE
					WHEN IFNULL({len(filters.get('item_group') or [])}, 0) != 0
						THEN pii.item_group in ({', '.join(f"'{i}'" for i in (filters.get('item_group') or ['', '']))})
					ELSE 1=1
				END AND
				CASE
					WHEN IFNULL({len(filters.get('warehouse') or [])}, 0) != 0
						THEN pii.warehouse in ({', '.join(f"'{i}'" for i in (filters.get('warehouse') or ['', '']))})
					ELSE 1=1
				END
			GROUP BY
				pii.item_code
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
			'fieldname': 'qty',
			'label': 'Qty',
			'fieldtype': 'Float',
			'width': 150
		},
		{
			'fieldname': 'amount',
			'label': 'Amount',
			'fieldtype': 'Currency',
			'width': 150
		}
	]