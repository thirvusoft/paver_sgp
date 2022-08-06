import frappe
import json
from frappe.utils.csvutils import getlink
from datetime import datetime



@frappe.whitelist()
def employee_finder_attendance(designation='', department='', location='', branch='', company=''):
	employee_names=[]
	filters={}
	if(designation):
		filters["designation"]=designation
	if(department):
		filters['department']=department
	if(location):
		filters['location']=location
	if(branch):
		filters['branch']=branch
	if(company):
		filters['company']=company
	a=frappe.db.get_all("Employee",filters=filters,fields=["name", "employee_name", 'department'], order_by='employee_name')
	for name in a:
		employee_names.append(name)
	return employee_names


@frappe.whitelist()
def change_check_in(employee, logtype, name, check_in='', check_out=''):
	filters={}
	filters['log_type']=logtype
	if(logtype=='IN'):
		filters['time']=['!=', check_in]
	if(logtype=='OUT'):
		filters['time']=['!=', check_out]
	filters['employee']=employee
	filters['ts_emp_att_tool_name']=name
	res=frappe.get_all('Employee Checkin', filters, ['time'])
	if(res):
		if(str(res[0].time)!=(check_out if(logtype=='OUT') else check_in)):
			return frappe.get_all('Employee Checkin', filters, ['time'])
	


def validate_duplicate_entry(self, event):
	employee_list=[]
	for row in self.employee_detail:
		if(row.employee and row.employee in employee_list):
			frappe.throw(f"Duplicate entry for an employee {row.employee} at row {row.idx}")
		elif(row.employee):
			employee_list.append(row.employee)

@frappe.whitelist()
def check_in(table_list, ts_name):
	table_list=json.loads(table_list)
	for i in table_list:
		if(i.get('check_in') and i.get('employee')):
			if(i.get('department')):
				update_dept(i.get('employee'), i.get('department'))
			if(frappe.get_all("Employee Checkin",filters={'employee':i.get("employee"),'time':i.get('check_in'), 'ts_emp_att_tool_name':ts_name})):
				pass
			else:
				prev_doc=frappe.db.exists('Employee Checkin', {'employee': i.get('employee'), 'ts_emp_att_tool_name':ts_name, 'log_type':"IN"})
				if(not prev_doc):
					doc = frappe.new_doc("Employee Checkin")
					doc.update({
						'employee':i.get("employee"),
						'log_type':"IN",
						'time': i.get('check_in'),
						'ts_emp_att_tool_name':ts_name,
					})
					doc.flags.ignore_mandatory=True
					doc.insert()
				elif(frappe.db.exists('Employee Checkin', prev_doc)):
					
					doc=frappe.get_doc('Employee Checkin', prev_doc)
					doc.update({
						'employee':i.get("employee"),
						'log_type':"IN",
						'time': i.get('check_in'),
						'ts_emp_att_tool_name':ts_name,
					})
					doc.flags.ignore_mandatory=True
					doc.save()
		
		if(i.get('check_out') and i.get('employee')):
			if(i.get('department')):
				update_dept(i.get('employee'), i.get('department'))
			if(frappe.get_all("Employee Checkin",filters={'employee':i.get("employee"),'time':i.get('check_out'), 'ts_emp_att_tool_name':ts_name})):
				pass
			else:
				prev_doc=frappe.db.exists('Employee Checkin', {'employee': i.get('employee'), 'ts_emp_att_tool_name':ts_name, 'log_type':"OUT"})
				if(not prev_doc):
					doc = frappe.new_doc("Employee Checkin")
					doc.update({
						'employee':i.get("employee"),
						'log_type':"OUT",
						'time': i.get('check_out'),
						'ts_emp_att_tool_name':ts_name,
					})
					doc.flags.ignore_mandatory=True
					doc.insert()
						
				elif(frappe.db.exists('Employee Checkin', prev_doc)):
					doc=frappe.get_doc('Employee Checkin', prev_doc)
					doc.update({
						'employee':i.get("employee"),
						'log_type':"OUT",
						'time': i.get('check_out'),
						'ts_emp_att_tool_name':ts_name,
					})
					doc.flags.ignore_mandatory=True
					doc.save()
	
@frappe.whitelist()
def get_check_in(employee, name, logtype):
	doc= frappe.get_last_doc("Employee Checkin", filters={'employee': employee, 'ts_emp_att_tool_name': name, 'log_type': logtype})
	time=doc.time
	return time


@frappe.whitelist()
def attendance(table_list, company, ts_name):
	table_list=json.loads(table_list)
	validate_empty_field(table_list)
	doc1=frappe.get_single('Global Defaults')
	if(not doc1.default_company and not company):
		frappe.throw('Please Enter Default Company in '+getlink('global-defaults','Global Defaults'))
	for i in table_list:
		if(i.get("employee")):
			doc = frappe.new_doc("Attendance")
			doc.update({
				'employee':i.get("employee"),
				'status':"Present",
				'attendance_date': i.get('check_in'),
				'company': company if(company) else doc1.default_company,
				'ts_employee_attendance_tool': ts_name
			})
			doc.insert(ignore_permissions=True)
			doc.submit()

	
def update_attendance_to_checkin(self, event):
	emp_checkin_name=frappe.get_all('Employee Checkin', {'employee': self.employee, 'time': ['between', [self.attendance_date, self.attendance_date]]}, pluck='name')
	for doc in emp_checkin_name:
		frappe.db.set_value('Employee Checkin', doc, 'attendance', self.name)


def fill_emp_cancel_detail(self, event):
	if self.ts_emp_att_tool_name and self.ts_emp_att_tool_name in frappe.get_all('TS Employee Attendance Tool', {'docstatus': ['!=', 2]}, pluck='name'):
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
		doc.flags.ignore_mandatory=True
		doc.save('Update')

def fill_attn_cancel_detail(self, event):
	if self.ts_employee_attendance_tool and (self.ts_employee_attendance_tool in frappe.get_all('TS Employee Attendance Tool', {'docstatus': ['!=', 2]}, pluck='name')):
		doc=frappe.get_doc("TS Employee Attendance Tool", self.ts_employee_attendance_tool )
		emp=False
		cancel_list=[]
		for i in doc.ts_emp_checkin:
			if i.employee_name ==self.employee:
				i.attendance=self.name
				i.working_hrs=self.working_hours
				i.department=self.department
				emp=True
			cancel_list.append(i)
		if(not emp):
			cancel_list.append({'employee_name':self.employee, 'attendance': self.name, 'working_hrs': self.working_hours, 'department': self.department})
		doc.update({
			'ts_emp_checkin':cancel_list
		})
		doc.flags.ignore_mandatory=True
		doc.save('Update')



@frappe.whitelist()
def help_session(emp, emp_tabl):
	emp_tabl=json.loads(emp_tabl)
	res={}
	for i in emp_tabl:
		if i['employee'] == emp:
			res['cdt']=i.get('doctype')
			res['cdn']=i.get('name')
			break
		
	return res


@frappe.whitelist()
def row_delete(employee, name):
    if(frappe.get_all("Employee Checkin", filters={'employee':employee, 'ts_emp_att_tool_name':name})):
        return 1


def update_dept(employee, dept):
	emp_doc=frappe.get_doc('Employee', employee)
	if(emp_doc.department!=dept):
		emp_doc.update({
			'department': dept
		})
		emp_doc.flags.ignore_mandatory=True
		emp_doc.save()
	
@frappe.whitelist()
def delete_check_in(table_list, ts_name):
	table_list=json.loads(table_list)
	emp_list=[]
	for row in table_list:
		if(row.get('employee')):
			emp_list.append(row.get('employee'))
	delete_list=frappe.get_all('Employee Checkin', {'employee': ['not in', emp_list], 'ts_emp_att_tool_name': ts_name}, pluck='name')
	for doc in delete_list:
		frappe.delete_doc('Employee Checkin', doc)


def validate_empty_field(employee_detail):
	for i in employee_detail:
		if(not i.get('employee')):
			frappe.throw(f"Employee field cannot be empty for row {i.get('idx')}")
		if(not i.get('check_in')):
			frappe.throw(f"Checkin field cannot be empty for row {i.get('idx')}")
		if(not i.get('check_out')):
			frappe.throw(f"Checkout field cannot be empty for row {i.get('idx')}")
		

def day_wise_department(self, event):
	if(self.date):
		date=datetime.strptime(str(self.date), "%Y-%m-%d %H:%M:%S").date()
		filters={'date': ['between', [date, date]], 'docstatus':1}
		if(self.department):
			filters['department']=self.department
		if(self.designation):
			filters['designation']=self.designation
		if(self.branch):
			filters['branch']=self.branch
		if(self.location):
			filters['location']=self.location
		docs=frappe.get_all('TS Employee Attendance Tool', filters)
		if(docs):
			frappe.throw(f'Attendance tool already exist for this date for{(" "+frappe.bold(self.department)) if self.department else ""}{(" "+frappe.bold(self.designation)) if self.designation else ""}{(" "+frappe.bold(self.branch)) if self.branch else ""}{(" "+frappe.bold(self.location)) if self.location else ""}')
