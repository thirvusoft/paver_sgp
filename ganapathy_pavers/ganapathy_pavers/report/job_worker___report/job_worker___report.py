# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import datetime
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
        adv_conditions = "where empadv.repay_unclaimed_amount_from_salary=1"
        if site_type:
            conditions += " and site.type='{0}'".format(site_type)
        if from_date and to_date:
            conditions += "  and jwd.start_date between '{0}' and '{1}' ".format(from_date, to_date)
            adv_conditions += " and empadv.posting_date between '{0}' and '{1}' ".format(from_date, to_date)
        if employee:
            conditions += " and jwd.name1 ='{0}' ".format(employee)
        if site_name:
            conditions += " and site.name = '{0}' ".format(site_name)
    report_data = frappe.db.sql(""" select *,(amount + salary_balance - advance_amount)  from (select jwd.name1 as jobworker,site.name,site.status,{3},jwd.other_work, jwd.description_for_other_work,
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
    
    data+=get_employees_to_add(filters, [row[0] for row in data])
    for row in data:
        if row[0] and frappe.db.exists("Employee", row[0]):
            row[7]=get_employee_salary_balance(employee=row[0], from_date=from_date, to_date=to_date)

    data.sort(key = lambda x:x[0])
    
    
    if(len(data)):
        start = 0
        for i in range(len(data)-1):
            if (data[i][0] != data[i+1][0]):
                adv=get_employee_salary_slip_advance_deduction(data[i][0], from_date, to_date, data[i][9])
                data[i][9]=None
                data[i][10]=None
                employee_id=data[i][0]
                data[i][0]=frappe.db.get_value("Employee", data[i][0], "employee_name")
                final_data.append(data[i]+[None])
                total = [" " for i in range(12)]
                total[2] = "<b style=color:rgb(255 82 0);>""Total""</b>"
                total[3] = f"<b>{'%.2f'%sum((data[i][3] or 0) for i in range(start,i+1))}</b>"
                total[4] = f"<b>{'%.2f'%sum((data[i][4] or 0) for i in range(start,i+1))}</b>"
                total[5]=0
                total[7] = sum((data[i][7] or 0) for i in range(start,i+1))
                total[8] = f"<b>{'%.2f'%sum((data[i][8] or 0) for i in range(start,i+1))}</b>"
                total[9] = adv
                amount=sum((data[i][8] or 0) for i in range(start,i+1))
                salary_bal=sum((data[i][7] or 0) for i in range(start,i+1))
                total[10] = round(((amount or 0)+(salary_bal or 0)-(adv or 0)), 2)
                total[11]=get_employee_salary_slip_amount(employee_id, from_date, to_date)
                final_data[-1][7]=None
                final_data.append(total)
                start = i+1	
                c=0
            else:
                data[i][0]=frappe.db.get_value("Employee", data[i][0], "employee_name")
                data[i][7]=None
                data[i][10]=None
                if(c==0):data[i][9]=None
                else:data[i][9]=None
                c+=1
                final_data.append(data[i]+[None])
        adv=get_employee_salary_slip_advance_deduction(data[-1][0], from_date, to_date, data[-1][9])
        data[-1][9]=None
        data[-1][10]=None
        employee_id=data[-1][0]
        data[-1][0]=frappe.db.get_value("Employee", data[-1][0], "employee_name")
        final_data.append(data[-1]+[None])
        total = [" " for i in range(12)]
        total[2] = "<b style=color:rgb(255 82 0);>""Total""</b>"
        total[3] = f"<b>{'%.2f'%sum((data[i][3] or 0) for i in range(start,len(data)))}</b>"
        total[4] = f"<b>{'%.2f'%sum((data[i][4] or 0) for i in range(start,len(data)))}</b>"
        total[5]=0
        total[7] = sum((data[i][7] or 0) for i in range(start,len(data)))
        total[8] = f"<b>{'%.2f'%sum((data[i][8] or 0) for i in range(start,len(data)))}</b>"
        total[9] = adv
        amount=sum((data[i][8] or 0) for i in range(start,len(data)))
        salary_bal=sum((data[i][7] or 0) for i in range(start,len(data)))
        total[10] = round(((amount or 0)+(salary_bal or 0)-(adv or 0)), 2)
        total[11]=get_employee_salary_slip_amount(employee_id, from_date, to_date)
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
    return columns, [row for row in final_data]

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
    last_ss_date=frappe.db.sql(f"""
    SELECT MAX(ss.end_date) 
    FROM `tabSalary Slip` ss
    WHERE ss.employee = '{employee}' AND ss.docstatus=1
    """)
    amount=0
    salary_slip=frappe.db.sql("""select total_unpaid_amount from `tabSalary Slip` where start_date >= %(from)s and end_date <=%(to)s and employee=%(emp)s and docstatus=1 order by posting_date desc,modified desc limit 1""",{"emp":employee, "from":from_date, "to":to_date},as_dict=True)
    salary_slip1=frappe.db.sql("""select total_unpaid_amount from `tabSalary Slip` where employee=%(emp)s and end_date<=%(to)s  and docstatus=1 order by posting_date desc,modified desc limit 1""",{"emp":employee,"from":from_date, "to":to_date},as_dict=True)
    conditions=f"""
    where jwd.name1='{employee}' and jwd.end_date < '{from_date}' 
    """
    if last_ss_date[0][0]:
        conditions+=f""" and jwd.start_date > '{datetime.datetime.strftime(last_ss_date[0][0], "%Y-%m-%d")}'"""
    if not last_ss_date[0][0] or datetime.datetime.strptime(from_date, "%Y-%m-%d").date()>last_ss_date[0][0]:
        amount=frappe.db.sql(f"""
        SELECT sum(jwd.amount)
        from `tabProject` as site
        left outer join `tabTS Job Worker Details` as jwd
            on site.name = jwd.parent
        {conditions}
        """)[0][0] or 0
    if salary_slip:
        return salary_slip[0]["total_unpaid_amount"]+amount

    elif(salary_slip1):
        return salary_slip1[0]["total_unpaid_amount"]+amount

def get_employee_salary_slip_amount(employee, from_date, to_date):
    query=f"""
        SELECT SUM(ss.paid_amount)
        FROM `tabSalary Slip` ss
        WHERE ss.docstatus=1 AND ss.employee='{employee}' AND ss.start_date >= '{from_date}' AND ss.end_date <= '{to_date}'
    """
    res=frappe.db.sql(query)[0][0]
    return res

def get_employee_salary_slip_advance_deduction(employee, from_date, to_date, adv):
    if frappe.db.get_all('Salary Slip', {'employee': employee, 'start_date': [">=", from_date], 'end_date': ["<=", to_date], "docstatus": 1}):
        query=f"""
            SELECT SUM(ss.total_deduction)
            FROM `tabSalary Slip` ss
            WHERE ss.docstatus=1 AND ss.employee='{employee}' AND ss.start_date >= '{from_date}' AND ss.end_date <= '{to_date}'
        """
        res=frappe.db.sql(query)[0][0]
        return res
    planned_deduction=0
    planned_deduction=frappe.db.sql(f"""
        SELECT 
            SUM(dp.amount)
        FROM `tabDeduction Planning` dp
        LEFT OUTER JOIN `tabEmployee Advance` ea
            ON ea.name=dp.parent
        WHERE 
            ea.docstatus=1 
            AND ea.employee='{employee}'
            AND dp.date between '{from_date}' and '{to_date}'
            AND ea.repay_unclaimed_amount_from_salary=1
    """)[0][0]
    return planned_deduction or adv

def get_employees_to_add(filters, employees):
    employees=list(set(employees))
    emp_filters={"status": ["!=", "Inactive"], "name": ["not in", employees], "designation": "Job Worker"}
    if filters.get("employee") and filters.get("employee") in employees:
        return[]
    elif filters.get("employee"):
        emp_filters["name"] = filters.get("employee")
    rem = frappe.get_all("Employee", emp_filters, pluck='name')
    return [[emp]+ [None for i in range(10)] for emp in rem]