# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
def execute(filters=None):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    employee = filters.get("employee")
    site_name = filters.get("site_name")
    site_type = filters.get("type")
    group_by_site="group by jwd.name1, site.name ,jwd.sqft_allocated, jwd.start_date, jwd.end_date, jwd.description_for_other_work" if filters.get("group_site_work") else ""
    conditions = ""
    adv_conditions = ""
    if from_date or to_date or employee or site_name or site_type:
        conditions = " where 1=1"
        adv_conditions = "where 1 = 1"
        if site_type:
            conditions += " and site.type='{0}'".format(site_type)
        if from_date and to_date:
            conditions += "  and jwd.start_date between '{0}' and '{1}' ".format(from_date, to_date)
            adv_conditions += " and empadv.posting_date between '{0}' and '{1}' ".format(from_date, to_date)
        if employee:
            conditions += " and jwd.name1 ='{0}' ".format(employee)
        if site_name:
            conditions += " and site.name = '{0}' ".format(site_name)
    report_data = frappe.db.sql(""" select *,(amount + salary_balance - advance_amount) from (select jwd.name1 as jobworker,site.name,site.status,{3},jwd.other_work, jwd.description_for_other_work,
                                        emp.salary_balance as salary_balance,{4} as amount,
                                        (select sum(empadv.advance_amount) from `tabEmployee Advance` as empadv {1} and empadv.employee = jwd.name1 and docstatus = 1) as advance_amount
                                        from `tabProject` as site
                                        left outer join `tabTS Job Worker Details` as jwd
                                            on site.name = jwd.parent
                                        left outer join `tabEmployee` as emp
                                            on emp.employee = jwd.name1
                                        {0}
                                    {2} order by jwd.sqft_allocated)as total_cal
                                """.format(conditions+ " and jwd.other_work = 0",adv_conditions, group_by_site, "sum(jwd.completed_bundle), sum(jwd.sqft_allocated)" if filters.get("group_site_work") else "jwd.completed_bundle, jwd.sqft_allocated", "sum(jwd.amount)" if filters.get("group_site_work") else "jwd.amount"))
    
    report_data1 = frappe.db.sql(""" select *,(amount + salary_balance - advance_amount) from (select jwd.name1 as jobworker,site.name,site.status,{3},jwd.other_work, jwd.description_for_other_work,
                                        emp.salary_balance as salary_balance,{4} as amount,
                                        (select sum(empadv.advance_amount) from `tabEmployee Advance` as empadv {1} and empadv.employee = jwd.name1 and docstatus = 1) as advance_amount
                                        from `tabProject` as site
                                        left outer join `tabTS Job Worker Details` as jwd
                                            on site.name = jwd.parent
                                        left outer join `tabEmployee` as emp
                                            on emp.employee = jwd.name1
                                        {0}
                                    group by jwd.name1{2},jwd.sqft_allocated, jwd.start_date, jwd.end_date, jwd.description_for_other_work order by jwd.sqft_allocated)as total_cal
                                """.format(conditions+" and jwd.other_work = 1",adv_conditions, "", "sum(jwd.completed_bundle), sum(jwd.sqft_allocated)" if filters.get("group_site_work") else "jwd.completed_bundle, jwd.sqft_allocated", "sum(jwd.amount)" if filters.get("group_site_work") else "jwd.amount"))
    data = [list(i) for i in (report_data or tuple())]
    final_data = []
    c = 0
    if filters.get("group_site_work"):
        data1={}
        for idx in range(len(data)):
            _key=f"{data[idx][0]}---{data[idx][1]}"
            if _key not in data1 or data[idx][5]:
                data1[_key]=data[idx]
            else:
                data1[_key][3]+=(data[idx][3] or 0)
                data1[_key][4]+=(data[idx][4] or 0)
                data1[_key][8]+=(data[idx][8] or 0)
        data=list(data1.values())
    data = [list(i) for i in (report_data1 or [])] + data

    

    for row in data:
        if row[0] and frappe.db.exists("Employee", row[0]):
            row[7]=get_employee_salary_balance(employee=row[0], from_date=from_date, to_date=to_date)
            row[0]=frappe.db.get_value("Employee", row[0], "employee_name")

    data.sort(key = lambda x:x[0])
   
    
    if(len(data)):
        start = 0
        for i in range(len(data)-1):
            if (data[i][0] != data[i+1][0]):
                adv=data[i][9]
                data[i][9]=None
                data[i][10]=None
                final_data.append(data[i])
                total = [" " for i in range(11)]
                total[2] = "<b style=color:orange;>""Total""</b>"
                total[3] = f"<b>{'%.2f'%sum((data[i][3] or 0) for i in range(start,i+1))}</b>"
                total[4] = f"<b>{'%.2f'%sum((data[i][4] or 0) for i in range(start,i+1))}</b>"
                total[5]=0
                total[7] = sum((data[i][7] or 0) for i in range(start,i+1))
                total[8] = f"<b>{'%.2f'%sum((data[i][8] or 0) for i in range(start,i+1))}</b>"
                total[9] = adv
                amount=sum((data[i][8] or 0) for i in range(start,i+1))
                salary_bal=sum((data[i][7] or 0) for i in range(start,i+1))
                total[10] = round(((amount or 0)+(salary_bal or 0)-(adv or 0)), 2)
                final_data[-1][7]=None
                final_data.append(total)
                start = i+1	
                c=0
            else:
                data[i][7]=None
                data[i][10]=None
                if(c==0):data[i][9]=None
                else:data[i][9]=None
                c+=1
                final_data.append(data[i])
        adv=data[-1][9]
        data[-1][9]=None
        data[-1][10]=None
        final_data.append(data[-1])
        total = [" " for i in range(11)]
        total[2] = "<b style=color:orange;>""Total""</b>"
        total[3] = f"<b>{'%.2f'%sum((data[i][3] or 0) for i in range(start,len(data)))}</b>"
        total[4] = f"<b>{'%.2f'%sum((data[i][4] or 0) for i in range(start,len(data)))}</b>"
        total[5]=0
        total[7] = sum((data[i][7] or 0) for i in range(start,len(data)))
        total[8] = f"<b>{'%.2f'%sum((data[i][8] or 0) for i in range(start,len(data)))}</b>"
        total[9] = adv
        amount=sum((data[i][8] or 0) for i in range(start,len(data)))
        salary_bal=sum((data[i][7] or 0) for i in range(start,len(data)))
        total[10] = round(((amount or 0)+(salary_bal or 0)-(adv or 0)), 2)
        final_data[-1][7]=None
        final_data.append(total)
    other_work=0
    for row in final_data:
        if row[5]:
            row[5]="Yes"
            other_work=1
        else:
            row[5]=""
            row[6]=""
    columns = get_columns(other_work)
  
    return columns, [row+[None] for row in final_data]

def get_columns(other_work):
	columns = [
		_("Job Worker") + ":Data/Employee:150",
		_("Site Name") + ":Link/Project:100",
		_("Status") + ":Data/Project:150",
        {
            "fieldname": "bundle",
            "label": "Bundle",
            "fieldtype": "Data",
            "ts_right_align": "text-right"
        },
		{
            "fieldname": "sfqt",
            "label": "SQFT",
            "fieldtype": "Data",
            "ts_right_align": "text-right"
        },
        {
            "fieldname": "other_work",
            "label": "Other Work",
            "fieldtype": "Data",
            "hidden": not other_work,
        },
        {
            "fieldname": "other_work_description",
            "label": "Other Work Description",
            "fieldtype": "Data",
            "hidden": not other_work
        },
        {
            "fieldname": "salary_balance",
            "label": "Salary Balance",
            "fieldtype": "Data",
            "ts_right_align": "text-right"
        },
		{
            "fieldname": "amount",
            "label": "Amount",
            "fieldtype": "Data",
            "ts_right_align": "text-right"
        },
		{
            "fieldname": "advance_deduction",
            "label": "Advance Deduction",
            "fieldtype": "Data",
            "ts_right_align": "text-right"
        },
		{
            "fieldname": "total_amount",
            "label": "Total Amount",
            "fieldtype": "Data",
            "ts_right_align": "text-right"
        },
        {
            "fieldname": "payment",
            "label": "Payment",
            "fieldtype": "Data",
            "default": None,
            "width": 150,
            "ts_right_align": "text-right"
        }
		]
	
	return columns

def get_employee_salary_balance(employee, from_date, to_date):
   
    salary_slip=frappe.db.sql("""select total_unpaid_amount from `tabSalary Slip` where posting_date between %(from)s and %(to)s and employee=%(emp)s and docstatus=1 order by posting_date desc,modified desc limit 1""",{"emp":employee, "from":from_date, "to":to_date},as_dict=True)
    salary_slip1=frappe.db.sql("""select total_unpaid_amount from `tabSalary Slip` where employee=%(emp)s and posting_date<=%(from)s  and docstatus=1 order by posting_date desc,modified desc limit 1""",{"emp":employee,"from":from_date},as_dict=True)
    salary_slip2=frappe.db.sql("""select salary_balance from `tabEmployee` where name=%(emp)s """,{"emp":employee},as_dict=True)
    if salary_slip:
        return salary_slip[0]["total_unpaid_amount"]

    elif(salary_slip1):
        return salary_slip1[0]["total_unpaid_amount"]
    else:
        return salary_slip2[0]["salary_balance"]
