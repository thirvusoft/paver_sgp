# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
def execute(filters=None):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    employee = filters.get("employee")
    site_name = filters.get("site_name")
    group_by_site=", site.name" if filters.get("group_site_work") else ""
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
    report_data = frappe.db.sql(""" select *,(amount + salary_balance - advance_amount) from (select (select employee_name from `tabEmployee` where name = jwd.name1 ) as jobworker,site.name,site.status,jwd.sqft_allocated,jwd.other_work, jwd.description_for_other_work,
                                        emp.salary_balance as salary_balance,jwd.amount as amount,
                                        (select sum(empadv.advance_amount) from `tabEmployee Advance` as empadv {1} and empadv.employee = jwd.name1 and docstatus = 1) as advance_amount
                                        from `tabProject` as site
                                        left outer join `tabTS Job Worker Details` as jwd
                                            on site.name = jwd.parent
                                        left outer join `tabEmployee` as emp
                                            on emp.employee = jwd.name1
                                        {0}
                                    group by jwd.name1{2},jwd.sqft_allocated order by jwd.sqft_allocated)as total_cal
                                """.format(conditions,adv_conditions, group_by_site))
    data = [list(i) for i in report_data]
    final_data = []
    c = 0
    if filters.get("group_site_work"):
        data1={}
        for idx in range(len(data)):
            _key=f"{data[idx][0]}---{data[idx][1]}"
            if _key not in data1:
                data1[_key]=data[idx]
            else:
                data1[_key][3]+=(data[idx][3] or 0)
                data1[_key][7]+=(data[idx][7] or 0)
        data=list(data1.values())
    if(len(data)):
        start = 0
        for i in range(len(data)-1):
            if (data[i][0] != data[i+1][0]):
                adv=data[i][8]
                data[i][8]=0
                final_data.append(data[i])
                total = [" " for i in range(10)]
                total[2] = "<b style=color:orange;>""Total""</b>"
                total[3] = f"<b>{'%.2f'%sum((data[i][3] or 0) for i in range(start,i+1))}</b>"
                total[4]=0
                total[6] = sum((data[i][6] or 0) for i in range(start,i+1))
                total[7] = f"<b>{'%.2f'%sum((data[i][7] or 0) for i in range(start,i+1))}</b>"
                total[8] = adv
                total[9] = f"<b>{'%.2f'%sum((data[i][9] or 0) for i in range(start,i+1))}</b>"
                final_data[-1][6]=0
                final_data.append(total)
                start = i+1	
                c=0
            else:
                data[i][6]=0
                if(c==0):data[i][8]=0
                else:data[i][8]=0
                c+=1
                final_data.append(data[i])
        adv=data[-1][8]
        data[-1][8]=0
        final_data.append(data[-1])
        total = [" " for i in range(10)]
        total[2] = "<b style=color:orange;>""Total""</b>"
        total[3] = f"<b>{'%.2f'%sum((data[i][3] or 0) for i in range(start,len(data)))}</b>"
        total[4]=0
        total[6] = sum((data[i][6] or 0) for i in range(start,len(data)))
        total[7] = f"<b>{'%.2f'%sum((data[i][7] or 0) for i in range(start,len(data)))}</b>"
        total[8] = adv
        total[9] = f"<b>{'%.2f'%sum((data[i][9] or 0) for i in range(start,len(data)))}</b>"
        final_data[-1][6]=0
        final_data.append(total)
    other_work=0
    for row in final_data:
        if row[4]:
            row[4]="Yes"
            other_work=1
        else:
            row[4]=""
            row[5]=""
    columns = get_columns(other_work)
    
    return columns, final_data

def get_columns(other_work):
	columns = [
		_("Job Worker") + ":Data/Employee:150",
		_("Site Name") + ":Link/Project:150",
		_("Status") + ":Data/Project:150",
		_("Completed Sqft") + ":Data:150",
        {
            "fieldname": "other_work",
            "label": "Other Work",
            "fieldtype": "Data",
            "hidden": not other_work
        },
        {
            "fieldname": "other_work_description",
            "label": "Other Work Description",
            "fieldtype": "Data",
            "hidden": not other_work
        },
		_("Salary Balance") + ":Data:150",
		_("Amount") + ":Data:150",
		_("Advance Amount") + ":Data:150",
		_("Total Amount") + ":Data:150",
		]
	
	return columns
