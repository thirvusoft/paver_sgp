import frappe
import json
from frappe.utils.csvutils import getlink
from datetime import datetime
from frappe.utils import date_diff
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


@frappe.whitelist()
def employee_finder_attendance(designation='', location='', machine='', branch='', company=''):
	employee_names=[]
	filters={'status':"Active"}
	if(designation):
		filters["designation"]=designation
	if(location):
		filters['location']=location
	if(branch):
		filters['branch']=branch
	if(company):
		filters['company']=company
	if(machine):
		filters['machine']=machine
	a=frappe.db.get_all("Employee",filters=filters,fields=["name", "employee_name", 'location', 'machine'], order_by='employee_name')
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
	if(isinstance(table_list, str)):
		table_list=json.loads(table_list)
	for i in table_list:
		if(i.get('check_in') and i.get('employee')):
			if(i.get('location')):
				update_dept(i.get('employee'), i.get('location'), i.get('machine'))
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
					if(doc.employee!=i.get('employee') or doc.log_type!="IN" or doc.time!=i.get('check_in') or doc.ts_emp_att_tool_name!=ts_name):
						doc.update({
							'employee':i.get("employee"),
							'log_type':"IN",
							'time': i.get('check_in'),
							'ts_emp_att_tool_name':ts_name,
						})
						doc.flags.ignore_mandatory=True
						doc.save()
		
		if(i.get('check_out') and i.get('employee')):
			if(i.get('location')):
				update_dept(i.get('employee'), i.get('location'), i.get('machine'))
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
					if(doc.employee!=i.get('employee') or doc.log_type!="OUT" or doc.time!=i.get('check_out') or doc.ts_emp_att_tool_name!=ts_name):
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
	if(isinstance(table_list, str)):
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
				'attendance_date':  datetime.strptime(i.get('check_in'), DATE_TIME_FORMAT).date(),
				'location': i.get('location'),
				'machine': i.get('machine'),
				'company': company if(company) else doc1.default_company,
				'ts_employee_attendance_tool': ts_name
			})
			doc.insert(ignore_permissions=True)
			doc.submit()

	
def update_attendance_to_checkin(self, event):
	emp_checkin_name=frappe.db.sql(f"""
		SELECT name
		FROM `tabEmployee Checkin`
		WHERE employee='{self.employee}' 
		AND DATE(time) BETWEEN '{self.attendance_date}' AND '{self.attendance_date}'
	""", as_list=True)

	emp_checkin_name = [i[0] if isinstance(i, list) else i for i in emp_checkin_name if i]

	for checkin in frappe.get_all('Employee Checkin', {'attendance': self.name, "name": ["not in", emp_checkin_name]}, pluck='name'):
		doc=frappe.get_doc("Employee Checkin", checkin)
		doc.add_comment(text=f"""
		{frappe.utils.now()} - Reference: {self.name}<br>
		Removed Attendance name: {doc.attendance}  - {self.attendance_date}
		""")
		frappe.db.set_value('Employee Checkin', checkin, 'attendance', "")

	for _doc in emp_checkin_name:
		doc=frappe.get_doc("Employee Checkin", _doc)
		doc.add_comment(text=f"""
		{frappe.utils.now()} - Reference: {self.name}<br>
		Linking Attendance name: {self.name}  - {self.attendance_date}
		""")
		frappe.db.set_value('Employee Checkin', _doc, 'attendance', self.name)


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
		doc.run_method = lambda x: x
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
				i.location=self.location
				i.machine=self.machine
				emp=True
			cancel_list.append(i)
		if(not emp):
			cancel_list.append({
				'employee_name':self.employee, 
				'attendance': self.name, 
				'working_hrs': self.working_hours, 
				'location': self.location, 
				'machine': self.machine
				})
		doc.update({
			'ts_emp_checkin':cancel_list
		})
		doc.flags.ignore_mandatory=True
		doc.save('Update')



@frappe.whitelist()
def help_section(emp, emp_tabl):
	emp_tabl=json.loads(emp_tabl)
	res={}
	for i in emp_tabl:
		if i['employee'] == emp:
			res['cdt']=i.get('doctype')
			res['cdn']=i.get('name')
			res['idx']=i.get('idx')
			break
		
	return res


@frappe.whitelist()
def row_delete(employee, name):
    if(frappe.get_all("Employee Checkin", filters={'employee':employee, 'ts_emp_att_tool_name':name})):
        return 1


def update_dept(employee, location, machine):
	emp_doc=frappe.get_doc('Employee', employee)
	if(emp_doc.location!=location or emp_doc.machine!=machine):
		emp_doc.update({
			'location': location,
			'machine': machine
		})
		emp_doc.flags.ignore_mandatory=True
		emp_doc.save()
	
@frappe.whitelist()
def delete_check_in(table_list, ts_name):
	if(isinstance(table_list, str)):
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
		date=datetime.strptime(str(self.date), DATE_TIME_FORMAT).date()
		filters={'date': ['between', [date, date]], 'docstatus':['!=', 2]}
		if(self.name in frappe.get_all(self.doctype, pluck = 'name')):
			filters['name'] = ['!=', self.name]
		if(self.designation):
			filters['designation']=self.designation
		if(self.branch):
			filters['branch']=self.branch
		if(self.location):
			filters['location']=self.location
		if(self.machine):
			filters['machine']=self.machine
		docs=frappe.get_all('TS Employee Attendance Tool', filters ,pluck='name')
		if(docs):
			frappe.throw(f'Attendance tool already exist for this date {frappe.utils.csvutils.getlink("TS Employee Attendance Tool", docs[0])} for{(" "+frappe.bold(self.designation)) if self.designation else ""}{(" "+frappe.bold(self.branch)) if self.branch else ""}{(" "+frappe.bold(self.location)) if self.location else ""}')

def validate_same_dates(self, event):
	for row in self.employee_detail:
		if(row.check_out and row.check_in):
			if(date_diff(row.check_out, row.check_in)!=0):
				frappe.throw(f"Checkin and Checkout must be a same date for row {row.idx}")

def create_and_delete_checkins(self, event):	
	check_in([i.__dict__ for i in self.employee_detail], self.name)
	delete_check_in([i.__dict__ for i in self.employee_detail], self.name)

def create_attendance(self, event):
	attendance([i.__dict__ for i in self.employee_detail], self.company, self.name)

def doc_cancel(self, event):
	for checkin in frappe.get_all("Employee Checkin",{'ts_emp_att_tool_name':self.name,}):
		doc= frappe.get_doc("Employee Checkin", checkin.name)
		if doc.docstatus == 1:
			doc.cancel()
		doc.delete()
	frappe.msgprint("Cancelled all Employee Checkins and Attendances")
