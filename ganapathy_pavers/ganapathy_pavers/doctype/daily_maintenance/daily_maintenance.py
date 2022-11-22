# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.healthcare.doctype.clinical_procedure.clinical_procedure import get_stock_qty
from ganapathy_pavers import uom_conversion


class DailyMaintenance(Document):
	def onload(self):
		labour_employee_details= frappe.db.sql("""select count(att.name) from `tabAttendance` as att left outer join `tabEmployee` 
										as employee on att.employee=employee.name where employee.designation="Labour Worker" and att.attendance_date='{0}' and att.status="Present" """.format(self.date),as_list=True)
		self.labour_present=labour_employee_details[0][0]
		operator_employee_details= frappe.db.sql("""select count(att.name) from `tabAttendance` as att left outer join `tabEmployee` 
										as employee on att.employee=employee.name where employee.designation="Operator" and att.attendance_date='{0}' and att.status="Present" """.format(self.date),as_list=True)
		self.operator_present=operator_employee_details[0][0]
		labour_employee_details_absent= frappe.db.sql("""select count(att.name) from `tabAttendance` as att left outer join `tabEmployee` 
										as employee on att.employee=employee.name where employee.designation="Labour Worker" and att.attendance_date='{0}' and att.status="Absent" """.format(self.date),as_list=True)
		self.labour_absent=labour_employee_details_absent[0][0]
		operator_employee_details_absent= frappe.db.sql("""select count(att.name) from `tabAttendance` as att left outer join `tabEmployee` 
										as employee on att.employee=employee.name where employee.designation="Operator" and att.attendance_date='{0}' and att.status="Absent" """.format(self.date),as_list=True)
		self.operator_absent=operator_employee_details_absent[0][0]


	
@frappe.whitelist()
def paver_item(warehouse, date, warehouse_colour):
	item=frappe.db.get_all("Item", filters={'item_group':"Pavers",'has_variants':1},pluck='name')
	# print(item)
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
				colour=""
			
				for k in attribute.attributes:
					if k.attribute=="Colour":
						colour=k.attribute_value.lower()
					if not colour:
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
										["Item Variant Attribute","attribute_value",'=','Shot Blast'],
																			])
		if item_2:
			template_1={'short_name':i, 'type': 'Shot Blast'}
			for sb in item_2:
				stock_qty_sb=get_stock_qty(sb.name, warehouse)

				attribute=frappe.get_doc("Item",sb.name)
				colour_sb=""
			
				for cl in attribute.attributes:
					if cl.attribute=="Colour":
						colour_sb=cl.attribute_value.lower()
					if not colour_sb:
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
	vehicle_d=frappe.db.get_all("Vehicle Log", filters={'date': date,'docstatus':1,'delivery_note':['is', 'set'] }, fields=['license_plate', 'delivery_note'])
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
	paver_m=frappe.db.sql(f""" select item_to_manufacture, work_station, sum(production_sqft) as production_sqft,
                         		sum(no_of_racks) as no_of_racks from `tabMaterial Manufacturing` where date(from_time) = '{date}' group by item_to_manufacture """, as_list=True)
	if paver_m:
		sqft=0
		rack=0
		for paver in paver_m:  
			production_details={'item':paver[0],'machine':paver[1],'rack':paver[2],'sqft':paver[3]}
			rack+=paver[2]
			sqft+=paver[3]
			production.append(production_details)
		production.append({'item':'Total Sqft', 'rack':rack, 'sqft':sqft})
	cw_m=frappe.db.get_all("CW Manufacturing", filters={'molding_date':date}, pluck='name')
	if cw_m:
		cw_item=frappe.db.get_all("CW Items", filters={'parent':['in' ,cw_m]}, fields=['item','workstation','production_sqft'])
		sqft=0
		for cw in cw_item:
			if cw:
				cw_production={'item':cw.item,'machine':cw.workstation, 'rack':'', 'sqft':cw.production_sqft}
				sqft+=cw.production_sqft
				production.append(cw_production)
		production.append({'item':'Total Sqft', 'sqft':sqft})
	

	#compound_wall_items
	compound_item=frappe.db.get_all("Item", filters={'item_group':"Compound Walls","compound_wall_type":"Post",'item_name':['like',"%FEET%"]},pluck='name')
	post_item={}
	# print(compound_item)
	if compound_item:
		# for i in compound_item:
			ci_wo= frappe.db.get_all("Item", filters={'item_name':['like','% FEET WITHOUT BOLT POST%'],'name':['in',compound_item],'disabled':0})
			# print(ci_wo)
			if ci_wo:
				template={'post_length':ci_wo, 'type':'Normal'}
				for j in ci_wo:
					post=j['name'].split('FEET')[0]+ 'FEET'
					if post in post_item and post_item[post]['type']=='Normal':
						if 'wo_bolt' in post_item[post]:
							post_item[post]['wo_bolt']+=get_stock_qty(j.name, warehouse) or 0
						else:
							post_item[post]['wo_bolt']=get_stock_qty(j.name, warehouse) or 0

						# post_item[post]['post_length']=j['name'].split('FEET')[0]+ 'FEET'
					else:
						post_item[post]={'wo_bolt':get_stock_qty(j.name, warehouse) or 0, 'post_length':post, 'type':'Normal'}
			# print(post_item)		
			ci_w= frappe.db.get_all("Item", filters={'item_name':['like','%FEET BOLT POST%'], 'name':['in',compound_item],'disabled':0})
			print(ci_w)
			if ci_w:
				template={'post_length':ci_w, 'type':'Normal'}
				for j in ci_w:
					post=j['name'].split('FEET')[0]+ 'FEET'
					if post in post_item and post_item[post]['type']=='Normal':
						if 'with_bolt' in post_item[post]:
							post_item[post]['with_bolt']+=get_stock_qty(j.name, warehouse) or 0
						else:
							post_item[post]['with_bolt']=get_stock_qty(j.name, warehouse) or 0

      
						# post_item[post]['post_length']=j['name'].split('FEET')[0]+ 'FEET'
					else:
						post_item[post]={'with_bolt':get_stock_qty(j.name, warehouse) or 0, 'post_length':post, 'type':'Normal'}
			# print(post_item)
			
			ci_wo_cp= frappe.db.get_all("Item", filters={'item_name':['like','%CORNER WITHOUT%'], 'name':['in',compound_item],'disabled':0})
			print(ci_wo_cp)
			if ci_wo_cp:
				template={'post_length':ci_wo_cp, 'type':'Normal'}
				for j in ci_wo_cp:
					post=j['name'].split('FEET')[0]+ 'FEET'
					if post in post_item:
						if 'pc_wo_bolt' in post_item[post]:
							post_item[post]['pc_wo_bolt']+=get_stock_qty(j.name, warehouse) or 0
						else:
							post_item[post]['pc_wo_bolt']=get_stock_qty(j.name, warehouse) or 0

					else:
						post_item[post]={'pc_wo_bolt':get_stock_qty(j.name, warehouse) or 0, 'post_length':post}
			# print(post_item)
			
   
			# ci_w_cp= frappe.db.get_all("Item", filters={'item_name':['like','%CORNER BOLT%'], 'name':['in',compound_item],'disabled':0})
			# print(ci_w_cp)
			# if ci_w_cp:
			# 	template={'post_length':ci_w_cp,'type':'Normal'}
			# 	for j in ci_w_cp:
			# 		post=j['name'].split('FEET')[0]+ 'FEET'
			# 		if post in post_item:
			# 			if 'pc_with_bolt' in post_item[post]:
			# 				post_item[post]['pc_with_bolt']+=get_stock_qty(j.name, warehouse) or 0
			# 			else:
			# 				post_item[post]['pc_with_bolt']=get_stock_qty(j.name, warehouse) or 0

			# 		else:
			# 			post_item[post]={'pc_with_bolt':get_stock_qty(j.name, warehouse) or 0, 'post_length':post}
      
			# ci_fencing_wo= frappe.db.get_all("Item", filters={'item_name':['like','%FENCING WITHOUT BOLT POST%'], 'item_group':'Compound Walls','disabled':0})
			# print(ci_fencing_wo)
			# if ci_fencing_wo:
			# 	for j in ci_fencing_wo:
			# 		post=j['name'].split('FEET')[0]+ 'FEET'
			# 		if post in post_item and post_item[post]['type']=='Fencing':
			# 			if 'wo_bolt' in post_item[post]:
			# 				post_item[post]['wo_bolt']+=get_stock_qty(j.name, warehouse) or 0
			# 			else:
			# 				post_item[post]['wo_bolt']=get_stock_qty(j.name, warehouse) or 0

			# 		else:
			# 			post_item[post]={'wo_bolt':get_stock_qty(j.name, warehouse) or 0, 'post_length':post, 'type':"Fencing"}
			# # print(post_item)
   
			ci_fencing_with= frappe.db.get_all("Item", filters={'item_name':['like','%FENCING BOLT POST%'], 'item_group':'Compound Walls','disabled':0})
			print(ci_fencing_with)
			if ci_fencing_with:
				for j in ci_fencing_with:
					post=j['name'].split('FEET')[0]+ 'FEET'
					if post in post_item and post_item[post]['type']=='Fencing':
						if 'with_bolt' in post_item[post]:
							post_item[post]['with_bolt']+=get_stock_qty(j.name, warehouse) or 0
						else:
							post_item[post]['with_bolt']=get_stock_qty(j.name, warehouse) or 0

					else:
						post_item[post]={'with_bolt':get_stock_qty(j.name, warehouse) or 0, 'post_length':post, 'type':"Fencing"}
			# print(post_item)
			
	#colour powder items
	colour_item=frappe.db.get_all("Item", filters={'item_group':"Raw Material",'has_variants':1},pluck='name')
	colour_details=[]
	for col in colour_item:
		item_col=frappe.db.get_all("Item", filters=[['name','like','%Pigment%'],['variant_of','in',col]])
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
					if colour not in template:
						template[colour]=0
						template[colour]+=color_stock
				template={'colour':j.name,'stock':color_stock, 'attribute_value':colour}
				colour_details.append(template)
				
	# slab type item
	slab_item=frappe.db.get_all("Item", filters={'item_group':'Compound Walls', 'compound_wall_type':'Slab', 'disabled':0}, pluck='name')
	post_cap=frappe.db.get_value("Item", 'POST CAP', 'name')
	slab_details=[]
	
	for i in slab_item:
		slab_stock=get_stock_qty(i, warehouse)
		slab={'item':i,'stock':slab_stock}
		slab_details.append(slab)
	post_=get_stock_qty('POST CAP', warehouse)
	post={'item':post_cap, 'stock':post_}
	slab_details.append(post)
	# print(slab_item)
 
	#pavers size details 
	paver_item=frappe.db.get_all("Item", filters={'item_group':"Pavers",'has_variants':1},pluck='name')
	# print(paver_item)
	for i in paver_item:
		normal=frappe.db.get_all("Item", filters=[
										['variant_of','=',i],
										["Item Variant Attribute","attribute_value",'=','Normal']], pluck='name')
		# print(normal)
		for j in normal:
			# print(f""" select name from `tabItem` WHERE name regexp '[0-9][mM][Mm]' and 'disabled'=0 name in {tuple(normal)}""")
			paver=frappe.db.sql(""" select name from `tabItem` WHERE name regexp '[0-9][mM][Mm]' and 'disabled'=0 """)
			# print(paver)
      
	

	return items_stock, total_stock,items_stock_shot,total_stock_shot, list(sqf.values()), production,  list(post_item.values()), colour_details, slab_details