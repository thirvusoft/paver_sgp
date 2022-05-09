import frappe
from frappe import _


class EmployeeAdvanceTool(Document):
	@frappe.whitelist()
	def get_doctypes_for_closing(self):

	@frappe.whitelist()
	def employee_advance_details(self):
		self=frappe.get_doc('Employee Advance Tool',self)
		self.set("employee_advance_details", [])
		employees = self.get_emp_list()
		if not employees:
			error_msg = _(
				"No employees found for the mentioned criteria:<br>Company: {0}<br> Currency: {1}<br>Payroll Payable Account: {2}"
			).format(
				frappe.bold(self.company),
				frappe.bold(self.currency),
				frappe.bold(self.payroll_payable_account),
			)
	
			if self.designation:
				error_msg += "<br>" + _("Designation: {0}").format(frappe.bold(self.designation))
			frappe.throw(error_msg, title=_("No employees found"))

		for d in employees:
			self.append("employees", d)

		self.number_of_employees = len(self.employees)
		if self.validate_attendance:
			return self.validate_employee_attendance()
	@frappe.whitelist()
	def create_employee_advance(self):
		"""
		Creates Advance for selected employees if already not created
		"""
		self.check_permission("write")
		employees = [emp.employee for emp in self.employees]
		if employees:
			args = frappe._dict(
				{
					"employee_name":self.employee_name,
					"posting_date":self.posting_date,
					"start_date": self.start_date,
					"company": self.company,
					"posting_date": self.posting_date,
					"current_advance":self.current_advance
				}
			)