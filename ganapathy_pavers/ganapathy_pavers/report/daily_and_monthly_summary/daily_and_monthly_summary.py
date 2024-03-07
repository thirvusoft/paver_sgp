# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
import ganapathy_pavers

def execute(filters=None):
	columns, data = get_columns() or [], get_data(filters) or []
	return columns, data

def get_columns():
	column = [
		{
			'fieldname':'type',
			'label':'Type',
			'fieldtype':'Data',
			'width':300
		},
		{
			'fieldname':'sqft',
			'label':'SQFT',
			'fieldtype':'Float',
			'width':300,
			'precision':3
		},
	]
	return column


def get_data(filters= {}):
	final_data = []
	pm_filt = {'docstatus':['!=', 2], 'is_sample': 0}
	cw_filt = {'docstatus':['!=', 2], "type": ["is", "set"]}
	dl_filt = {'docstatus':1}
	if(filters.get('from_date')):
		pm_filt['from_time'] = ['>=', filters.get('from_date')]
		cw_filt['molding_date'] = ['>=', filters.get('from_date')]
		dl_filt['posting_date'] = ['>=', filters.get('from_date')]

	if(filters.get('to_date')):
		pm_filt['from_time'] = ['<=', filters.get('to_date')]
		cw_filt['molding_date'] = ['<=', filters.get('to_date')]
		dl_filt['posting_date'] = ['<=', filters.get('to_date')]
	if(filters.get('from_date') and filters.get('to_date')):
		cw_filt['molding_date'] = ['between', (filters.get('from_date'), filters.get('to_date'))]
		pm_filt['from_time'] = ['between', (filters.get('from_date'), filters.get('to_date'))]
		dl_filt['posting_date'] = ['between', (filters.get('from_date'), filters.get('to_date'))]

	pm_sqft = sum(frappe.db.get_all('Material Manufacturing', filters=pm_filt, pluck='total_production_sqft'))
	cw_sqft = frappe.db.get_all('CW Manufacturing', filters=cw_filt, fields=['sum(production_sqft) as production_sqft', 'type'], group_by="type")
	delivery_notes = frappe.db.get_all('Delivery Note', filters=dl_filt, pluck='name')

	if pm_sqft:
		final_data.append({'type':'Paver Production', 'sqft': pm_sqft})
	
	for cw in cw_sqft:
		final_data.append({'type': f'{cw.type} Production', 'sqft': cw.production_sqft or 0})

	si_filt = dl_filt
	si_filt['update_stock'] = 1
	sales_invoice = frappe.db.get_all('Sales Invoice', filters=si_filt, pluck='name')
	
	pv_dl_items = frappe.db.get_all('Delivery Note Item', filters={'parent':['in', delivery_notes], 'item_group':'Pavers'}, fields=['item_code', 'stock_qty', 'stock_uom'])
	cw_dl_items = frappe.db.get_all('Delivery Note Item', filters={'parent':['in', delivery_notes], 'item_group':'Compound Walls'}, fields=['item_code', 'stock_qty', 'stock_uom'])

	pv_si_items = frappe.db.get_all('Sales Invoice Item', filters={'parent':['in', sales_invoice], 'item_group':'Pavers'}, fields=['item_code', 'stock_qty', 'stock_uom'])
	cw_si_items = frappe.db.get_all('Sales Invoice Item', filters={'parent':['in', sales_invoice], 'item_group':'Compound Walls'}, fields=['item_code', 'stock_qty', 'stock_uom'])
	
	pv_dl_qty = 0
	cw_type_wise_delivery_qty = {}
	item_wise_type = {}

	for i in pv_dl_items:
		if(i.stock_uom != 'SQF'):
			pv_dl_qty += ganapathy_pavers.uom_conversion(i.item_code, from_uom=i.stock_uom, from_qty=i.stock_qty, to_uom='SQF')
		else:
			pv_dl_qty += i.stock_qty

	for i in pv_si_items:
		if(i.stock_uom != 'SQF'):
			pv_dl_qty += ganapathy_pavers.uom_conversion(i.item_code, from_uom=i.stock_uom, from_qty=i.stock_qty, to_uom='SQF')
		else:
			pv_dl_qty += i.stock_qty
	
	for i in cw_dl_items:
		if i.item_code not in item_wise_type:
			item_wise_type[i.item_code] = frappe.db.get_value('Item', i.item_code, 'compound_wall_type')

		if(i.stock_uom != 'SQF'):
			cw_dl_qty = ganapathy_pavers.uom_conversion(i.item_code, from_uom=i.stock_uom, from_qty=i.stock_qty, to_uom='SQF')
		else:
			cw_dl_qty = i.stock_qty
		
		if item_wise_type[i.item_code] not in cw_type_wise_delivery_qty:
			cw_type_wise_delivery_qty[item_wise_type[i.item_code]] = 0
		
		cw_type_wise_delivery_qty[item_wise_type[i.item_code]] += cw_dl_qty

	for i in cw_si_items:
		if i.item_code not in item_wise_type:
			item_wise_type[i.item_code] = frappe.db.get_value('Item', i.item_code, 'compound_wall_type')

		if(i.stock_uom != 'SQF'):
			cw_dl_qty = ganapathy_pavers.uom_conversion(i.item_code, from_uom=i.stock_uom, from_qty=i.stock_qty, to_uom='SQF')
		else:
			cw_dl_qty = i.stock_qty
		
		if item_wise_type[i.item_code] not in cw_type_wise_delivery_qty:
			cw_type_wise_delivery_qty[item_wise_type[i.item_code]] = 0
		
		cw_type_wise_delivery_qty[item_wise_type[i.item_code]] += cw_dl_qty

	if final_data:
		final_data.append({})
	
	if pv_dl_qty:
		final_data.append({'type':'Paver Delivery', 'sqft':pv_dl_qty})

	for cw in cw_type_wise_delivery_qty:
		if cw_type_wise_delivery_qty[cw]:
			final_data.append({'type': f'{cw} Delivery', 'sqft': cw_type_wise_delivery_qty[cw]})

	return final_data
