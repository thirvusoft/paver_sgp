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
def paver_item(warehouse, date):
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
		# print(i,item_1)
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
		# print(i,item_2)
		template_1={'short_name':i, 'type': 'Shot Blast'}
		for sb in item_2:
			stock_qty_sb=get_stock_qty(sb.name, warehouse)
			# print(stock_qty_sb)

			attribute=frappe.get_doc("Item",sb.name)
			colour_sb=""
		
			for cl in attribute.attributes:
				# print(cl.attribute)
				if cl.attribute=="Colour":
					colour_sb=cl.attribute_value.lower()
					# print(colour_sb)
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
	vehicle_d=frappe.db.get_all("Vehicle Log", filters={'date': date,'docstatus':0,'delivery_note':['is', 'set'] }, fields=['license_plate', 'delivery_note'])
	sqf={}
	for veh in vehicle_d:
		dn=frappe.get_doc("Delivery Note", veh['delivery_note'])
		for row in dn.items:
			if row.item_group in ["Pavers","Compound Wall"]:
				sq=uom_conversion(row.item_code, row.stock_uom, row.stock_qty, "SQF")
				if veh['license_plate'] not in sqf:
					sqf[veh['license_plate']]=0
				sqf[veh['license_plate']]+=sq	
    #production_details			
	paver_m=frappe.db.sql(f""" select item_to_manufacture, work_station, sum(production_sqft) as production_sqft,
                         		sum(no_of_racks) as no_of_racks from `tabMaterial Manufacturing` where date(from_time)={date} """, as_list=True)
	cw_m=frappe.db.get_all("CW Manufacturing", filters={'molding_date':date})
	print(date)
	production=[]
	print(paver_m)
	for paver in paver_m:  
		production_details={'item':paver[0],'machine':paver[1],'rack':paver[2],'sqft':paver[3]}
		production.append(production_details)
	return items_stock, total_stock, list(sqf.values()), production