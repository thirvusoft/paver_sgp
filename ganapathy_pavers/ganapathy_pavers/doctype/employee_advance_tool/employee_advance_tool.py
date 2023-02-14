import frappe

from frappe.model.document import Document

class EmployeeAdvanceTool(Document):
	pass
@frappe.whitelist()
	
def employee_finder(advance1="", location=""):

	employee_names=[]
	filters={"status": "Active"}
	if advance1:
		filters["designation"]=advance1
	if location:
		filters["location"]=location
	a=frappe.db.get_all("Employee",filters=filters,fields=["name", "employee_name"],order_by="employee_name")
	for name in a:
		employee_names.append(name)
	return employee_names

@frappe.whitelist()
def create_employee_advance(name,amount,date,payment_type,mode_of_payment,branch, salary_slip=""):
		advance_doc=frappe.new_doc('Employee Advance')
		advance_doc.employee = name
		advance_doc.advance_amount = amount
		advance_doc.posting_date = date
		advance_doc.exchange_rate = 1.0
		advance_doc.branch=branch
		advance_doc.mode_of_payment=mode_of_payment
		advance_doc.salary_slip=salary_slip
		if payment_type=="Deduct from Salary":
			advance_doc.repay_unclaimed_amount_from_salary=1
		advance_doc.insert()
		advance_doc.save()
		advance_doc.submit()
		frappe.db.commit()
		return advance_doc

@frappe.whitelist()
def employee_finder_attendance(designation='', department=''):
	employee_names=[]
	filters={"status": "Active"}
	if(designation):
		filters["designation"]=designation
	if(department):
		filters['department']=department
	a=frappe.db.get_all("Employee",filters=filters,fields=["name", "employee_name"], order_by='employee_name')
	for name in a:
		employee_names.append(name)
	return employee_names