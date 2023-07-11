# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe, json
from frappe.model.document import Document
from ganapathy_pavers.ganapathy_pavers.doctype.daily_maintenance.daily_maintenance import get_stock_qty
from ganapathy_pavers.ganapathy_pavers.doctype.item_size_rate.item_size_rate import get_item_size_price
from frappe.utils.data import nowdate
from ganapathy_pavers import uom_conversion, get_item_price

class StockValue(Document):
	def validate(self):
		self.paver_stock_value = 0
		self.normal_paver_stock_value = 0
		self.shot_blast_paver_stock_value = 0
		self.kerb_stone_stock_value = 0
		self.compound_wall_stock_value = 0
		self.raw_material_stock_value = 0

		self.paver_stock_qty = 0
		self.normal_paver_stock_qty = 0
		self.shot_blast_paver_stock_qty = 0
		self.kerb_stone_stock_qty = 0
		self.compound_wall_stock_qty = 0
		self.raw_material_stock_qty = 0

		self.paver_stock_nos = 0
		self.normal_paver_stock_nos = 0
		self.shot_blast_paver_stock_nos = 0
		self.kerb_stone_stock_nos = 0
		self.compound_wall_stock_nos = 0
		self.raw_material_stock_nos = 0

		self.paver_stock_sqft = 0
		self.normal_paver_stock_sqft = 0
		self.shot_blast_paver_stock_sqft = 0
		self.kerb_stone_stock_sqft = 0
		self.compound_wall_stock_sqft = 0
		self.raw_material_stock_sqft = 0

		self.paver_stock_bundle = 0
		self.normal_paver_stock_bundle = 0
		self.shot_blast_paver_stock_bundle = 0
		self.kerb_stone_stock_bundle = 0
		self.compound_wall_stock_bundle = 0
		self.raw_material_stock_bundle = 0

		for row in self.paver_stock:
			row.amount = (row.qty or 0) * (row.rate or 0)
			if row.finish=='Normal':
				self.normal_paver_stock_value += row.amount or 0
				self.normal_paver_stock_qty += row.qty or 0
				self.normal_paver_stock_nos += row.nos or 0
				self.normal_paver_stock_sqft += row.sqft or 0
				self.normal_paver_stock_bundle += row.bundle or 0

			elif row.finish=='Shot Blast':
				self.shot_blast_paver_stock_value += row.amount or 0
				self.shot_blast_paver_stock_qty += row.qty or 0
				self.shot_blast_paver_stock_nos += row.nos or 0
				self.shot_blast_paver_stock_sqft += row.sqft or 0
				self.shot_blast_paver_stock_bundle += row.bundle or 0

			self.paver_stock_value += row.amount or 0
			self.paver_stock_qty += row.qty or 0
			self.paver_stock_nos += row.nos or 0
			self.paver_stock_sqft += row.sqft or 0
			self.paver_stock_bundle += row.bundle or 0

		for row in self.kerb_stone_stock:
			row.amount = (row.qty or 0) * (row.rate or 0)
			self.kerb_stone_stock_value += row.amount or 0
			self.kerb_stone_stock_qty += row.qty or 0
			self.kerb_stone_stock_nos += row.nos or 0
			self.kerb_stone_stock_sqft += row.sqft or 0
			self.kerb_stone_stock_bundle += row.bundle or 0
		
		for row in self.cw_stock:
			row.amount = (row.qty or 0) * (row.rate or 0)
			self.compound_wall_stock_value += row.amount or 0
			self.compound_wall_stock_qty += row.qty or 0
			self.compound_wall_stock_nos += row.nos or 0
			self.compound_wall_stock_sqft += row.sqft or 0
			self.compound_wall_stock_bundle += row.bundle or 0
		
		for row in self.raw_material_stock:
			row.amount = (row.qty or 0) * (row.rate or 0)
			self.raw_material_stock_value += row.amount or 0
			self.raw_material_stock_qty += row.qty or 0
			self.raw_material_stock_nos += row.nos or 0
			self.raw_material_stock_sqft += row.sqft or 0
			self.raw_material_stock_bundle += row.bundle or 0
		
		self.total_stock_qty = self.paver_stock_qty + self.kerb_stone_stock_qty + self.compound_wall_stock_qty + self.raw_material_stock_qty
		self.total_stock_value = self.paver_stock_value + self.kerb_stone_stock_value + self.compound_wall_stock_value + self.raw_material_stock_value
		self.total_stock_nos = self.paver_stock_nos + self.kerb_stone_stock_nos + self.compound_wall_stock_nos + self.raw_material_stock_nos
		self.total_stock_sqft = self.paver_stock_sqft + self.kerb_stone_stock_sqft + self.compound_wall_stock_sqft + self.raw_material_stock_sqft
		self.total_stock_bundle = self.paver_stock_bundle + self.kerb_stone_stock_bundle + self.compound_wall_stock_bundle + self.raw_material_stock_bundle

@frappe.whitelist()
def get_items(unit='', item_group='', cw_type = '', date='', time = '23:59:59', paver_cw_warehouse=[], rm_warehouse=[], ignore_empty_item_size=False):
	default_price_list = frappe.db.get_value("Stock Defaults", unit, 'price_list')
	
	if not frappe.db.get_all('Stock Defaults', {'unit': unit}):
		frappe.throw(f"""Please create <a href="/app/stock-defaults/"><b>Stock Defaults</b></a> for <b>{unit}</b>""")

	def get_default_price_list():
		return default_price_list or frappe.throw(f"""Please Enter <b>Price List</b> in <a href='/app/stock-defaults/{unit}'><b>Stock Defaults: {unit}</b></a>""")

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
		'raw_material_stock': [],
		'kerb_stone_stock': [],
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
	
	item_filters += f""" and 
		CASE 
			WHEN item.item_group = 'Raw Material'
				THEN item.name in (
					SELECT 
						dsm_rm.item_code
					FROM `tabDSM Items` dsm_rm
					WHERE
						dsm_rm.parenttype = 'Stock Defaults' and
						dsm_rm.parent = '{unit}'
				)
			ELSE 1=1
		END
	"""

	items = frappe.db.sql(f"""
		SELECT
		    name,
			item.item_size,
			CASE
		    	WHEN item.name like '%kerb%stone%' 
		    		THEN 'Kerb Stone'
		       	ELSE item.item_group
		    END as item_group,
			item.compound_wall_type,
			IFNULL(item.dsm_uom, item.stock_uom) as uom,
			(
				CASE
					WHEN item.item_group = 'Pavers'
						THEN IFNULL((
								SELECT
									iva.attribute_value
								FROM `tabItem Variant Attribute` iva
								WHERE
									iva.parenttype = "Item" and
									iva.parent = item.name and
									iva.attribute = "Finish"
								LIMIT 1
							), '')
		       		ELSE ''
		       	END
		    ) as finish,
		    (
				CASE
					WHEN item.item_group = 'Pavers'
						THEN IFNULL((
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
							), '')
		       		ELSE ''
		       	END
		    ) as colour,
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
		elif item.get('item_group') == 'Kerb Stone':
			res['kerb_stone_stock'].append(item)

	for item in res['paver_stock']:
		item['qty'] = get_stock_qty(
			item_code=item.get('name'),
			warehouse=paver_cw_warehouse,
			date=nowdate(),
			time = time,
			to_uom=item.get('uom'),
			uom_conv=False
		)
		item['nos'] = uom_conversion(item=item.get('name'), from_uom=item.get('uom'), from_qty=item.get("qty"), to_uom="Nos", throw_err=False)
		item['sqft'] = uom_conversion(item=item.get('name'), from_uom=item.get('uom'), from_qty=item.get("qty"), to_uom="SQF", throw_err=False)
		item['bundle'] = uom_conversion(item=item.get('name'), from_uom=item.get('uom'), from_qty=item.get("qty"), to_uom="Bdl", throw_err=False)

		rate = ()
		if item.get('item_size'):
			filters = {}
			filters['item_group'] = item.get('item_group')

			if item.get('item_group') == 'Pavers':
				filters['finish'] = item.get('finish')
				filters['colour'] = item.get('colour')
			elif item.get('item_group') == 'Compound Walls' and item.get('compound_wall_type') in ['Post', 'Corner Post', 'Fencing Post']:
				filters['post_type'] = item.get('compound_wall_type')

			rate = get_item_size_price(item_size=item.get('item_size'), item_code=item.get('name'), posting_date=date, to_uom=item.get('uom'), filters=filters)
		else:
			rate = get_item_price(args={
					'batch_no': '',
					'posting_date': date, 
					'price_list': get_default_price_list()
				}, 
				item_code=item.get('name'), 
				to_uom = item.get('uom'))
			
		if rate and rate[0] and len(rate[0])>1:
			item['rate'] = rate[0][1]
	
	for item in res['kerb_stone_stock']:
		item['qty'] = get_stock_qty(
			item_code=item.get('name'),
			warehouse=paver_cw_warehouse,
			date=nowdate(),
			time = time,
			to_uom=item.get('uom'),
			uom_conv=False
		)
		item['nos'] = uom_conversion(item=item.get('name'), from_uom=item.get('uom'), from_qty=item.get("qty"), to_uom="Nos", throw_err=False)
		item['sqft'] = uom_conversion(item=item.get('name'), from_uom=item.get('uom'), from_qty=item.get("qty"), to_uom="SQF", throw_err=False)
		item['bundle'] = uom_conversion(item=item.get('name'), from_uom=item.get('uom'), from_qty=item.get("qty"), to_uom="Bdl", throw_err=False)
		
		rate = ()
		if item.get('item_size'):
			filters = {}
			filters['item_group'] = item.get('item_group')

			if item.get('item_group') == 'Kerb Stone':
				filters['finish'] = item.get('finish')
				filters['colour'] = item.get('colour')
			elif item.get('item_group') == 'Compound Walls' and item.get('compound_wall_type') in ['Post', 'Corner Post', 'Fencing Post']:
				filters['post_type'] = item.get('compound_wall_type')

			rate = get_item_size_price(item_size=item.get('item_size'), item_code=item.get('name'), posting_date=date, to_uom=item.get('uom'), filters=filters)
		else:
			rate = get_item_price(args={
					'batch_no': '',
					'posting_date': date, 
					'price_list': get_default_price_list()
				}, 
				item_code=item.get('name'), 
				to_uom = item.get('uom'))
			
		if rate and rate[0] and len(rate[0])>1:
			item['rate'] = rate[0][1]
	
	for item in res['cw_stock']:
		item['qty'] = get_stock_qty(
			item_code=item.get('name'),
			warehouse=paver_cw_warehouse,
			date=nowdate(),
			time = time,
			to_uom=item.get('uom'),
			uom_conv=False
		)
		item['nos'] = uom_conversion(item=item.get('name'), from_uom=item.get('uom'), from_qty=item.get("qty"), to_uom="Nos", throw_err=False)
		item['sqft'] = uom_conversion(item=item.get('name'), from_uom=item.get('uom'), from_qty=item.get("qty"), to_uom="SQF", throw_err=False)
		item['bundle'] = uom_conversion(item=item.get('name'), from_uom=item.get('uom'), from_qty=item.get("qty"), to_uom="Bdl", throw_err=False)

		rate = ()
		if item.get('item_size'):
			filters = {}
			filters['item_group'] = item.get('item_group')

			if item.get('item_group') == 'Pavers':
				filters['finish'] = item.get('finish')
				filters['colour'] = item.get('colour')
			elif item.get('item_group') == 'Compound Walls' and item.get('compound_wall_type') in ['Post', 'Corner Post', 'Fencing Post']:
				filters['post_type'] = item.get('compound_wall_type')

			rate = get_item_size_price(item_size=item.get('item_size'), item_code=item.get('name'), posting_date=date, to_uom=item.get('uom'), filters=filters)
		else:
			rate = get_item_price(args={
					'batch_no': '',
					'posting_date': date, 
					'price_list': get_default_price_list()
				}, 
				item_code=item.get('name'), 
				to_uom = item.get('uom'))
		
		if rate and rate[0] and len(rate[0])>1:
			item['rate'] = rate[0][1]
	
	for item in res['raw_material_stock']:
		item['qty'] = get_stock_qty(
			item_code=item.get('name'),
			warehouse=rm_warehouse,
			date=nowdate(),
			time = time,
			to_uom=item.get('uom'),
			uom_conv=False
		)
		item['nos'] = uom_conversion(item=item.get('name'), from_uom=item.get('uom'), from_qty=item.get("qty"), to_uom="Nos", throw_err=False)
		item['sqft'] = uom_conversion(item=item.get('name'), from_uom=item.get('uom'), from_qty=item.get("qty"), to_uom="SQF", throw_err=False)
		item['bundle'] = uom_conversion(item=item.get('name'), from_uom=item.get('uom'), from_qty=item.get("qty"), to_uom="Bdl", throw_err=False)

		rate = ()
		if item.get('item_size'):
			filters = {}
			filters['item_group'] = item.get('item_group')

			if item.get('item_group') == 'Pavers':
				filters['finish'] = item.get('finish')
				filters['colour'] = item.get('colour')
			elif item.get('item_group') == 'Compound Walls' and item.get('compound_wall_type') in ['Post', 'Corner Post', 'Fencing Post']:
				filters['post_type'] = item.get('compound_wall_type')

			rate = get_item_size_price(item_size=item.get('item_size'), item_code=item.get('name'), posting_date=date, to_uom=item.get('uom'), filters=filters)
		else:
			rate = get_item_price(args={
					'batch_no': '',
					'posting_date': date, 
					'price_list': get_default_price_list()
				}, 
				item_code=item.get('name'), 
				to_uom = item.get('uom'))
		
		if rate and rate[0] and len(rate[0])>1:
			item['rate'] = rate[0][1]

	return group_item_sizes(res)
	

def group_item_sizes(res):
	paver = res['paver_stock']
	kerb_stone = res['kerb_stone_stock']
	cw = res['cw_stock']
	raw_material = res['raw_material_stock']

	paver_res = {}
	kerb_stone_res = {}
	cw_res =  {}
	raw_material_res ={}

	for row in paver:
		key = f"""{row.get('item_size') or row.get('name')}--------{row.get('colour_type') or ""}---------{row.get('uom')}--------------{row.get('rate')}"""
		if key not in paver_res:
			paver_res[key or ''] = {
				'size': row.get('item_size') or '',
				'type': row.get('colour_type'),
				'finish': row.get('finish'),
				'colour': row.get('colour'),
				'item_code': (row.get('name') or '') if not row.get('item_size') else '',
				'qty': row.get('qty') or 0,
				'nos': row.get('nos') or 0,
				'sqft': row.get('sqft') or 0,
				'bundle': row.get('bundle') or 0,
				'uom': row.get('uom') or '',
				'rate': row.get('rate') or 0,
				'amount': (row.get('qty') or 0) * (row.get('rate') or 0),
			}
		else:
			paver_res[key or '']['qty'] += row.get('qty') or 0
			paver_res[key or '']['nos'] += row.get('nos') or 0
			paver_res[key or '']['sqft'] += row.get('sqft') or 0
			paver_res[key or '']['bundle'] += row.get('bundle') or 0
	
	for row in kerb_stone:
		key = f"""{row.get('item_size') or row.get('name')}--------{row.get('colour_type') or ""}---------{row.get('uom')}--------------{row.get('rate')}"""
		if key not in kerb_stone_res:
			kerb_stone_res[key or ''] = {
				'size': row.get('item_size') or '',
				'type': row.get('colour_type'),
				'finish': row.get('finish'),
				'colour': row.get('colour'),
				'item_code': (row.get('name') or '') if not row.get('item_size') else '',
				'qty': row.get('qty') or 0,
				'nos': row.get('nos') or 0,
				'sqft': row.get('sqft') or 0,
				'bundle': row.get('bundle') or 0,
				'uom': row.get('uom') or '',
				'rate': row.get('rate') or 0,
				'amount': (row.get('qty') or 0) * (row.get('rate') or 0),
			}
		else:
			kerb_stone_res[key or '']['qty'] += row.get('qty') or 0
			kerb_stone_res[key or '']['nos'] += row.get('nos') or 0
			kerb_stone_res[key or '']['sqft'] += row.get('sqft') or 0
			kerb_stone_res[key or '']['bundle'] += row.get('bundle') or 0
	
	for row in cw:
		key = f"{row.get('item_size') or row.get('name')}---------{row.get('uom')}--------------{row.get('rate')}"
		if key not in cw_res:
			cw_res[key or ''] = {
				'size': row.get('item_size') or '',
				'item_code': (row.get('name') or '') if not row.get('item_size') else '',
				'type': row.get('compound_wall_type'),
				'qty': row.get('qty') or 0,
				'nos': row.get('nos') or 0,
				'sqft': row.get('sqft') or 0,
				'bundle': row.get('bundle') or 0,
				'uom': row.get('uom') or '',
				'rate': row.get('rate') or 0,
				'amount': (row.get('qty') or 0) * (row.get('rate') or 0),
			}
		else:
			cw_res[key or '']['qty'] += row.get('qty') or 0
			cw_res[key or '']['nos'] += row.get('nos') or 0
			cw_res[key or '']['sqft'] += row.get('sqft') or 0
			cw_res[key or '']['bundle'] += row.get('bundle') or 0
	
	for row in raw_material:
		key = f"{row.get('item_size') or row.get('name')}---------{row.get('uom')}--------------{row.get('rate')}"
		if key not in raw_material_res:
			raw_material_res[key or ''] = {
				'size': row.get('item_size') or '',
				'item_code': (row.get('name') or '') if not row.get('item_size') else '',
				'qty': row.get('qty') or 0,
				'nos': row.get('nos') or 0,
				'sqft': row.get('sqft') or 0,
				'bundle': row.get('bundle') or 0,
				'uom': row.get('uom') or '',
				'rate': row.get('rate') or 0,
				'amount': (row.get('qty') or 0) * (row.get('rate') or 0),
			}
		else:
			raw_material_res[key or '']['qty'] += row.get('qty') or 0
			raw_material_res[key or '']['nos'] += row.get('nos') or 0
			raw_material_res[key or '']['sqft'] += row.get('sqft') or 0
			raw_material_res[key or '']['bundle'] += row.get('bundle') or 0

	res = frappe._dict({
		'paver_stock': sorted(list(paver_res.values()), key=lambda x: x.get('finish') or ''),
		'kerb_stone_stock': sorted(list(kerb_stone_res.values()), key=lambda x: x.get('finish') or ''),
		'cw_stock': list(cw_res.values()),
		'raw_material_stock': list(raw_material_res.values())
	})

	res.paver_stock_value = 0
	res.normal_paver_stock_value = 0
	res.shot_blast_paver_stock_value = 0
	res.kerb_stone_stock_value = 0
	res.compound_wall_stock_value = 0
	res.raw_material_stock_value = 0

	res.paver_stock_qty = 0
	res.normal_paver_stock_qty = 0
	res.shot_blast_paver_stock_qty = 0
	res.kerb_stone_stock_qty = 0
	res.compound_wall_stock_qty = 0
	res.raw_material_stock_qty = 0

	res.paver_stock_nos = 0
	res.normal_paver_stock_nos = 0
	res.shot_blast_paver_stock_nos = 0
	res.kerb_stone_stock_nos = 0
	res.compound_wall_stock_nos = 0
	res.raw_material_stock_nos = 0

	res.paver_stock_sqft = 0
	res.normal_paver_stock_sqft = 0
	res.shot_blast_paver_stock_sqft = 0
	res.kerb_stone_stock_sqft = 0
	res.compound_wall_stock_sqft = 0
	res.raw_material_stock_sqft = 0

	res.paver_stock_bundle = 0
	res.normal_paver_stock_bundle = 0
	res.shot_blast_paver_stock_bundle = 0
	res.kerb_stone_stock_bundle = 0
	res.compound_wall_stock_bundle = 0
	res.raw_material_stock_bundle = 0

	for row in res.paver_stock:
		row['amount'] = (row.get('qty') or 0) * (row.get('rate') or 0)

		if row.get('finish') == 'Normal':
			res.normal_paver_stock_value += row.get('amount') or 0
			res.normal_paver_stock_qty += row.get('qty') or 0
			res.normal_paver_stock_nos += row.get('nos') or 0
			res.normal_paver_stock_sqft += row.get('sqft') or 0
			res.normal_paver_stock_bundle += row.get('bundle') or 0

		elif row.get('finish') == 'Shot Blast':
			res.shot_blast_paver_stock_value += row.get('amount') or 0
			res.shot_blast_paver_stock_qty += row.get('qty') or 0
			res.shot_blast_paver_stock_nos += row.get('nos') or 0
			res.shot_blast_paver_stock_sqft += row.get('sqft') or 0
			res.shot_blast_paver_stock_bundle += row.get('bundle') or 0

		res.paver_stock_value += row.get('amount') or 0
		res.paver_stock_qty += row.get('qty') or 0
		res.paver_stock_nos += row.get('nos') or 0
		res.paver_stock_sqft += row.get('sqft') or 0
		res.paver_stock_bundle += row.get('bundle') or 0
	
	for row in res.kerb_stone_stock:
		row['amount'] = (row.get('qty') or 0) * (row.get('rate') or 0)
		res.kerb_stone_stock_value += row.get('amount') or 0
		res.kerb_stone_stock_qty += row.get('qty') or 0
		res.kerb_stone_stock_nos += row.get('nos') or 0
		res.kerb_stone_stock_sqft += row.get('sqft') or 0
		res.kerb_stone_stock_bundle += row.get('bundle') or 0
	
	for row in res.cw_stock:
		row['amount'] = (row.get('qty') or 0) * (row.get('rate') or 0)
		res.compound_wall_stock_value += row.get('amount') or 0
		res.compound_wall_stock_qty += row.get('qty') or 0
		res.compound_wall_stock_nos += row.get('nos') or 0
		res.compound_wall_stock_sqft += row.get('sqft') or 0
		res.compound_wall_stock_bundle += row.get('bundle') or 0
	
	for row in res.raw_material_stock:
		row['amount'] = (row.get('qty') or 0) * (row.get('rate') or 0)
		res.raw_material_stock_value += row.get('amount') or 0
		res.raw_material_stock_qty += row.get('qty') or 0
		res.raw_material_stock_nos += row.get('nos') or 0
		res.raw_material_stock_sqft += row.get('sqft') or 0
		res.raw_material_stock_bundle += row.get('bundle') or 0
	
	res.total_stock_qty = res.paver_stock_qty + res.kerb_stone_stock_qty + res.compound_wall_stock_qty + res.raw_material_stock_qty
	res.total_stock_value = res.paver_stock_value + res.kerb_stone_stock_value + res.compound_wall_stock_value + res.raw_material_stock_value
	res.total_stock_nos = res.paver_stock_nos + res.kerb_stone_stock_nos + res.compound_wall_stock_nos + res.raw_material_stock_nos
	res.total_stock_sqft = res.paver_stock_sqft + res.kerb_stone_stock_sqft + res.compound_wall_stock_sqft + res.raw_material_stock_sqft
	res.total_stock_bundle = res.paver_stock_bundle + res.kerb_stone_stock_bundle + res.compound_wall_stock_bundle + res.raw_material_stock_bundle
	
	return res