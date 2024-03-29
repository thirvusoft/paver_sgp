import frappe
from frappe.utils.data import get_link_to_form, time_diff_in_hours
from datetime import date, timedelta, datetime

from erpnext.hr.doctype.shift_type.shift_type import process_auto_attendance_for_all_shifts
def mark_attendance():
	get_shift_type=frappe.db.get_all("Shift Type" ,pluck="name")
	last_att_sync = frappe.db.get_single_value("Thirvu HR Settings", "last_attendance_sync")
	last_checkin_sync = frappe.db.get_single_value("Thirvu HR Settings", "last_sync_of_without_log")
	for i in get_shift_type:
		frappe.db.set_value("Shift Type", i, "process_attendance_after", last_att_sync)
		frappe.db.set_value("Shift Type", i, "last_sync_of_checkin", last_checkin_sync)
	process_auto_attendance_for_all_shifts()
	
def check_in_out(self, event):
	total_working_hours = 0
	for emp_attendance_tool in self.working_area_list:
		emp_checkin_hours=frappe.get_all('Employee Checkin', 
		{'attendance': self.name, 'ts_emp_att_tool_name': emp_attendance_tool.get('emp_attendance_tool')},
		["log_type","time"])
		current_log="IN"
		total_hours=[]
		temp_hour=[]
		for i in emp_checkin_hours:
			if i.log_type==current_log:
				temp_hour.append(i.time)
				if current_log=="OUT":
					total_hours.append(temp_hour)
					temp_hour=[]
					current_log="IN"
					continue
				if current_log=="IN":
					current_log="OUT"
		hours=0
		hours_to_reduce=0
		if emp_attendance_tool.get('emp_attendance_tool'):
			ts_emp=frappe.get_doc("TS Employee Attendance Tool", emp_attendance_tool.get('emp_attendance_tool'))
			for row in ts_emp.employee_detail:
				if row.employee == self.employee:
					hours_to_reduce = row.hours_to_reduce

		for j in total_hours:
			hours+=(time_diff_in_hours(j[1],j[0]) or 0)
		if emp_attendance_tool.get('emp_attendance_tool') and hours_to_reduce:
			hours-=hours_to_reduce
		
		total_working_hours += (hours or 0)
		frappe.db.set_value(emp_attendance_tool.doctype, emp_attendance_tool.name, 'working_hours',hours)

	frappe.db.set_value(self.doctype, self.name, 'working_hours',total_working_hours)
	return ot_hours_cal(self, float(total_working_hours))

def ot_hours_cal(self, hours):
	day_ot=hours % 8.0
	frappe.db.set_value(self.doctype, self.name, "ot_hours",  day_ot)
	frappe.db.set_value(self.doctype, self.name, "one_day_hours",  (hours//8)*8)
	frappe.db.set_value(self.doctype, self.name, "full_day_workings",  hours//8)




# Copyright (c) 2022, Thirvusoft Pvt and contributors
# For license information, please see license.txt
import frappe
from frappe.utils import cint, get_datetime, getdate, to_timedelta, time_diff_in_hours,get_time 
from frappe.utils import time_diff_in_hours
from frappe import _, utils
from datetime import datetime, timedelta
import datetime

import frappe
from frappe.model.document import Document

def get_employees_for_shift():
	total_employees=frappe.db.get_all('Employee', filters={"attendance_device_id":['is', 'set'],'status':'Active'}, pluck='name')
	return total_employees

@frappe.whitelist()
def scheduler_for_employee_shift():
	create_workers_attendance()

def create_datewise_checkin(employee,employee_checkin,date_wise_checkin,checkin_name):
	for data in employee_checkin:
		if data.time.date() in date_wise_checkin:
			adding_checkin_datewise(date_wise_checkin,data.time.date(),[{'log_type':data['log_type'],'time':data['time']}])
			adding_checkin_datewise(checkin_name,data.time.date(),[data['name']])
		else:
			date_wise_checkin.update({data.time.date():[{"log_type":data['log_type'],"time":data['time']}]})
			checkin_name.update({data.time.date():[data['name']]})
	
	for logs in date_wise_checkin:
		logs_res=[]
		
		[logs_res.append(x) for x in date_wise_checkin[logs] if x not in logs_res]
		date_wise_checkin.update({logs:logs_res})

def adding_checkin_datewise(checkin_date, checkin_date_key, checkin_details):
	if checkin_date_key not in checkin_date:
		checkin_date[checkin_date_key] = list()
	checkin_date[checkin_date_key].extend(checkin_details)

def create_workers_attendance():
	"""Workers Attendance"""

	employee_list = get_employees_for_shift()
	for employee in employee_list:

		date_wise_checkin = frappe._dict()
		checkin_name = frappe._dict()
		emp_checkin = frappe.db.get_all("Employee Checkin", 
			filters={"employee": employee, "device_id": ["is", "set"]}, 
			order_by="time",
			fields=['time', 'log_type', 'name']
			)
		create_datewise_checkin(employee, emp_checkin, date_wise_checkin, checkin_name)
		
		for data in date_wise_checkin:
			attendance = frappe._dict()
			in_time = out_time = 0

			if date_wise_checkin[data][0]['log_type']=='IN':
				in_time = date_wise_checkin[data][0]['time'].time()
				in_time_date = date_wise_checkin[data][0]['time']	

			if date_wise_checkin[data][len(date_wise_checkin[data]) - 1]:
				out_time = date_wise_checkin[data][len(date_wise_checkin[data]) - 1]['time'].time()
				out_time_date = date_wise_checkin[data][len(date_wise_checkin[data]) - 1]['time']
						
			if in_time or out_time:
				
				if not frappe.db.exists("Attendance",{"employee":employee,"attendance_date":data}):
					attendance.update({
						"attendance_date":data,
						"employee":employee,
						"status":"Present" 
					})
					
					try:
						attendance_doc = frappe.new_doc("Attendance")
						attendance_doc.update(attendance)
						attendance_doc.insert()
						if attendance['status']== "Present":
							attendance_doc.submit()
					except Exception as e:
						frappe.log_error(title="Attendance Creation",message=e)
			

def unlink_logs(doc,event):
	unlink_attendance_from_checkins(doc)

def unlink_attendance_from_checkins(self):
	EmployeeCheckin = frappe.qb.DocType("Employee Checkin")
	linked_logs = (
		frappe.qb.from_(EmployeeCheckin)
		.select(EmployeeCheckin.name)
		.where(EmployeeCheckin.attendance == self.name)
		.for_update()
		.run(as_dict=True)
	)

	if linked_logs:
		(
			frappe.qb.update(EmployeeCheckin)
			.set("attendance", "")
			.where(EmployeeCheckin.attendance == self.name)
		).run()
		
		frappe.msgprint(
			msg=_("Unlinked Attendance record from Employee Checkins: {}").format(
				", ".join(get_link_to_form("Employee Checkin", log.name) for log in linked_logs)
			),
			title=_("Unlinked logs"),
			indicator="blue",
			is_minimizable=True,
			wide=True,
		)