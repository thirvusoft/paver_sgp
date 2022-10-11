# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt
from locale import currency
import frappe
from frappe import _, errprint
from frappe.utils import format_date

def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	employee = filters.get("employee")
	site_name = filters.get("site_name")
	conditions = ""
	if from_date or to_date or employee or site_name:
		conditions = " where 1 = 1"
		if from_date and to_date:
			conditions += "  and jwd.start_date between '{0}' and '{1}' ".format(from_date, to_date)
		if employee:
			conditions += " and jwd.name1 ='{0}' ".format(employee)
		if site_name:
			conditions += " and site.name = '{0}' ".format(site_name)

	report_data = frappe.db.sql(""" select  jwd.start_date,
											site.name,
											(select employee_name from `tabEmployee` where name = jwd.name1 ) as jobworker,
											site.supervisor_name,
											jwd.item,
											jwd.completed_bundle,
											jwd.sqft_allocated,
											jwd.rate,
											jwd.amount 
									from tabProject as site
									left outer join `tabTS Job Worker Details` as jwd
										on site.name = jwd.parent 
									{0}
									order by {1}, jwd.start_date, site.name
									""".format(conditions, 'site.name' if(filters.get('group_by')=='Site Name') else 'jobworker'))

	data = [[format_date(i[0], 'dd-mm-yyyy')]+list(i)[1:] for i in report_data]
	final_data = []
	group=1
	total_sqft=0
	total_amount=0
	currency = frappe.db.get_value("Currency", frappe.db.get_default("currency"), "symbol") or ''
	if(filters.get('group_by')=='Job Worker'):
		group=2
	if(len(data)):
		start = 0
		for i in range(len(data)):
			total_sqft+=data[i][6]
			total_amount+=data[i][8]
		for i in range(len(data)-1):
			if (data[i][group] != data[i+1][group]):
				data[i][6] = "%.2f"%data[i][6]
				final_data.append(data[i][:8]+[f"{currency} %.2f"%data[i][8]])
				total = [" " for i in range(9)]
				total[5] = "<b style=color:orange;>""Total""</b>"
				total[6] = frappe.bold("%.2f"%sum(float(data[i][6]) for i in range(start,i+1)))
				total[7] = ("")
				total[8] = frappe.bold(f"{currency} %.2f"%sum(float(data[i][8]) for i in range(start,i+1)))
				final_data.append(total)
				total = [None for i in range(9)]
				final_data.append(total)
				start = i+1	
			else:
				data[i][6] = "%.2f"%data[i][6]
				final_data.append(data[i][:8]+[f"{currency} %.2f"%data[i][8]])
				
		final_data.append(data[-1])
		total = ["" for i in range(9)]
		total[5] = "<b style=color:orange;>""Total""</b>"
		total[6] = frappe.bold("%.2f"%sum(float(data[i][6]) for i in range(start,len(data))))
		total[7] = ("")
		total[8] = frappe.bold(f"{currency} %.2f"%sum(float(data[i][8]) for i in range(start,len(data))))
		final_data.append(total)
	total = ["" for i in range(9)]
	final_data.append(["" for i in range(9)])
	total[0] = "<b>Total</b>"
	total[6] = frappe.bold("%.2f"%total_sqft)
	total[8] = frappe.bold(f"{currency} %.2f"%total_amount)
	final_data.append(total)
	columns = get_columns()
	return columns, final_data

def get_columns():
	columns = [
		_("Date") + ":Data/Project:100",
		_("Site Name") + ":Link/Project:200",
		_("Job Worker") + ":Data/Employee:150",
		_("Supervisor") + ":Data/Employee:150",
		_("Item") + ":Link/Item:150",
		_("Bundles") + ":Data:80",
		_("Completed Sqft") + ":Data:130",
		_("Rate") + ":Currency:100",
		_("Amount") + ":Data:150",
		]
	
	return columns
