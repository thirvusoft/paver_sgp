import frappe

from frappe.model.document import Document

class EmployeeAdvanceTool(Document):
	pass
@frappe.whitelist()
def employee_finder(advance1):
	employee_names=[]
	a=frappe.db.get_all("Employee",filters={"designation":advance1},fields=["name", "employee_name"])
	for name in a:
		employee_names.append(name)
	return employee_names
@frappe.whitelist()
def create_employee_advance(name,amount,date,payment_type):
		advance_doc=frappe.new_doc('Employee Advance')
		advance_doc.employee = name
		advance_doc.advance_amount = amount
		advance_doc.posting_date = date
		advance_doc.exchange_rate = 1.0
		if payment_type=="Deduct from Salary":
			advance_doc.repay_unclaimed_amount_from_salary=1
		advance_doc.insert()
		advance_doc.save()
		advance_doc.submit()
		frappe.db.commit()
