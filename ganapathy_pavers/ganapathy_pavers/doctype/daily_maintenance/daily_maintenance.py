# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.healthcare.doctype.clinical_procedure.clinical_procedure import get_stock_qty


class DailyMaintenance(Document):
	print("PPPPPPPPPPPPP")
	def onload(self):
		print("PPPPPPPPPPP")
		labour_employee_details= frappe.db.sql("""select count(att.name) from `tabAttendance` as att left outer join `tabEmployee` 
										as employee on att.employee=employee.name where employee.designation="Labour Worker" and att.attendance_date='{0}' and att.status="Present" """.format(self.date),as_list=True)
		self.labour_present=labour_employee_details[0][0]
		print(labour_employee_details)
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
def paver_item(warehouse):
	item=frappe.db.get_all("Item", filters={'item_group':"Pavers",'has_variants':1},pluck='name')
	# print(item)
	items_stock=[]
	total_stock={}
	for i in item:
		item_1=frappe.db.get_all("Item", filters=[
										['variant_of','=',i],
										["Item Variant Attribute","attribute_value",'=','Normal'],
																			])
		# print(i,item_1)
		template={'short_name':i, 'type': 'Normal'}
		for j in item_1:
			stock_qty=get_stock_qty(j.name, warehouse)
			print(stock_qty)

			attribute=frappe.get_doc("Item",j.name)
			colour=""
		
			for k in attribute.attributes:
				print(k.attribute)
				if k.attribute=="Colour":
					colour=k.attribute_value.lower()
					print(colour)
				if not colour:
					continue
			if colour not in template:
				template[colour]=0
			template[colour]+=stock_qty
			if colour not in total_stock:
				total_stock[colour]=0
			total_stock[colour]+=stock_qty
		items_stock.append(template)
	return items_stock, total_stock			
				
			
		# item_2=frappe.db.get_all("Item", filters=[
	  	# 								['variant_of','=',i],
		#                                 ["Item Variant Attribute","attribute_value",'=','Shot Blast'],
		#                    													])
		# print(i,item_2)
