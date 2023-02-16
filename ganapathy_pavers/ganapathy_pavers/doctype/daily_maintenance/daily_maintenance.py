# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import json
from erpnext.stock.stock_ledger import get_previous_sle
import frappe
from frappe.model.document import Document
from frappe.utils.data import nowdate, nowtime
from ganapathy_pavers import uom_conversion

def get_stock_qty(item_code, warehouse):
	qty = get_previous_sle({
		'item_code': item_code,
		'warehouse_condition': f""" warehouse in {tuple(warehouse)}""" if len(warehouse)>1 else f""" warehouse = '{warehouse[0]}'""",
		'posting_date': nowdate(),
		'posting_time': nowtime()
	}).get('qty_after_transaction') or 0
	return dsm_uom_conversion(item_code, qty)

def dsm_uom_conversion(item, qty, uom=None):
	to_uom=frappe.db.get_value("Item", item, "dsm_uom")
	if not to_uom:
		return qty
	return uom_conversion(item=item, from_uom=uom, from_qty=qty, to_uom=to_uom)



def daily_maintenance_print_format(doc):
	html=frappe.render_template('ganapathy_pavers/ganapathy_pavers/doctype/daily_maintenance/daily_maintenance.html', {'doc':doc})
	css=f"<style>{frappe.render_template('ganapathy_pavers/ganapathy_pavers/doctype/daily_maintenance/daily_maintenance.css', {'doc':doc})}</style>"
	res=html+css
	return res
	
def get_raw_materials_for_print(doc):
	res={}
	for row in doc.raw_material_details:
		if row.machine not in res:
			res[row.machine]={'items': [], 'width': '49'}
		res[row.machine]['items'].append(row)
	if len(res)%2==1:
		res[list(res.keys())[-1]]['width']='100'
	return res

@frappe.whitelist()
def get_attendance_details(date):
	labour_employee_details= frappe.db.sql("""select count(att.name) from `tabAttendance` as att left outer join `tabEmployee` 
									as employee on att.employee=employee.name where employee.designation="Labour Worker" and att.attendance_date='{0}' and att.status="Present" """.format(date),as_list=True)
	labour_present=labour_employee_details[0][0]
	operator_employee_details= frappe.db.sql("""select count(att.name) from `tabAttendance` as att left outer join `tabEmployee` 
									as employee on att.employee=employee.name where employee.designation="Operator" and att.attendance_date='{0}' and att.status="Present" """.format(date),as_list=True)
	operator_present=operator_employee_details[0][0]
	labour_employee_details_absent= frappe.db.sql("""select count(att.name) from `tabAttendance` as att left outer join `tabEmployee` 
									as employee on att.employee=employee.name where employee.designation="Labour Worker" and att.attendance_date='{0}' and att.status="Absent" """.format(date),as_list=True)
	labour_absent=labour_employee_details_absent[0][0]
	operator_employee_details_absent= frappe.db.sql("""select count(att.name) from `tabAttendance` as att left outer join `tabEmployee` 
									as employee on att.employee=employee.name where employee.designation="Operator" and att.attendance_date='{0}' and att.status="Absent" """.format(date),as_list=True)
	operator_absent=operator_employee_details_absent[0][0]
	return {
			'labour_present': labour_present,
			'operator_present': operator_present,
			'labour_absent': labour_absent,
			'operator_absent': operator_absent
			}

class DailyMaintenance(Document):
	pass
@frappe.whitelist()
def paver_item(warehouse, date, warehouse_colour):
	warehouse = [row.get('warehouse') for row in json.loads(warehouse) if row.get('warehouse')]
	warehouse_colour=[row.get('warehouse') for row in json.loads(warehouse_colour) if row.get('warehouse')]
	item=frappe.db.get_all("Item", filters={'item_group':"Pavers",'has_variants':1},pluck='name',order_by='name')
	items_stock=[]
	total_stock={}
	#paver_item_normal
	for i in item:
		item_1=frappe.db.get_all("Item", filters=[
										['variant_of','=',i],
										["Item Variant Attribute","attribute_value",'=','Normal'],
																			])
		if item_1:
			template={'short_name':i, 'type': 'Normal'}
			for j in item_1:
				stock_qty=get_stock_qty(j.name, warehouse)

				attribute=frappe.get_doc("Item",j.name)
				colour=frappe.db.sql(f"""
					select attribute_value from `tabItem Variant Attribute` where parent='{j.name}' and parenttype='Item' and attribute='Colour'
				""")
				if colour and colour[0]:
					colour=colour[0][0].lower()
				else:
					continue
					
				if colour not in template:
					template[colour]=0
				template[colour]+=stock_qty
				if colour not in total_stock:
					total_stock[colour]=0
				total_stock[colour]+=stock_qty
			items_stock.append(template)
	#paver_item_shotblast
	items_stock_shot=[]
	total_stock_shot={}
	for i in item:
		item_2=frappe.db.get_all("Item", filters=[
										['variant_of','=',i],
										["Item Variant Attribute","attribute_value",'=','Shot Blast']
																			])
		if item_2:
			template_1={'short_name':i, 'type': 'Shot Blast'}
			for sb in item_2:
				stock_qty_sb=get_stock_qty(sb.name, warehouse)

				attribute=frappe.get_doc("Item",sb.name)
				colour_sb=frappe.db.sql(f"""
					select attribute_value from `tabItem Variant Attribute` where parent='{sb.name}' and parenttype='Item' and attribute='Colour' order by attribute_value 
				""")
				if colour_sb and colour_sb[0]:
					colour_sb=colour_sb[0][0].lower()
				else:
					continue
				if colour_sb not in template_1:
					template_1[colour_sb]=0
				template_1[colour_sb]+=stock_qty_sb
				if colour_sb not in total_stock_shot:
					total_stock_shot[colour_sb]=0
				total_stock_shot[colour_sb]+=stock_qty_sb
			items_stock_shot.append(template_1)
	
 
 	#vehicle_details
	sqf={}
	vehicle_d=frappe.db.get_all("Vehicle Log", filters={'date': date,'docstatus':1,'delivery_note':['is', 'set'] }, fields=['license_plate', 'delivery_note'], order_by="license_plate")
	if vehicle_d:
		for veh in vehicle_d:
			dn=frappe.get_doc("Delivery Note", veh['delivery_note'])
			for row in dn.items:
				if row.item_group in ["Pavers","Compound Walls"]:
					sq=uom_conversion(row.item_code, row.stock_uom, row.stock_qty, "SQF")
					if veh['license_plate'] not in sqf:
						sqf[veh['license_plate']]={'vehicle':veh['license_plate'],'sqft':0}
					sqf[veh['license_plate']]['sqft']+=sq
	vehicle_s=frappe.db.get_all("Vehicle Log", filters={'date': date,'docstatus':1,'sales_invoice':['is', 'set'] }, fields=['license_plate', 'sales_invoice'])
	if vehicle_s:
		for veh in vehicle_s:
			si=frappe.get_doc("Sales Invoice", veh['sales_invoice'])
			for row in si.items:
				if row.item_group in ["Pavers","Compound Walls"]:
					sq=uom_conversion(row.item_code, row.stock_uom, row.stock_qty, "SQF")
					if veh['license_plate'] not in sqf:
						sqf[veh['license_plate']]={'vehicle':veh['license_plate'],'sqft':0}
					sqf[veh['license_plate']]['sqft']+=sq
	
 	
  	#machine_details
	production=[]
	paver=frappe.db.sql(f"""select item_to_manufacture as item, work_station as machine, sum(production_sqft) as sqft,
	sum(no_of_racks) as rack from `tabMaterial Manufacturing` where date(from_time) = '{date}' group by item_to_manufacture, work_station order by work_station, item_to_manufacture""", as_dict=True)
	if paver:
		production+=paver
		production+=frappe.db.sql(f"""select "Total Stock" as item, sum(production_sqft) as sqft,
	sum(no_of_racks) as rack from `tabMaterial Manufacturing` where date(from_time) = '{date}' """, as_dict=True)
	
	cw=frappe.db.sql(f"""select cwi.item as item, cwi.workstation as machine, cwi.production_sqft as sqft from `tabCW Items` as cwi
	 	left outer join `tabCW Manufacturing` as cw on cwi.parent=cw.name where cw.molding_date='{date}' and cw.docstatus!=2 group by cwi.item, cwi.workstation order by cwi.workstation, cwi.item;
	""", as_dict=True)
	if cw:
		production+=cw
		production+=frappe.db.sql(f"""select "Total Stock" as item, sum(cwi.production_sqft) as sqft from `tabCW Items` as cwi
	 	left outer join `tabCW Manufacturing` as cw on cwi.parent=cw.name where cw.molding_date='{date}' and cw.docstatus!=2;
	""", as_dict=True)
	

	#compound_wall_items
	compound_item=frappe.db.get_all("Item", filters={'item_group':"Compound Walls","compound_wall_type":"Post",'item_name':['like',"%FEET%"]},pluck='name',order_by='name')
	post_item={}
	if compound_item:
		# for i in compound_item:
			ci_wo= frappe.db.get_all("Item", filters=[['item_name','like','%WITHOUT%'],['item_name','not like','%CORNER%'],['item_name','not like','%FENCING%'],['name','in',compound_item],['disabled','=',0]])
			if ci_wo:
				for j in ci_wo:
					post=j['name'].split('FEET')[0]+ 'FEET'
					if (post + "Normal") in post_item and post_item[post + "Normal"]['type']=='Normal':
						if 'wo_bolt' in post_item[post + "Normal"]:
							post_item[post + "Normal"]['wo_bolt']+=get_stock_qty(j.name, warehouse) or 0
						else:
							post_item[post + "Normal"]['wo_bolt']=get_stock_qty(j.name, warehouse) or 0

						# post_item[post]['post_length']=j['name'].split('FEET')[0]+ 'FEET'
					else:
						post_item[post + "Normal"]={'wo_bolt':get_stock_qty(j.name, warehouse) or 0, 'post_length':post, 'type':'Normal'}
			ci_w= frappe.db.get_all("Item", filters=[['item_name','not like','%WITHOUT%'], ['item_name','not like','%CORNER%'],['item_name','not like','%FENCING%'], ['name','in',compound_item],['disabled', '=', 0]],order_by='item_name')
			
			if ci_w:
				for j in ci_w:
					post=j['name'].split('FEET')[0]+ 'FEET'
					if (post + "Normal") in post_item and post_item[post + "Normal"]['type']=='Normal':
						if 'with_bolt' in post_item[post + "Normal"]:
							post_item[post + "Normal"]['with_bolt']+=get_stock_qty(j.name, warehouse) or 0
						else:
							post_item[post + "Normal"]['with_bolt']=get_stock_qty(j.name, warehouse) or 0

      
						# post_item[post]['post_length']=j['name'].split('FEET')[0]+ 'FEET'
					else:
						post_item[post + "Normal"]={'with_bolt':get_stock_qty(j.name, warehouse) or 0, 'post_length':post, 'type':'Normal'}
			
			ci_wo_cp= frappe.db.get_all("Item", filters=[['item_name','like','%CORNER%'],['item_name','like','%WITHOUT%'],['item_name','not like','%FENCING%'], ['name', 'in',compound_item],['disabled', '=',0]])
			if ci_wo_cp:
				for j in ci_wo_cp:
					post=j['name'].split('FEET')[0]+ 'FEET'
					if (post + "Normal") in post_item and post_item[post + "Normal"]['type']=='Normal':
						if 'pc_wo_bolt' in post_item[post + "Normal"]:
							post_item[post + "Normal"]['pc_wo_bolt']+=get_stock_qty(j.name, warehouse) or 0
						else:
							post_item[post + "Normal"]['pc_wo_bolt']=get_stock_qty(j.name, warehouse) or 0

					else:
						post_item[post + "Normal"]={'pc_wo_bolt':get_stock_qty(j.name, warehouse) or 0, 'post_length':post, 'type':'Normal'}
			
   
			ci_w_cp= frappe.db.get_all("Item", filters=[['item_name','not like','%FENCING%'],['item_name','like','%CORNER%'],['item_name','not like','%WITHOUT%'], ['name', 'in',compound_item],['disabled', '=',0]])
			if ci_w_cp:
				template={'post_length':ci_w_cp,'type':'Normal'}
				for j in ci_w_cp:
					post=j['name'].split('FEET')[0]+ 'FEET'
					if (post + "Normal") in post_item:
						if 'pc_with_bolt' in post_item[post + "Normal"]:
							post_item[post + "Normal"]['pc_with_bolt']+=get_stock_qty(j.name, warehouse) or 0
						else:
							post_item[post + "Normal"]['pc_with_bolt']=get_stock_qty(j.name, warehouse) or 0

					else:
						post_item[post + "Normal"]={'pc_with_bolt':get_stock_qty(j.name, warehouse) or 0, 'post_length':post, 'type': 'Normal'}
      
			ci_fencing_wo= frappe.db.get_all("Item", filters=[['item_name','like','%FENCING%'],['item_name','like','%WITHOUT%'], ['name', 'in',compound_item],['disabled', '=',0]])
			if ci_fencing_wo:
				for j in ci_fencing_wo:
					post=j['name'].split('FEET')[0]+ 'FEET'
					if (post + "FENCING") in post_item and post_item[post + "FENCING"]['type']=='Fencing':
						if 'wo_bolt' in post_item[post + "FENCING"]:
							post_item[post + "FENCING"]['wo_bolt']+=get_stock_qty(j.name, warehouse) or 0
						else:
							post_item[post + "FENCING"]['wo_bolt']=get_stock_qty(j.name, warehouse) or 0

					else:
						post_item[post + "FENCING"]={'wo_bolt':get_stock_qty(j.name, warehouse) or 0, 'post_length':post, 'type':"Fencing"}
   
			ci_fencing_with= frappe.db.get_all("Item", filters=[['item_name','like','%FENCING%'],['item_name','not like','%WITHOUT%'], ['name', 'in',compound_item],['disabled', '=',0]])
			if ci_fencing_with:
				for j in ci_fencing_with:
					post=j['name'].split('FEET')[0]+ 'FEET'
					if (post + "FENCING") in post_item and post_item[post + "FENCING"]['type']=='Fencing':
						if 'with_bolt' in post_item[post + "FENCING"]:
							post_item[post + "FENCING"]['with_bolt']+=get_stock_qty(j.name, warehouse) or 0
						else:
							post_item[post + "FENCING"]['with_bolt']=get_stock_qty(j.name, warehouse) or 0

					else:
						post_item[post + "FENCING"]={'with_bolt':get_stock_qty(j.name, warehouse) or 0, 'post_length':post, 'type':"Fencing"}
			
	#colour powder items
	colour_item=frappe.db.get_all("Item", filters={'item_group':"Raw Material",'has_variants':1},pluck='name')
	
	colour_details={}
	template={}
	for col in colour_item:
		item_col=frappe.db.get_all("Item", filters=[['name','like','%Pigment%'],['variant_of','in',col]],order_by='name')

		if item_col:
			
			for j in item_col:
				color_stock=get_stock_qty(j.name, warehouse_colour)
				attribute=frappe.get_doc("Item",j.name)
				colour=""
				
				for k in attribute.attributes:
					if k.attribute=="Colour":
						colour=k.attribute_value.lower()
				if not colour:
					continue
				if j.name not in colour_details:
					colour_details[j.name]={'colour': j.name, 'attribute_value': colour, 'stock':0}
				colour_details[j.name]['stock']+=color_stock
	dolamite=frappe.db.get_all("Item", filters=[['name','like','%dolamite%']])
	for j in dolamite:
		color_stock=get_stock_qty(j.name, warehouse_colour)
		colour_details[j.name]={'colour': j.name, 'stock':color_stock}
	colour_details=list(colour_details.values())
	for item in colour_details:
		if 'pigment' in item['colour'].lower():
			item['sqft']=round(item['stock']/3*100)
			item['no_of_days']=round(item['stock']/3*100/3000)
		elif 'dolamite' in item['colour'].lower():
			item['sqft']=round(item['stock']*49/75*100)
			item['no_of_days']=round(item['stock']*49/75*100/3000)
	# slab type item
	slab_item=frappe.db.get_all("Item", filters={'item_group':'Compound Walls', 'compound_wall_type':'Slab', 'disabled':0}, pluck='name')
	
	slab_details=[]
	
	for i in slab_item:
		slab_stock=get_stock_qty(i, warehouse)
		slab={'item':i,'stock':slab_stock}
		slab_details.append(slab)
	if frappe.db.exists("Item", "POST CAP"):
		post_cap=frappe.db.get_value("Item", 'POST CAP', 'name')
		post_=get_stock_qty('POST CAP', warehouse)
		post={'item':post_cap, 'stock':post_}
		slab_details.append(post)
 
	#pavers size details 
	paver_item=frappe.db.get_all("Item", filters={'item_group':"Pavers",'has_variants':1},pluck='name',order_by="name")

	for i in paver_item:
		normal=frappe.db.get_all("Item", filters=[
										['variant_of','=',i],
										["Item Variant Attribute","attribute_value",'=','Normal']], pluck='name',order_by='name')
	
		for j in normal:
			paver=frappe.db.sql(""" select name from `tabItem` WHERE name regexp '[0-9][mM][Mm]' and 'disabled'=0 """)
      
	
	normal_total_stock=size_details(items_stock, _type='Normal')
	normal_total_stock+=size_details(items_stock_shot, _type='Shot Blast')
	raw_material_stock=raw_material_stock_details()
	return items_stock, total_stock, items_stock_shot, total_stock_shot, list(sqf.values()), production,  sorted(list(post_item.values()), key=lambda x: x.get("post_length", "") or ""), colour_details, sorted(slab_details, key=lambda x: x.get("item", "") or ""), normal_total_stock, raw_material_stock

def size_details(items, _type):
	fields=['red', 'black', 'grey', 'brown', 'yellow']
	total_size={}
	for row in items:
		if row['short_name'] and 'mm' not in row['short_name'].lower():
			continue
		shortname=row['short_name'].lower()
		size=shortname.split('mm')[0][::-1]
		for i in range(len(size)):
			if not size[i].isnumeric():
				size=size[:i]
				break
		num_size=int(size[::-1]) if size[::-1].isnumeric() else 0
		size=size[::-1]+'MM'
		if 'kerb' in shortname:
			size+=' KERB STONE'
		if size not in total_size:
			total_size[size]={'type': _type, 'size': size, "num_size": num_size, 'total_stock': 0}
		for field in fields:
			total_size[size]['total_stock']+=row.get(field, 0)
	return sorted(list(total_size.values()), key=lambda x: x.get("num_size", "") or "")

def raw_material_stock_details():
	dsm=frappe.get_single("DSM Defaults")
	raw_material_stock = [get_stock_details_from_warehosue(item.warehouse, item.machine or "", item.type or "") for item in dsm.raw_material_details]
	
	total_stock=[]
	for item in raw_material_stock:
		total_stock+=list(item)
	
	total_stock.sort(key=lambda x: x.get("item", "") or "")
	return total_stock
	

def get_stock_details_from_warehosue(warehouse, machine="", prefix=""):
	dsm=frappe.get_single("DSM Defaults")
	item_filters=[]
	for row in dsm.items:
		item_filters.append(row.item_code)
	_prefix=prefix
	if _prefix and _prefix[-1]!=" ":
		_prefix+=" "
	condition=""
	if item_filters and len(item_filters)>1:
		condition=f' and bin.item_code in {tuple(item_filters)}'
	elif item_filters:
		condition=f' and bin.item_code="{item_filters[0]}"'
	condition=condition+" order by item asc"
	
	stock=frappe.db.sql(f"""select concat('{_prefix}', bin.item_code) as item, bin.actual_qty as qty, '{prefix}' as type, '{machine}' as machine from `tabBin` as bin
		left outer join `tabItem` as item on item.item_code=bin.item_code where item.item_group='Raw Material'
		and bin.warehouse='{warehouse}' and bin.actual_qty>0 {condition}; """, as_dict=True)
	
	return stock