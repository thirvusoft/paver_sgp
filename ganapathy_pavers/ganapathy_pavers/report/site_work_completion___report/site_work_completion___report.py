# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt
import frappe
from frappe import _, errprint
def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	employee = filters.get("employee")
	site_name = filters.get("status")
	conditions = ""
	if from_date or to_date or employee or site_name:
		conditions = " where 1 = 1"
		if from_date and to_date:
			conditions += "  and jwd.start_date between '{0}' and '{1}' ".format(from_date, to_date)
		if employee:
			conditions += " and jwd.name1 ='{0}' ".format(employee)
		if site_name:
			conditions += " and site.name = '{0}' ".format(site_name)

	report_data = frappe.db.sql(""" select jwd.start_date,site.name,
											(select employee_name from `tabEmployee` where name = jwd.name1 ) as jobworker,
											site.supervisor_name,jwd.item,
											jwd.completed_bundle,jwd.sqft_allocated,jwd.rate,jwd.amount 
									from tabProject as site
									left outer join `tabTS Job Worker Details` as jwd
										on site.name = jwd.parent 
									{0}
									group by site.name,jwd.name1,jwd.sqft_allocated
									""".format(conditions))

	data = [list(i) for i in report_data]
	final_data = []
	start = 0
	for i in range(len(data)-1):
		if (data[i][1] != data[i+1][1]):
			final_data.append(data[i])
			total = [" " for i in range(9)]
			total[5] = "<b style=color:orange;>""Total""</b>"
			total[6] = sum(data[i][6] for i in range(start,i+1))
			total[7] = ("NaN" for i in range(start,i+1))
			total[8] = sum(data[i][8] for i in range(start,i+1))
			final_data.append(total)
			start = i+1	
		else:
			final_data.append(data[i])
			
	final_data.append(data[-1])
	total = [" " for i in range(9)]
	total[5] = "<b style=color:orange;>""Total""</b>"
	total[6] = sum(data[i][6] for i in range(start,len(data)))
	total[7] = ("NaN" for i in range(start,i+1))
	total[8] = sum(data[i][8] for i in range(start,len(data)))
	final_data.append(total)
	columns = get_columns()
	return columns, final_data

def get_columns():
	columns = [
		_("Date") + ":Date/Project:100",
		_("Site Name") + ":Link/Project:200",
		_("Job Worker") + ":Data/Employee:150",
		_("Supervisor") + ":Data/Employee:150",
		_("Item") + ":Link/Item:150",
		_("Bundles") + ":Data:80",
		_("Completed Sqft") + ":Data:130",
		_("Rate") + ":Currency:100",
		_("Amount") + ":Currency:150",
		]
	
	return columns