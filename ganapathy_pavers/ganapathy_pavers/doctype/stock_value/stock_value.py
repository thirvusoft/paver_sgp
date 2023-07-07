# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe, json
from frappe.model.document import Document
from ganapathy_pavers.ganapathy_pavers.doctype.daily_maintenance.daily_maintenance import get_stock_qty
from ganapathy_pavers.ganapathy_pavers.doctype.item_size_rate.item_size_rate import get_item_size_price
from frappe.utils.data import nowdate

class StockValue(Document):
	def validate(self):
		self.paver_stock_value = 0
		self.compound_wall_stock_value = 0
		self.raw_material_stock_value = 0

		self.paver_stock_qty = 0
		self.compound_wall_stock_qty = 0
		self.raw_material_stock_qty = 0

		for row in self.paver_stock:
			row.amount = (row.qty or 0) * (row.rate or 0)
			self.paver_stock_value += row.amount or 0
			self.paver_stock_qty += row.qty or 0
		
		for row in self.cw_stock:
			row.amount = (row.qty or 0) * (row.rate or 0)
			self.compound_wall_stock_value += row.amount or 0
			self.compound_wall_stock_qty += row.qty or 0
		
		for row in self.raw_material_stock:
			row.amount = (row.qty or 0) * (row.rate or 0)
			self.raw_material_stock_value += row.amount or 0
			self.raw_material_stock_qty += row.qty or 0
		
		self.total_stock_qty = self.paver_stock_qty + self.compound_wall_stock_qty + self.raw_material_stock_qty
		self.total_stock_value = self.paver_stock_value + self.compound_wall_stock_value + self.raw_material_stock_value

@frappe.whitelist()
def get_items(item_group='', cw_type = '', date='', paver_cw_warehouse=[], rm_warehouse=[], ignore_empty_item_size=False):
	try:
		if isinstance(ignore_empty_item_size, str):
			ignore_empty_item_size = int(ignore_empty_item_size)
	except:
		frappe.log_error(title='STOCK VALUE', message=f"""
		   item_group: {item_group}\ncw_type: {cw_type }\ndate: {date}\npaver_cw_warehouse: {paver_cw_warehouse}\nrm_warehouse: {rm_warehouse}\nignore_empty_item_size: {ignore_empty_item_size}\n
		   \n
		   {frappe.get_traceback()}
		   """)
	res = {
		'paver_stock': [],
		'cw_stock': [],
		'raw_material_stock': []
	}
	if isinstance(paver_cw_warehouse, str):
		paver_cw_warehouse = json.loads(paver_cw_warehouse)
	if isinstance(rm_warehouse, str):
		rm_warehouse = json.loads(rm_warehouse)
	
	item_filters = " item.is_stock_item = 1 and item.disabled = 0 and item.has_variants = 0 "
	if ignore_empty_item_size:
		item_filters += """ and 
		CASE 
			WHEN item.item_group = "Pavers" THEN IFNULL(item.item_size, '') != ''
			ELSE 1=1
		END
		"""
	if item_group:
		item_filters += f" and item.item_group = '{item_group}' "
	
		if item_group == 'Compound Walls' and cw_type:
			item_filters += f" and item.compound_wall_type = '{cw_type}' "
	
	items = frappe.db.sql(f"""
		SELECT
		    name,
			item.item_size,
			item.item_group,
			item.compound_wall_type,
			item.stock_uom as uom,
		    (
		    	CASE
					WHEN item.item_group = 'Pavers'
		       			THEN CONCAT(
		       				IFNULL((
								SELECT
		       						CONCAT(iva.attribute_value, ' ')
		       					FROM `tabItem Variant Attribute` iva
		       					WHERE
		       						iva.parenttype = "Item" and
									iva.parent = item.name and
		       						iva.attribute = "Finish"
		    					LIMIT 1
							), ''),
							CASE 
		       					WHEN (
		       						SELECT
										iva.attribute_value
									FROM `tabItem Variant Attribute` iva
									WHERE
										iva.parenttype = "Item" and
										iva.parent = item.name and
										iva.attribute = "Colour"
									LIMIT 1
		       					) = "Grey"
									THEN "Grey"
		    					WHEN (
		       						SELECT
										COUNT(iva.attribute_value)
									FROM `tabItem Variant Attribute` iva
									WHERE
										iva.parenttype = "Item" and
										iva.parent = item.name and
										iva.attribute = "Colour"
									LIMIT 1
		       					)>0 
		       						THEN "Colour"
		       					ELSE ""
		       				END
						)
		       				
		       		ELSE ''
		       	END
			) as colour_type
		from `tabItem` item
		where
		    {item_filters}
		ORDER BY CAST(REGEXP_REPLACE(item.item_size, '[^0-9]', '') AS UNSIGNED)
	""", as_dict=True)

	for item in items:
		if item.get('item_group') == 'Pavers':
			res['paver_stock'].append(item)
		elif item.get('item_group') == "Compound Walls":
			res['cw_stock'].append(item)
		elif item.get('item_group') == "Raw Material":
			res["raw_material_stock"].append(item)

	for item in res['paver_stock']:
		item['qty'] = get_stock_qty(
			item_code=item.get('name'),
			warehouse=paver_cw_warehouse,
			date=nowdate(),
			time = "23:59:59",
			uom_conv=False
		)
		if item.get('item_size'):
			rate = get_item_size_price(item_size=item.get('item_size'), posting_date=date)
			if rate and rate[0] and len(rate[0])>1:
				item['rate'] = rate[0][1]
	
	for item in res['cw_stock']:
		item['qty'] = get_stock_qty(
			item_code=item.get('name'),
			warehouse=paver_cw_warehouse,
			date=nowdate(),
			time = "23:59:59",
			uom_conv=False
		)
		if item.get('item_size'):
			rate = get_item_size_price(item_size=item.get('item_size'), posting_date=date)
			if rate and rate[0] and len(rate[0])>1:
				item['rate'] = rate[0][1]
	
	for item in res['raw_material_stock']:
		item['qty'] = get_stock_qty(
			item_code=item.get('name'),
			warehouse=rm_warehouse,
			date=nowdate(),
			time = "23:59:59",
			uom_conv=False
		)
		if item.get('item_size'):
			rate = get_item_size_price(item_size=item.get('item_size'), posting_date=date)
			if rate and rate[0] and len(rate[0])>1:
				item['rate'] = rate[0][1]

	return group_item_sizes(res)
	

def group_item_sizes(res):
	paver = res['paver_stock']
	cw = res['cw_stock']
	raw_material = res['raw_material_stock']

	paver_res = {}
	cw_res =  {}
	raw_material_res ={}

	for row in paver:
		key = f"""{row.get('item_size') or row.get('name')}--------{row.get('colour_type') or ""}"""
		if key not in paver_res:
			paver_res[key or ''] = {
				'size': row.get('item_size') or '',
				'type': row.get('colour_type'),
				'item_code': (row.get('name') or '') if not row.get('item_size') else '',
				'qty': row.get('qty') or 0,
				'uom': row.get('uom') or '',
				'rate': row.get('rate') or 0,
				'amount': (row.get('qty') or 0) * (row.get('rate') or 0),
			}
		else:
			paver_res[key or '']['qty'] += row.get('qty') or 0
	
	for row in cw:
		key = row.get('item_size') or row.get('name')
		if key not in cw_res:
			cw_res[key or ''] = {
				'size': row.get('item_size') or '',
				'item_code': (row.get('name') or '') if not row.get('item_size') else '',
				'type': row.get('compound_wall_type'),
				'qty': row.get('qty') or 0,
				'uom': row.get('uom') or '',
				'rate': row.get('rate') or 0,
				'amount': (row.get('qty') or 0) * (row.get('rate') or 0),
			}
		else:
			cw_res[key or '']['qty'] += row.get('qty') or 0
	
	for row in raw_material:
		key = row.get('item_size') or row.get('name')
		if key not in raw_material_res:
			raw_material_res[key or ''] = {
				'size': row.get('item_size') or '',
				'item_code': (row.get('name') or '') if not row.get('item_size') else '',
				'qty': row.get('qty') or 0,
				'uom': row.get('uom') or '',
				'rate': row.get('rate') or 0,
				'amount': (row.get('qty') or 0) * (row.get('rate') or 0),
			}
		else:
			raw_material_res[key or '']['qty'] += row.get('qty') or 0

	res = frappe._dict({
		'paver_stock': list(paver_res.values()),
		'cw_stock': list(cw_res.values()),
		'raw_material_stock': list(raw_material_res.values())
	})

	res.paver_stock_value = 0
	res.compound_wall_stock_value = 0
	res.raw_material_stock_value = 0

	res.paver_stock_qty = 0
	res.compound_wall_stock_qty = 0
	res.raw_material_stock_qty = 0

	for row in res.paver_stock:
		row['amount'] = (row.get('qty') or 0) * (row.get('rate') or 0)
		res.paver_stock_value += row.get('amount') or 0
		res.paver_stock_qty += row.get('qty') or 0
	
	for row in res.cw_stock:
		row['amount'] = (row.get('qty') or 0) * (row.get('rate') or 0)
		res.compound_wall_stock_value += row.get('amount') or 0
		res.compound_wall_stock_qty += row.get('qty') or 0
	
	for row in res.raw_material_stock:
		row['amount'] = (row.get('qty') or 0) * (row.get('rate') or 0)
		res.raw_material_stock_value += row.get('amount') or 0
		res.raw_material_stock_qty += row.get('qty') or 0
	
	res.total_stock_qty = res.paver_stock_qty + res.compound_wall_stock_qty + res.raw_material_stock_qty
	res.total_stock_value = res.paver_stock_value + res.compound_wall_stock_value + res.raw_material_stock_value
	
	return res