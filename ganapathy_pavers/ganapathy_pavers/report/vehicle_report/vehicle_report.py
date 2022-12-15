# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

from copy import copy
import frappe
import ganapathy_pavers

def execute(filters=None):
	columns, data = get_columns() or [], get_data(filters) or [{}]
	return columns, data


def get_columns():
	columns = [
		{
			'fieldname':'vehicle_no',
			'label':'Vehicle No',
			'fieldtype':'Link',
			'options':'Vehicle',
			'width':130,
		},
		{
			'fieldname':'paver_expense',
			'label':'Paver Expense',
			'fieldtype':'Float',
			'width':130,
		},
		{
			'fieldname':'paver_sqft',
			'label':'Paver SQFT',
			'fieldtype':'Float',
			'width':130,
		},
		{
			'fieldname':'paver_sqft_cost',
			'label':'Paver SQFT Cost',
			'fieldtype':'Float',
			'width':130,
		},
		{
			'fieldname':'mileage',
			'label':'Mileage',
			'fieldtype':'Float',
			'width':130,
		},
		{
			'fieldname':'cw_expense',
			'label':'Compound Wall Expense',
			'fieldtype':'Float',
			'width':130,
		},
		{
			'fieldname':'cw_sqft',
			'label':'Compound Wall SQFT',
			'fieldtype':'Float',
			'width':130,
		},
		{
			'fieldname':'cw_sqft_cost',
			'label':'Compound Wall SQFT Cost',
			'fieldtype':'Float',
			'width':130,
		},
		{
			'fieldname':'mileage',
			'label':'Mileage',
			'fieldtype':'Float',
			'width':130,
		},
		
	]
	return columns


def get_sqft(vl_filt, vehicle):
	vl_filt['license_plate'] = vehicle
	data = {}
	dn_vl_filt = copy(vl_filt)
	si_vl_filt = copy(vl_filt)

	dn_vl_filt['delivery_note'] = ['is', 'set']
	si_vl_filt['sales_invoice'] = ['is', 'set']

	dn_names, si_names = frappe.db.get_all('Vehicle Log', filters=dn_vl_filt, pluck='delivery_note'), frappe.db.get_all('Vehicle Log', filters=si_vl_filt, pluck='sales_invoice')
	dn_names = frappe.db.get_all('Delivery Note', filters={'docstatus':['!=', 2], 'type':['in', ('Pavers', 'Compound Wall')], 'name':['in', dn_names]}, fields=['name', 'type'])
	si_names = frappe.db.get_all('Sales Invoice', filters={'docstatus':['!=', 2], 'type':['in', ('Pavers', 'Compound Wall')], 'name':['in', si_names]}, fields=['name', 'type'])
	
	paver_sqft, cw_sqft = 0, 0

	for i in dn_names:
		dn_item = frappe.db.get_all('Delivery Note Item', filters={'parent':i['name']}, fields=['item_code', 'stock_qty', 'uom'])
		for j in dn_item:
			if not (frappe.get_value("Item", j.item_code, "item_group") in["Pavers", "Compound Walls"]):
				continue
			if(j.uom != 'SQF' and i['type'] == 'Pavers'):
				paver_sqft += ganapathy_pavers.uom_conversion(j.item_code, from_uom=j.uom, from_qty=j.stock_qty, to_uom='SQF')
			elif(j.uom == 'SQF' and i['type'] == 'Pavers'):
				paver_sqft += j.stock_qty
			
			if(j.uom != 'SQF' and i['type'] == 'Compound Wall'):
				cw_sqft += ganapathy_pavers.uom_conversion(j.item_code, from_uom=j.uom, from_qty=j.stock_qty, to_uom='SQF')
			elif(j.uom == 'SQF' and i['type'] == 'Compound Wall'):
				cw_sqft += j.stock_qty
	
	for i in si_names:
		si_item = frappe.db.get_all('Sales Invoice Item', filters={'parent':i['name']}, fields=['item_code', 'stock_qty', 'uom'])
		for j in si_item:
			if(j.uom != 'SQF' and i['type'] == 'Pavers'):
				paver_sqft += ganapathy_pavers.uom_conversion(j.item_code, from_uom=j.uom, from_qty=j.stock_qty, to_uom='SQF')
			elif(j.uom == 'SQF' and i['type'] == 'Pavers'):
				paver_sqft += j.stock_qty
			
			if(j.uom != 'SQF' and i['type'] == 'Compound Wall'):
				cw_sqft += ganapathy_pavers.uom_conversion(j.item_code, from_uom=j.uom, from_qty=j.stock_qty, to_uom='SQF')
			elif(j.uom == 'SQF' and i['type'] == 'Compound Wall'):
				cw_sqft += j.stock_qty

	data['vehicle_no'] = vehicle
	data['paver_sqft'] = paver_sqft
	data['cw_sqft'] = cw_sqft

	return data

def get_expense(vl_filt, vehicle, data, filters):
	vl_filt['license_plate'] = vehicle
	dn_vl_filt = copy(vl_filt)
	si_vl_filt = copy(vl_filt)
	filt = copy(vl_filt)

	dn_vl_filt['delivery_note'] = ['is', 'set']
	si_vl_filt['sales_invoice'] = ['is', 'set']

	dn_names, si_names = frappe.db.get_all('Vehicle Log', filters=dn_vl_filt, pluck='delivery_note'), frappe.db.get_all('Vehicle Log', filters=si_vl_filt, pluck='sales_invoice')
	dn_names = frappe.db.get_all('Delivery Note', filters={'docstatus':['!=', 2], 'type':['in', ('Pavers', 'Compound Wall')], 'name':['in', dn_names]}, fields=['name', 'type'])
	si_names = frappe.db.get_all('Sales Invoice', filters={'docstatus':['!=', 2], 'type':['in', ('Pavers', 'Compound Wall')], 'name':['in', si_names]}, fields=['name', 'type'])
	pv_exp, cw_exp = 0, 0
	
	
	for i in dn_names:
		filt['delivery_note'] = i.name
		if(i.type == 'Pavers'):
			pv_exp += sum(frappe.db.get_all('Vehicle Log', filters=filt, pluck='total_vehicle_costs'))
		elif(i.type == 'Compound Wall'):
			cw_exp += sum(frappe.db.get_all('Vehicle Log', filters=filt, pluck='total_vehicle_costs'))

	for i in si_names:
		if(i.type == 'Pavers'):
			pv_exp += sum(frappe.db.get_all('Vehicle Log', filters=filt, pluck='total_vehicle_costs'))
		elif(i.type == 'Compound Wall'):
			cw_exp += sum(frappe.db.get_all('Vehicle Log', filters=filt, pluck='total_vehicle_costs'))
	
	data['paver_expense'] = pv_exp
	data['cw_expense'] = cw_exp
	data['paver_sqft_cost'] = pv_exp/(data['paver_sqft'] or 1)
	data['cw_sqft_cost'] = cw_exp/(data['cw_sqft'] or 1)

	return data


def get_vehicle_mileage(vl_filt, vehicle, data):
	if('select_purpose' in vl_filt.keys()):
		del vl_filt['select_purpose']
		
	vl_filt['license_plate'] = vehicle
	vl_filt['mileage'] = ['>', 0]

	mileage = frappe.db.get_all('Vehicle Log', vl_filt, 'mileage', order_by = 'date asc', limit=1)
	data['mileage'] = mileage[0]['mileage'] if(len(mileage)) else 0

	return data
def get_data(filters={}):
	final_data = []

	vl_filt = {'docstatus':1, 'select_purpose':'Goods Supply'}
	if(filters.get('from_date')):
		vl_filt['date'] = ['>=', filters.get('from_date')]
	if(filters.get('to_date')):
		vl_filt['date'] = ['<=', filters.get('to_date')]
	if(filters.get('from_date') and filters.get('to_date')):
		vl_filt['date'] = ['between', (filters.get('from_date'), filters.get('to_date'))]
	vehicle_filter = {}
	if(filters.get('fuel_type')):
		vehicle_filter['fuel_type'] = filters.get('fuel_type')

	vehicle_list = frappe.db.get_all('Vehicle', filters=vehicle_filter, pluck='name')

	for vehicle in vehicle_list:
		data = {}
		data = get_sqft(vl_filt, vehicle)
		data = get_expense(vl_filt, vehicle, data, filters)
		data = get_vehicle_mileage(vl_filt, vehicle, data)
		final_data.append(data)
	return final_data