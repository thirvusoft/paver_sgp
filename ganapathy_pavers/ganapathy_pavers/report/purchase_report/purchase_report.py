# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from ganapathy_pavers import uom_conversion

def execute(filters=None):
	columns, data = get_columns(), get_data(filters=filters)
	return columns, data

def get_columns():
	return [
		{
			"fieldname": "row_info",
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "name",
			"label": "Name",
			"fieldtype": "Data" ,
			"width": 150
		},
		{
			"fieldname": "qty",
			"label": "Qty",
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "uom",
			"label": "UOM",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 150
		},
		{
			"fieldname": "average_rate",
			"label": "Average Rate",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "amount",
			"label": "Amount",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "payment",
			"label": "Payment",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "old_balance",
			"label": "Old Balance",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "balance",
			"label": "Month End Balance",
			"fieldtype": "Currency",
			"width": 150
		}
	]

def get_data(filters):
	if not filters.get("from_date"):
		frappe.throw("Please choose from date")
	if not filters.get("to_date"):
		frappe.throw("Please choose to date")
	
	supplier_data = get_supplier_data(filters=filters)
	item_data = get_item_data(filters=filters)
	return supplier_data + ([{}] if supplier_data and item_data else []) + item_data

def get_supplier_data(filters):
	data = frappe.db.sql(f"""
	SELECT
		'Supplier' as row_info,
		pi.supplier as name,
		SUM(
			pii.qty * IFNULL(
							pii.conversion_factor
						, 0)/
						IFNULL(
					  		(
								SELECT
									uom.conversion_factor
								FROM `tabUOM Conversion Detail` uom
								WHERE
									uom.parenttype='Item' and
									uom.parent=pii.item_code and
									uom.uom=(SELECT IF(IFNULL(item.purchase_uom, '') != '', item.purchase_uom, item.stock_uom) FROM `tabItem` item WHERE item.name=pii.item_code limit 1)
							)    
						, 1)
		) as qty,
		AVG(
			((pii.rate + (pii.rate * IFNULL(pii.tax_rate, 0)/100)) * IFNULL(
					  		(
								SELECT
									uom.conversion_factor
								FROM `tabUOM Conversion Detail` uom
								WHERE
									uom.parenttype='Item' and
									uom.parent=pii.item_code and
									uom.uom=(SELECT IF(IFNULL(item.purchase_uom, '') != '', item.purchase_uom, item.stock_uom) FROM `tabItem` item WHERE item.name=pii.item_code limit 1)
							)    
						, 0)/
					  	IFNULL(
							pii.conversion_factor
						, 1)
			) + 
			(IFNULL(pi.ts_total_amount, 0) / pi.total_qty)
		) as average_rate,
		SUM(pi.rounded_total) as amount
	FROM `tabPurchase Invoice` pi
	INNER JOIN `tabPurchase Invoice Item` pii ON pii.parenttype = 'Purchase Invoice' AND pi.name = pii.parent
	WHERE
		pi.docstatus = 1 AND
		pi.posting_date between "{filters.get("from_date")}" AND "{filters.get("to_date")}" AND
		CASE
			WHEN IFNULL({len(filters.get('supplier_group') or [])}, 0) != 0
				THEN (
					select sup.supplier_group from `tabSupplier` sup where sup.name = pi.supplier limit 1
				) in ({', '.join(f"'{i}'" for i in (filters.get('supplier_group') or ['', '']))})
			ELSE 1=1
		END
	GROUP BY
		pi.supplier
	""", as_dict=True)

	old_balance_amount = {row.party: row.amount for row in frappe.db.sql("""
		select party, (sum(credit_in_account_currency) - sum(debit_in_account_currency)) as amount
		from `tabGL Entry`
		where party_type = "Supplier" and posting_date < %s
		and is_cancelled = 0
		group by party
		""", (filters.get("from_date")), as_dict=True)}

	balance_amount = {row.party: row.amount for row in frappe.db.sql("""
		select party, (sum(credit_in_account_currency) - sum(debit_in_account_currency)) as amount
		from `tabGL Entry`
		where party_type = "Supplier" and posting_date < %s
		and is_cancelled = 0
		group by party
		""", (filters.get("to_date")), as_dict=True)}

	payment_amount = {row.party: row.amount for row in frappe.db.sql("""
		select party, sum(debit_in_account_currency) as amount
		from `tabGL Entry`
		where party_type = "Supplier" and posting_date between %s and %s
		and is_cancelled = 0
		group by party
		""", (filters.get("from_date"), filters.get("to_date")), as_dict=True)}

	for row in data:
		row.old_balance = old_balance_amount.get(row.name) or 0
		row.balance = balance_amount.get(row.name) or 0
		row.payment = payment_amount.get(row.name) or 0
	
	total = {
		"row_info": "bold",
		"name": "Total"
	}

	if data:
		for row in data:
			for field in row:
				if isinstance(row[field], (int, float)) and field in ["amount", "payment", "old_balance", "balance"]:
					total[field] = row[field] + (total.get(field) or 0)
		
		data.append(total)
	return data

def get_item_data(filters):
	data = frappe.db.sql(f"""
	SELECT
		"Item" as row_info,
		pii.item_code as name,
		pii.type,
		SUM(
			pii.qty * IFNULL(
							pii.conversion_factor
						, 0)/
						IFNULL(
					  		(
								SELECT
									uom.conversion_factor
								FROM `tabUOM Conversion Detail` uom
								WHERE
									uom.parenttype='Item' and
									uom.parent=pii.item_code and
									uom.uom=(SELECT IF(IFNULL(item.purchase_uom, '') != '', item.purchase_uom, item.stock_uom) FROM `tabItem` item WHERE item.name=pii.item_code limit 1)
							)    
						, 1)
		) as qty,
		AVG(
			((pii.rate + (pii.rate * IFNULL(pii.tax_rate, 0)/100)) * IFNULL(
					  		(
								SELECT
									uom.conversion_factor
								FROM `tabUOM Conversion Detail` uom
								WHERE
									uom.parenttype='Item' and
									uom.parent=pii.item_code and
									uom.uom=(SELECT IF(IFNULL(item.purchase_uom, '') != '', item.purchase_uom, item.stock_uom) FROM `tabItem` item WHERE item.name=pii.item_code limit 1)
							)    
						, 0)/
					  	IFNULL(
							pii.conversion_factor
						, 1)
			) + 
			(IFNULL(pi.ts_total_amount, 0) / pi.total_qty)
		) as average_rate,
		(SELECT IF(IFNULL(item.purchase_uom, '') != '', item.purchase_uom, item.stock_uom) FROM `tabItem` item WHERE item.name=pii.item_code limit 1) as uom
	FROM `tabPurchase Invoice` pi
	INNER JOIN `tabPurchase Invoice Item` pii ON pii.parenttype = 'Purchase Invoice' AND pi.name = pii.parent
	WHERE
		pi.docstatus = 1 AND
		pii.type in ("Pavers", "Compound Wall") AND
		pi.posting_date between "{filters.get("from_date")}" AND "{filters.get("to_date")}" AND
		CASE
			WHEN IFNULL({len(filters.get('supplier_group') or [])}, 0) != 0
				THEN (
					select sup.supplier_group from `tabSupplier` sup where sup.name = pi.supplier limit 1
				) in ({', '.join(f"'{i}'" for i in (filters.get('supplier_group') or ['', '']))})
			ELSE 1=1
		END AND
		CASE
			WHEN IFNULL({len(filters.get('item_group') or [])}, 0) != 0
				THEN pii.item_group in ({', '.join(f"'{i}'" for i in (filters.get('item_group') or ['', '']))})
			ELSE 1=1
		END
	GROUP BY
		pii.item_code, pii.type
	""", as_dict=True)

	paver_list = frappe.db.get_list("Material Manufacturing", {'from_time': ["between", [filters.get("from_date"), filters.get("to_date")]], 'docstatus': ["!=", 2]}, pluck="name")
	cw_list = frappe.db.get_list("CW Manufacturing", {'molding_date': ["between", [filters.get("from_date"), filters.get("to_date")]], 'docstatus': ["!=", 2]}, pluck="name")
	
	item_wise_purchase_uom = {}

	paver_bom_rows = frappe.db.get_all("BOM Item", {
				"parenttype": "Material Manufacturing",
				"parent": ["in", paver_list],
			}, ["item_code", "rate", "uom"])
	paver_item_rate = {}

	for row in paver_bom_rows:
		if row.item_code not in item_wise_purchase_uom:
			item_wise_purchase_uom[row.item_code] = frappe.db.get_value("Item", row.item_code, "purchase_uom") or frappe.db.get_value("Item", row.item_code, "stock_uom")

		paver_item_rate[row.item_code] = (paver_item_rate.get(row.item_code) or []) + [uom_conversion(item=row.item_code, from_uom=item_wise_purchase_uom[row.item_code], from_qty=row.rate, to_uom=row.uom)]
	
	cw_bom_rows = frappe.db.get_all("BOM Item", {
				"parenttype": "CW Manufacturing",
				"parent": ["in", cw_list],
			}, ["item_code", "rate", "uom"])
	cw_item_rate = {}

	for row in cw_bom_rows:
		if row.item_code not in item_wise_purchase_uom:
			item_wise_purchase_uom[row.item_code] = frappe.db.get_value("Item", row.item_code, "purchase_uom") or frappe.db.get_value("Item", row.item_code, "stock_uom")

		cw_item_rate[row.item_code] = (cw_item_rate.get(row.item_code) or []) + [uom_conversion(item=row.item_code, from_uom=item_wise_purchase_uom[row.item_code], from_qty=row.rate, to_uom=row.uom)]
	
	paver_data = []
	cw_data = []
	
	for row in data:
		if row.type == "Pavers":
			row.amount = sum(paver_item_rate.get(row.name))/len(paver_item_rate.get(row.name)) if paver_item_rate.get(row.name) else 0
			row.payment = (row.amount or 0) - (row.average_rate or 0)
			row.old_balance = (row.payment or 0) * (row.qty or 0)
			paver_data.append(row)

		elif row.type == "Compound Wall":
			row.amount = sum(cw_item_rate.get(row.name))/len(cw_item_rate.get(row.name)) if cw_item_rate.get(row.name) else 0
			row.payment = (row.amount or 0) - (row.average_rate or 0)
			row.old_balance = (row.payment or 0) * (row.qty or 0)
			cw_data.append(row)

	paver_total = {
		"row_info": "bold",
		"name": "Total"
	}
	if paver_data:
		for row in paver_data:
			for field in row:
				if isinstance(row[field], (int, float)) and field in ["old_balance"]:
					paver_total[field] = row[field] + (paver_total.get(field) or 0)
		paver_data.append(paver_total)

	cw_total = {
		"row_info": "bold",
		"name": "Total"
	}
	if cw_data:
		for row in cw_data:
			for field in row:
				if isinstance(row[field], (int, float)) and field in ["old_balance"]:
					cw_total[field] = row[field] + (cw_total.get(field) or 0)
		cw_data.append(cw_total)

	return ([
			{'row_info': 'item_head', 'name': 'Item', 'qty': 'PURCHASE UNIT', 'uom': 'PURCHASE UOM', 'average_rate': 'PURCHASE RATE', 'amount': 'COSTING RATE', 'payment': 'VARIATION RATE', 'old_balance': 'AMOUNT'},
			{'row_info': 'bold', 'name': 'PAVER'},
			*paver_data,
			{}
		] if paver_data else []) + ([
			{'row_info': 'item_head', 'name': 'Item', 'qty': 'PURCHASE UNIT', 'uom': 'PURCHASE UOM', 'average_rate': 'PURCHASE RATE', 'amount': 'COSTING RATE', 'payment': 'VARIATION RATE', 'old_balance': 'AMOUNT'},
			{'row_info': 'bold', 'name': 'COMPOUND WALL'},
			*cw_data,
			{}
		] if cw_data else []) + ([
			{'row_info': 'bold', 'name': 'Net Total', 'old_balance': (paver_total.get("old_balance") or 0) + (cw_total.get("old_balance") or 0)}
		] if paver_data or cw_data else [])
