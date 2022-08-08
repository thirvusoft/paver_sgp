# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
def execute(filters=None):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    employee = filters.get("employee")
    site_name = filters.get("site_name")
    conditions = ""
    adv_conditions = ""
    if from_date or to_date or employee or site_name:
        conditions = " where 1 = 1"
        adv_conditions = "where 1 = 1"
        if from_date and to_date:
            conditions += "  and jwd.start_date between '{0}' and '{1}' ".format(from_date, to_date)
            adv_conditions += " and empadv.posting_date between '{0}' and '{1}' ".format(from_date, to_date)
        if employee:
            conditions += " and jwd.name1 ='{0}' ".format(employee)
        if site_name:
            conditions += " and site.name = '{0}' ".format(site_name)
    report_data = frappe.db.sql(""" select *,(amount + salary_balance - advance_amount) from (select (select employee_name from `tabEmployee` where name = jwd.name1 ) as jobworker,site.name,site.status,jwd.sqft_allocated,
                                        emp.salary_balance as salary_balance,jwd.amount as amount,
                                        (select sum(empadv.advance_amount - empadv.return_amount) from `tabEmployee Advance` as empadv {1} and empadv.employee = jwd.name1 and docstatus = 1) as advance_amount
                                        from `tabProject` as site
                                        left outer join `tabTS Job Worker Details` as jwd
                                            on site.name = jwd.parent
                                        left outer join `tabEmployee` as emp
                                            on emp.employee = jwd.name1
                                        {0}
                                    group by jwd.name1,jwd.sqft_allocated)as total_cal
                                """.format(conditions,adv_conditions))
    data = [list(i) for i in report_data]
    final_data = []
    c = 0
    
    if(len(data)):
        start = 0
        for i in range(len(data)-1):
            if (data[i][0] != data[i+1][0]):
                adv=data[i][6]
                data[i][6]=[]
                final_data.append(data[i])
                total = [" " for i in range(8)]
                total[2] = "<b style=color:orange;>""Total""</b>"
                total[3] = sum((data[i][3] or 0) for i in range(start,i+1))
                total[4] = sum((data[i][4] or 0) for i in range(start,i+1))
                total[5] = sum((data[i][5] or 0) for i in range(start,i+1))
                total[6] = adv
                total[7] = sum((data[i][7] or 0) for i in range(start,i+1))
                final_data.append(total)
                start = i+1	
                c=0
            else:
                if(c==0):data[i][6]=()
                else:data[i][6]=()
                c+=1
                final_data.append(data[i])
        adv=data[-1][6]
        data[-1][6]=()      
        final_data.append(data[-1])
        total = [" " for i in range(8)]
        total[2] = "<b style=color:orange;>""Total""</b>"
        total[3] = sum((data[i][3] or 0) for i in range(start,len(data)))
        total[4] = sum((data[i][4] or 0) for i in range(start,len(data)))
        total[5] = sum((data[i][5] or 0) for i in range(start,len(data)))
        total[6] = adv
        total[7] = sum((data[i][7] or 0) for i in range(start,len(data)))
        final_data.append(total)
    columns = get_columns()
    return columns, final_data

def get_columns():
	columns = [
		_("Job Worker") + ":Data/Employee:150",
		_("Site Name") + ":Link/Project:150",
		_("Status") + ":Data/Project:150",
		_("Completed Sqft") + ":Data:150",
		_("Salary Balance") + ":Currency:150",
		_("Amount") + ":Currency:150",
		_("Advance Amount") + ":Currency:150",
		_("Total Amount") + ":Currency:150",
		]
	
	return columns
