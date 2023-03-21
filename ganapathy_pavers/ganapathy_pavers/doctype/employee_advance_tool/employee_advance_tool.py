import frappe

from frappe.model.document import Document

class EmployeeAdvanceTool(Document):
	def validate(self):
		table = self.employee_advance_details
		total = 0
		for  i in table:
			total = total + (i.get("current_advance") or 0)

		self.total_advance_amount=total
	
	def on_submit(self):
		i=0
		for adv in self.employee_advance_details:
			i+=1
			if((adv.current_advance) and not (adv.mode_of_payment or self.mode_of_payment)):
				frappe.throw(f"Mode of Payment is mandatory at #row {i}")
		
		for adv in self.employee_advance_details:
			create_employee_advance(
				amount=adv.current_advance,
				name=adv.employee,
				date=self.date,
				branch= self.branch,
				mode_of_payment=adv.mode_of_payment or self.mode_of_payment,
				payment_type=adv.payment_method,
				tool_name=self.name,
			)


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
def create_employee_advance(name,amount,date,payment_type,mode_of_payment,branch, salary_slip="", commit = True, tool_name=None):
		advance_doc=frappe.new_doc('Employee Advance')
		advance_doc.employee = name
		advance_doc.advance_amount = amount
		advance_doc.posting_date = date
		advance_doc.exchange_rate = 1.0
		advance_doc.employee_advance_tool = tool_name
		advance_doc.branch=branch
		advance_doc.mode_of_payment=mode_of_payment
		advance_doc.salary_slip=salary_slip
		if payment_type=="Deduct from Salary":
			advance_doc.repay_unclaimed_amount_from_salary=1
		advance_doc.insert()
		advance_doc.save()
		advance_doc.submit()
		if commit:
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

def cancel_employee_advance(self, event=None):
	if not self.employee_advance_tool:
		return
	
	doc = frappe.get_doc("Employee Advance Tool", self.employee_advance_tool)
	advances = doc.employee_advance_details

	for row in advances:
		if row.employee == self.employee and row.current_advance == self.advance_amount:
			row.is_cancelled = 1
	
	doc.update({
		"employee_advance_details": advances
	})

	doc.save('update')

