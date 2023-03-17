# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt
from locale import currency
import frappe
from frappe import _, errprint
from frappe.utils import format_date

def execute(filters={}):
	columns = get_columns(filters)
	if(filters.get('group_by')=='Site Name'):
		return columns, run(filters)[0]
	else:
		data=[]
		ts_filters={}
		if filters.get('employee'):
			ts_filters['name1'] = filters.get('employee')
		if filters.get('from_date') and filters.get('to_date'):
			ts_filters['start_date'] = ['between', [filters.get('from_date'), filters.get('to_date')]]
		if filters.get("site_name"):
			ts_filters['parent'] = filters.get("site_name")
		if not filters.get("show_other_work"):
			ts_filters['other_work'] = 0
		jw=list(set(frappe.get_all("TS Job Worker Details", filters=ts_filters, pluck="name1")))
		jw = [i or "" for i in jw]
		jw.sort()
		currency = frappe.db.get_value("Currency", frappe.db.get_default("currency"), "symbol") or ''
		filters['ts_group_by'] = 'Job Worker'
		filters['group_by'] = 'Site Name'
		final_total_sqft=0
		final_total_amount=0
		theme = frappe.db.get_value("User", frappe.session.user, "desk_theme")
		group_total_colour = {'Light': 'Green', 'Dark': 'orange'}
		for i in jw:
			if(i):
				filters['employee']=i
				jw_data=run(filters)
				final_total_sqft+=jw_data[1]
				final_total_amount+=jw_data[2]
				data+=jw_data[0]
				total = ["" for i in range(11)]
				total[0] = f"<b style='color:{group_total_colour.get(theme)}; font-size:20px;text-align: center;'>{frappe.get_value('Employee', i, 'employee_name')} <span style='font-size: 15px;'>Group Total</span></b>"
				total[6] = f'<b style="color:{group_total_colour.get(theme)}; font-size:20px;">{"%.2f"%jw_data[1]}</b>'
				total[10] = f'<b style="color:{group_total_colour.get(theme)}; font-size:20px;">{currency} {"%.2f"%jw_data[2]}</b>'
				data.append(total)
		total = ["" for i in range(11)]
		total[0] = f"<b>Total</b>"
		total[6] = frappe.bold("%.2f"%final_total_sqft)
		total[10] = frappe.bold(f"{currency} %.2f"%final_total_amount)
		data.append(total)
		return columns, data

def run(filters={}):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	employee = filters.get("employee")
	site_name = filters.get("site_name")
	show_other_work = filters.get("show_other_work")
	conditions = ""
	if from_date or to_date or employee or site_name:
		conditions = " where 1 = 1"
		if from_date and to_date:
			conditions += "  and jwd.start_date between '{0}' and '{1}' ".format(from_date, to_date)
		if employee:
			conditions += " and jwd.name1 ='{0}' ".format(employee)
		if site_name:
			conditions += " and site.name = '{0}' ".format(site_name)
		if not show_other_work:
			conditions += " and jwd.other_work = 0 "

	report_data = frappe.db.sql(""" select  jwd.start_date,
											site.name,
											(select employee_name from `tabEmployee` where name = jwd.name1 ) as jobworker,
											site.supervisor_name,
											jwd.item,
											jwd.completed_bundle,
											jwd.sqft_allocated,
											CASE
												WHEN jwd.other_work=1 THEN 'YES'
											END,
											jwd.description_for_other_work,
											jwd.rate,
											jwd.amount 
									from tabProject as site
									left outer join `tabTS Job Worker Details` as jwd
										on site.name = jwd.parent 
									{0}
									order by {1}, jwd.start_date, site.name
									""".format(conditions, 'site.name'))

	data = [[format_date(i[0], 'dd-mm-yyyy')]+list(i)[1:] for i in report_data]
	final_data = []
	group=1
	total_sqft=0
	total_amount=0
	currency = frappe.db.get_value("Currency", frappe.db.get_default("currency"), "symbol") or ''
	if(len(data)):
		start = 0
		for i in range(len(data)):
			total_sqft+=data[i][6]
			total_amount+=data[i][10]
		for i in range(len(data)-1):
			if (data[i][group] != data[i+1][group]):
				data[i][6] = "%.2f"%data[i][6]
				final_data.append(data[i][:10]+[f"{currency} %.2f"%data[i][10]])
				total = [" " for i in range(11)]
				total[4] = "<b style=color:rgb(255 82 0);>Total</b>"
				total[5] = frappe.bold("%.2f"%sum(float(data[i][5]) for i in range(start,i+1)))
				total[6] = frappe.bold("%.2f"%sum(float(data[i][6]) for i in range(start,i+1)))
				total[7] = ("")
				total[10] = frappe.bold(f"{currency} %.2f"%sum(float(data[i][10]) for i in range(start,i+1)))
				final_data.append(total)
				total = [None for i in range(11)]
				final_data.append(total)
				start = i+1	
			else:
				data[i][6] = "%.2f"%data[i][6]
				final_data.append(data[i][:10]+[f"{currency} %.2f"%data[i][10]])
				
		final_data.append(data[-1])
		total = ["" for i in range(11)]
		total[4] = "<b style=color:rgb(255 82 0);>""Total""</b>"
		total[5] = frappe.bold("%.2f"%sum(float(data[i][5]) for i in range(start,len(data))))
		total[6] = frappe.bold("%.2f"%sum(float(data[i][6]) for i in range(start,len(data))))
		total[7] = ("")
		total[10] = frappe.bold(f"{currency} %.2f"%sum(float(data[i][10]) for i in range(start,len(data))))
		final_data.append(total)
	total = ["" for i in range(11)]
	final_data.append(["" for i in range(11)])
	total[0] = "<b>Total</b>"
	total[6] = frappe.bold("%.2f"%total_sqft)
	total[10] = frappe.bold(f"{currency} %.2f"%total_amount)
	if(filters.get('ts_group_by')!='Job Worker'):
		final_data.append(total)
	
	return final_data, (total_sqft or 0), (total_amount or 0)

def get_columns(filters):
	columns = [
		_("Date") + ":Data/Project:200",
		_("Site Name") + ":Link/Project:200",
		_("Job Worker") + ":Data/Employee:150",
		_("Supervisor") + ":Data/Employee:150",
		_("Item") + ":Link/Item:150",
		_("Bundles") + ":Data:80",
		_("Completed Sqft") + ":Data:130",
		{
			"label": _("Other Work"),
			"fieldtype": "Data",
			"hidden": not filters.get("show_other_work"),
			"width": 100,
   		},
		{
			"label": _("Other Work Desription"),
			"fieldtype": "Data",
			"hidden": not filters.get("show_other_work"),
			"width": 100,
   		},
		_("Rate") + ":Float:100",
		_("Amount") + ":Data:150",
		]
	
	return columns
