# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days
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
	pm_filt = {'docstatus':['!=', 2]}
	cw_filt = {'docstatus':['!=', 2]}
	dl_filt = {'docstatus':1}
	if(filters.get('from_date')):
		pm_filt['from_time'] = ['>=', add_days(filters.get('from_date'),1)]
		cw_filt['molding_date'] = ['>=', filters.get('from_date')]
		dl_filt['posting_date'] = ['>=', filters.get('from_date')]

	if(filters.get('to_date')):
		pm_filt['to'] = ['<=', add_days(filters.get('to_date'),1)]
		cw_filt['molding_date'] = ['<=', filters.get('to_date')]
		dl_filt['posting_date'] = ['<=', filters.get('to_date')]
	if(filters.get('from_date') and filters.get('to_date')):
		cw_filt['molding_date'] = ['between', (filters.get('from_date'), filters.get('to_date'))]

	pm_sqft = sum(frappe.db.get_all('Material Manufacturing', filters=pm_filt, pluck='production_sqft'))
	cw_sqft = sum(frappe.db.get_all('CW Manufacturing', filters=cw_filt, pluck='production_sqft'))
	delivery_notes = frappe.db.get_all('Delivery Note', filters=dl_filt, pluck='name')

	si_filt = dl_filt
	si_filt['update_stock'] = 1
	sales_invoice = frappe.db.get_all('Sales Invoice', filters=si_filt, pluck='name')
	
	final_data.append({'type':'Daily Paver Production', 'sqft':pm_sqft})
	final_data.append({'type':'Daily Compound Wall Production', 'sqft':cw_sqft})
	
	pv_dl_items = frappe.db.get_all('Delivery Note Item', filters={'parent':['in', delivery_notes], 'item_group':'Pavers'}, fields=['item_code', 'stock_qty', 'uom'])
	cw_dl_items = frappe.db.get_all('Delivery Note Item', filters={'parent':['in', delivery_notes], 'item_group':'Compound Walls'}, fields=['item_code', 'stock_qty', 'uom'])

	pv_si_items = frappe.db.get_all('Sales Invoice Item', filters={'parent':['in', sales_invoice], 'item_group':'Pavers'}, fields=['item_code', 'stock_qty', 'uom'])
	cw_si_items = frappe.db.get_all('Sales Invoice Item', filters={'parent':['in', sales_invoice], 'item_group':'Compound Walls'}, fields=['item_code', 'stock_qty', 'uom'])
	
	pv_dl_qty = 0
	cw_dl_qty = 0

	for i in pv_dl_items:
		if(i.uom != 'SQF'):
			pv_dl_qty += ganapathy_pavers.uom_conversion(i.item_code, from_uom=i.uom, from_qty=i.stock_qty, to_uom='SQF')
		else:
			pv_dl_qty += i.stock_qty
	for i in pv_si_items:
		if(i.uom != 'SQF'):
			pv_dl_qty += ganapathy_pavers.uom_conversion(i.item_code, from_uom=i.uom, from_qty=i.stock_qty, to_uom='SQF')
		else:
			pv_dl_qty += i.stock_qty
	
	for i in cw_dl_items:
		if(i.uom != 'SQF'):
			cw_dl_qty += ganapathy_pavers.uom_conversion(i.item_code, from_uom=i.uom, from_qty=i.stock_qty, to_uom='SQF')
		else:
			cw_dl_qty += i.stock_qty
	for i in cw_si_items:
		if(i.uom != 'SQF'):
			cw_dl_qty += ganapathy_pavers.uom_conversion(i.item_code, from_uom=i.uom, from_qty=i.stock_qty, to_uom='SQF')
		else:
			cw_dl_qty += i.stock_qty

	final_data.append({'type':'Paver Delivery Note', 'sqft':pv_dl_qty})
	final_data.append({'type':'Compound Wall Delivery Note', 'sqft':cw_dl_qty})

	return final_data