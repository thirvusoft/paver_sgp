# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt
import json
import frappe
from frappe.model.document import Document

class EmployeeBonusTool(Document):
	pass
@frappe.whitelist()
def employee_finder(advance1):
	employee_names=[]
	a=frappe.db.get_all("Employee",filters={"designation":advance1},fields=["name", "employee_name"])
	for name in a:
		employee_names.append(name)
	return employee_names

@frappe.whitelist()
def create_retention_bonus(name,amount,date):
	amount=json.loads(amount)
	bonus_doc=frappe.new_doc('Retention Bonus')
	bonus_doc.employee = name
	bonus_doc.bonus_payment_date= date
	bonus_doc.bonus_amount = amount
	bonus_doc.salary_component='Bonus'
	bonus_doc.insert()
	bonus_doc.save()
	bonus_doc.submit()
	frappe.db.commit()
