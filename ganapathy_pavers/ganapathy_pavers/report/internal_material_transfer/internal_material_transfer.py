# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	for field in ['s_warehouse', 't_warehouse', 'item_code', 'group_by', 'also_group_by']:
		if not filters.get(field):
			filters[field] = []

	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_data(filters):
	order_by = ', '.join([{
		'Date': 'se.posting_date',
		'Item': 'sed.item_code'
	}.get(grp) or '' for grp in filters.get('group_by') or []])
	
	group_by=''

	if filters.get('report_type') == 'Summary':
		group_by = order_by

	if filters.get('group_by'):
		also_group_by = ", ".join([f"se.{frappe.scrub(field)}" for field in (filters.get('also_group_by') or [])])
	else:
		also_group_by = ""

	conditions = ''

	if filters.get('from_date'):
		conditions += f""" and se.posting_date >= DATE('{filters.get('from_date')}') """
	
	if filters.get('to_date'):
		conditions += f""" and se.posting_date <= DATE('{filters.get('to_date')}') """
	
	if filters.get('item_code'):
		conditions += f""" and sed.item_code in ({', '.join([f" '{i}' " for i in filters.get('item_code')])}) """

	if filters.get('s_warehouse'):
		conditions += f""" and sed.s_warehouse in ({', '.join([f" '{i}' " for i in filters.get('s_warehouse')])}) """
	
	if filters.get('t_warehouse'):
		conditions += f""" and sed.t_warehouse in ({', '.join([f" '{i}' " for i in filters.get('t_warehouse')])}) """
	
	if filters.get('vehicle'):
		conditions += f""" and se.vehicle = '{filters.get('vehicle')}' """

	if filters.get('driver'):
		conditions += f""" and se.driver = '{filters.get('driver')}' """
	
	if filters.get('operator'):
		conditions += f""" and se.operator = '{filters.get('operator')}' """


	query = f"""
		SELECT
			se.name as docname,
			se.posting_date,
			sed.item_code,
			SUM(sed.qty) as qty,
			sed.uom,
			SUM(sed.qty*ifnull(
				(
					SELECT
						uom.conversion_factor
					FROM `tabUOM Conversion Detail` uom
					WHERE
						uom.parenttype='Item' and
						uom.parent=sed.item_code and
						uom.uom=sed.uom
				)
				, 0)/
				ifnull((
					SELECT
						uom.conversion_factor
					FROM `tabUOM Conversion Detail` uom
					WHERE
						uom.parenttype='Item' and
						uom.parent=sed.item_code and
						uom.uom='SQF'
				)    
				, 0)
			) as sqr_ft,
			SUM(IFNULL(sed.ts_qty, 0)) as bdl,
			SUM(IFNULL(sed.pieces, 0)) as pieces,
			se.vehicle as vehicle,
			se.driver as driver,
			se.operator as operator
		FROM `tabStock Entry Detail` sed
		INNER JOIN `tabStock Entry` se
		ON se.name = sed.parent
		WHERE
			se.docstatus = 1 and
			se.stock_entry_type = 'Material Transfer' and
			se.is_internal_stock_transfer = 1
			{conditions}
		GROUP BY {'sed.name,' if not group_by else ''} sed.uom {', '+ group_by if group_by else ''} {', '+also_group_by if also_group_by else ''}
		{
			f'''ORDER BY 
			{order_by} {', '+also_group_by if order_by and also_group_by else also_group_by}'''
			if order_by or also_group_by
			else f'''
				ORDER BY se.posting_date, sed.item_code
			'''
		}
	"""

	data = frappe.db.sql(query=query, as_dict=True)

	if filters.get('report_type') == "Report":
		if filters.get('group_by'):
			data = add_group_total(data=data, filters=filters, add_total_row_only = False)
		else:
			data = add_group_total(data=data, filters=filters, add_total_row_only = True)
			frappe.msgprint('Please choose <b>Group By</b> to get a <b>Group Total</b>', alert=True, indicator='yellow')
	else:
		data = add_group_total(data=data, filters=filters, add_total_row_only = True)

	return data

def add_group_total(data, filters, gt_column = "item_code", add_total_row_only=False):
	res = []
	if filters.get('group_by') and filters.get('also_group_by'):
		filters['group_by'] += filters.get('also_group_by')

	current_group = "---".join([str(data[0].get({'Date': 'posting_date', 'Item': 'item_code'}.get(gb) or frappe.scrub(gb))) for gb in filters.get('group_by')]) if data else False
	group=[]
	group_total = {}
	total = {}

	for row in data:
		groupby = "---".join([str(row.get({'Date': 'posting_date', 'Item': 'item_code'}.get(gb) or frappe.scrub(gb))) for gb in filters.get('group_by')])
		if group and groupby != current_group and not add_total_row_only:
			group.sort(key = lambda x: (str(x.get('posting_date') or ''), str(x.get('item_code') or '')))
			res += group
			group_total[gt_column] = "Group Total"
			res.append(group_total)
			res.append({})
			group=[]
			group_total = {} 
			current_group = groupby

		group.append(row)
		for col in row:
			if (col not in group_total and (isinstance(row[col], int) or isinstance(row[col], float))):
				group_total[col] = (group_total.get(col) or 0) + row[col]
				total[col] = (total.get(col) or 0) + row[col]
				
			elif (isinstance(row[col], int) or isinstance(row[col], float)):
				group_total[col] = (group_total.get(col) or 0) + row[col]
				total[col] = (total.get(col) or 0) + row[col]

	if group and not add_total_row_only:
		group.sort(key = lambda x: (str(x.get('posting_date') or ''), str(x.get('item_code') or '')))
		res += group
		group_total[gt_column] = "Group Total"
		res.append(group_total)
		group=[]
		group_total = {} 
		groupby = "---".join([str(row.get({'Date': 'posting_date', 'Item': 'item_code'}.get(gb) or frappe.scrub(gb))) for gb in filters.get('group_by')])
		current_group = groupby
	
	if not res and group:
		res = group
	if res:
		total[gt_column] = "Total"
		res.append(total)

	return res

def get_columns(filters):
	columns = [
		{
			'fieldname': 'docname',
			'label': 'Document No.',
			'fieldtype': 'Link',
			'options': 'Stock Entry',
			'width': 150,
			'hidden': bool(filters.get('group_by') and filters.get('report_type') == 'Summary')
		},
		{
			'fieldname': 'posting_date',
			'label': 'Date',
			'fieldtype': 'Date',
			'width': 150,
			'hidden': bool(filters.get('group_by') and filters.get('report_type') == 'Summary' and 'Date' not in (filters.get('group_by') or []))
		},
		{
			'fieldname': 'item_code',
			'label': 'Item',
			'fieldtype': 'Link',
			'options': 'Item',
			'width': 350,
			'hidden': bool(filters.get('group_by') and filters.get('report_type') == 'Summary' and 'Item' not in (filters.get('group_by') or []))
		},
		{
			'fieldname': 'qty',
			'label': 'Qty',
			'fieldtype': 'Float',
			'width': 150,
		},
		{
			'fieldname': 'uom',
			'label': 'UOM',
			'fieldtype': 'Link',
			'options': 'UOM',
			'width': 100,
		},
		{
			'fieldname': 'sqr_ft',
			'label': 'SQF',
			'fieldtype': 'Float',
			'width': 150,
		},
		{
			'fieldname': 'bdl',
			'label': 'Bdl',
			'fieldtype': 'Float',
			'width': 150,
		},
		{
			'fieldname': 'pieces',
			'label': 'Pieces',
			'fieldtype': 'Float',
			'width': 150,
		},
		{
			'fieldname': 'vehicle',
			'label': 'Vehicle',
			'fieldtype': 'Link',
			'options': 'Vehicle',
			'width': 150,
			'hidden': bool(filters.get('group_by') and filters.get('report_type') == 'Summary' and 'Vehicle' not in (filters.get('also_group_by') or []))
		},
		{
			'fieldname': 'driver',
			'label': 'Driver',
			'fieldtype': 'Link',
			'options': 'Driver',
			'width': 150,
			'hidden': bool(filters.get('group_by') and filters.get('report_type') == 'Summary' and 'Driver' not in (filters.get('also_group_by') or []))
		},
		{
			'fieldname': 'operator',
			'label': 'Operator',
			'fieldtype': 'Link',
			'options': 'Driver',
			'width': 150,
			'hidden': bool(filters.get('group_by') and filters.get('report_type') == 'Summary' and 'Operator' not in (filters.get('also_group_by') or []))
		}
	]

	return columns
