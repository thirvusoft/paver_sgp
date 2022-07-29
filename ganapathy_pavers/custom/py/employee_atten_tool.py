from pickle import TRUE
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
import frappe
import json
from frappe.utils.csvutils import getlink


@frappe.whitelist()
def attenance(table_list, atten_date, checkout, company, ts_name):
	table_list=json.loads(table_list)
	doc1=frappe.get_single('Global Defaults')
	if(not doc1.default_company and not company):
		frappe.throw('Please Enter Default Company in '+getlink('global-defaults','Global Defaults'))
	for i in table_list:
		doc = frappe.new_doc("Attendance")
		doc.update({
			'employee':i.get("employee"),
			'status':"Present",
			'attendance_date': i.get('check_in') or atten_date,
			'company': company if(company) else doc1.default_company,
		})
		doc.insert(ignore_permissions=True)
		doc.submit()

	return checkin(table_list, atten_date, checkout, ts_name, doc.name)


def checkin(table_list, atten_date, checkout, ts_name, atten_name):
	for i in table_list:
		if i.get('check_in') or atten_date:
			doc = frappe.new_doc("Employee Checkin")
			doc.update({
				'employee':i.get("employee"),
				'log_type':"IN",
				'time': i.get('check_in') or atten_date,
				'ts_emp_att_tool_name':ts_name,
				'attendance': atten_name
			})
			doc.insert(ignore_permissions=True)
			# doc.submit()
		if i.get('check_out') or checkout:
			doc1 = frappe.new_doc("Employee Checkin")
			doc1.update({
				'employee':i.get("employee"),
				'log_type':"OUT",
				'time': i.get('check_out') or checkout,
				'ts_emp_att_tool_name':ts_name,
				'attendance': atten_name
			})
			doc1.insert(ignore_permissions=True)
			# doc1.submit()


def fill_emp_cancel_detail(self, event):
	if self.ts_emp_att_tool_name:
		doc=frappe.get_doc("TS Employee Attendance Tool", self.ts_emp_att_tool_name )
		emp=False
		cancel_list=[]
		for i in doc.ts_emp_checkin:
			if i.employee_name ==self.employee:
				if self.log_type =='IN':
					i.check_in=self.time
					emp=True

				if self.log_type =='OUT':
					i.check_out=self.time
					emp=True

			cancel_list.append(i)
		if(not emp):
			cancel_list.append({'employee_name':self.employee})
			if self.log_type =='IN':
					cancel_list[-1]["check_in"]=self.time

			if self.log_type =='OUT':
					cancel_list[-1]["check_out"]=self.time
		doc.update({
			'ts_emp_checkin':cancel_list
		})
		doc.flags.ignore_permissions=True
		doc.save('Update')



@frappe.whitelist()
def help_session(emp, upd_cout, emp_tabl):
    emp_tabl=json.loads(emp_tabl)
    check_in=[]
    for i in emp_tabl:
        check_in.append({'employee': i['employee']})
        if i['employee'] == emp:
            i['check_out'] = upd_cout
        check_in[-1].update({
            'employee_name': i['employee_name'],
			'check_out': i['check_out'],
			'check_in': i['check_in']
		})
    frappe.errprint(check_in)
    return check_in


