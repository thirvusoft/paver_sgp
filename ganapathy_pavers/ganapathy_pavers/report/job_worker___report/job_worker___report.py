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
            conditions += " and emp.paver=1" if site_type=="Pavers" else " and emp.compound_wall=1"
        if from_date and to_date:
            conditions += "  and jwd.start_date >= '{0}' and jwd.end_date <= '{1}'".format(from_date, to_date)
            adv_conditions += " and empadv.posting_date between '{0}' and '{1}' ".format(from_date, to_date)
        if employee:
            conditions += " and jwd.name1 ='{0}' ".format(employee)
        if site_name:
            conditions += " and site.name = '{0}' ".format(site_name)
    if filters.get('show_only_other_work'):
        report_data=[]
    else:
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
                                """.format(conditions+ " and jwd.other_work = 0",adv_conditions, group_by_site, "sum(jwd.completed_bundle), sum(jwd.sqft_allocated), avg(jwd.rate)" if filters.get("group_site_work") else "jwd.completed_bundle, jwd.sqft_allocated, jwd.rate", (("sum(jwd.amount)" if filters.get("group_site_work") else "jwd.amount"))))
 
    if filters.get("hide_other_work"):
        report_data1=[]
    else:
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
                                """.format(conditions+" and jwd.other_work = 1",adv_conditions, "", "sum(jwd.completed_bundle), sum(jwd.sqft_allocated), avg(jwd.rate)" if filters.get("group_site_work") else "jwd.completed_bundle, jwd.sqft_allocated, jwd.rate", "sum(jwd.amount)" if filters.get("group_site_work") else "jwd.amount"))
    data = [list(i) for i in (report_data or tuple())]
    final_data = []
    c = 0
    if filters.get("group_site_work"):
        data1={}
        count={}
        for idx in range(len(data)):
            _key=f"{data[idx][0]}---{data[idx][1]}"
            if _key not in count:
                count[_key]=0
            count[_key]+=1
            if _key not in data1 or data[idx][6]:
                data1[_key]=data[idx]
            else:
                data1[_key][3]+=(data[idx][3] or 0)
                data1[_key][4]+=(data[idx][4] or 0)
                data1[_key][5]+=(data[idx][5] or 0)
                data1[_key][9]+=(data[idx][9] or 0)

        for _key in data1:
            data1[_key][5] = (data1[_key][5] / count[_key]) if count[_key] else data1[_key][5]
        data=list(data1.values())
    data = [list(i) for i in (report_data1 or [])] + data
    
    if not filters.get('show_only_other_work'):
        data+=get_employees_to_add(filters, [row[0] for row in data])

    for row in data:
        if row[0] and frappe.db.exists("Employee", row[0]):
            row[8]=get_employee_salary_balance(employee=row[0], from_date=from_date, to_date=to_date)

    data.sort(key = lambda x:(x[0] or ""))
    
    _data = []
    for idx in range(len(data)):
        _data.append(data[idx])
        if idx+1 == len(data) or data[idx+1][0] != data[idx][0]:
            credit = frappe.db.sql(f"""
                select
                    jea.party,
                    sum(jea.credit) as amount,
                    je.salary_component as component
                from `tabJournal Entry Account` jea
                inner join `tabJournal Entry` je 
                on jea.parenttype="Journal Entry" and jea.parent=je.name
                where
                    je.docstatus=1 and
                    je.voucher_type="Credit Note" and
                    je.posting_date between '{from_date}' and '{to_date}' and
                    jea.party_type='Employee' and
                    jea.party='{data[idx][0]}' and
                    ifnull(je.salary_component, '')!=''
            """, as_dict=True)
            if credit[0].amount:
                _data.append([
                    credit[0].party,
                    credit[0].component,
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    _data[idx][8],
                    credit[0].amount,
                    '',
                    '',
                ])
    data = _data

    if(len(data)):
        start = 0
        for i in range(len(data)-1):
            if (data[i][0] != data[i+1][0]):
                adv=get_employee_salary_slip_advance_deduction(data[i][0], from_date, to_date, data[i][10])
                data[i][10]=None
                data[i][11]=None
                employee_id=data[i][0]
                data[i][0]=frappe.db.get_value("Employee", data[i][0], "employee_name")
                final_data.append(data[i]+[None])
                total = [" " for i in range(13)]
                total[0] = f"""<b style="font-size: 20px;text-align: center; color:green">{data[i][0]}</b>"""
                total[2] = "Total"
                total[3] = sum((data[i][3] or 0) for i in range(start,i+1))
                total[4] = sum((data[i][4] or 0) for i in range(start,i+1))
                total[5] = None#sum((data[i][5] or 0) for i in range(start,i+1))
                total[6]=0
                salary_bal=sum((data[i][8] or 0) for i in range(start,i+1))
                if salary_bal < 0:
                    salary_bal = 0
                total[8] = salary_bal
                total[9] = sum((data[i][9] or 0) for i in range(start,i+1))
                total[10] = adv
                amount=sum((data[i][9] or 0) for i in range(start,i+1))
                total_amt=round(((amount or 0)+(salary_bal or 0)-(adv or 0)), 2)
                total[11] = total_amt
                total[12]=get_employee_salary_slip_amount(employee_id, from_date, to_date)
                final_data[-1][8]=None
                final_data.append(total)
                start = i+1	
                c=0
            else:
                data[i][0]=frappe.db.get_value("Employee", data[i][0], "employee_name")
                data[i][8]=None
                data[i][11]=None
                if(c==0):data[i][10]=None
                else:data[i][10]=None
                c+=1
                final_data.append(data[i]+[None])
        adv=get_employee_salary_slip_advance_deduction(data[-1][0], from_date, to_date, data[-1][10])
        data[-1][10]=None
        data[-1][11]=None
        employee_id=data[-1][0]
        data[-1][0]=frappe.db.get_value("Employee", data[-1][0], "employee_name")
        final_data.append(data[-1]+[None])
        total = [" " for i in range(13)]
        total[0] = f"""<b style="font-size: 20px;text-align: center; color:green">{data[-1][0]}</b>"""
        total[2] = "Total"
        total[3] = sum((data[i][3] or 0) for i in range(start,len(data)))
        total[4] = sum((data[i][4] or 0) for i in range(start,len(data)))
        total[5] = None#sum((data[i][5] or 0) for i in range(start,len(data)))
        total[6]=0
        salary_bal=sum((data[i][8] or 0) for i in range(start,len(data)))
        if salary_bal<0:
            salary_bal=0
        total[8] = salary_bal
        total[9] = sum((data[i][9] or 0) for i in range(start,len(data)))
        total[10] = adv
        amount=sum((data[i][9] or 0) for i in range(start,len(data)))
        
        total_amt = round(((amount or 0)+(salary_bal or 0)-(adv or 0)), 2)
        total[11] = total_amt
        total[12]=get_employee_salary_slip_amount(employee_id, from_date, to_date)
        final_data[-1][8]=None
        final_data.append(total)
    other_work=0
    for row in final_data:
        if row[6]:
            row[6]="Yes"
            other_work=1
        else:
            row[6]=""
            row[7]=""
    columns = get_columns(other_work)
    return columns, add_total_row(final_data, index = 11)

def add_total_row(data, index=None):
    res=[]
    if data and data[0]:
        res=[0 for i in range(len(data[0]))]
        for row in data:
            if res and row[2]=="Total":
                res=add_list(row, res, index)
        res[0]="Total"
    return data+[res] if res else data

def add_list(a, b, index=None):
    ret_list1 = []
    for i in range(len(a)):
        if((isinstance(a[i], int) or isinstance(a[i], float)) and (isinstance(b[i], int) or isinstance(b[i], float))):
            if (i==index and a[i]<0):
                ret_list1.append(b[i])
                continue
            ret_list1.append(a[i] + b[i])
        else:
            ret_list1.append(None)
    return ret_list1

def get_columns(other_work):
	columns = [
		_("Job Worker") + ":Data/Employee:150",
		_("Site Name") + ":Link/Project:100",
		_("Status") + ":Data/Project:150",
        {
            "fieldname": "bundle",
            "label": "Bundle",
            "fieldtype": "Int",
            "ts_right_align": "text-right"
        },
		{
            "fieldname": "sfqt",
            "label": "SQFT",
            "fieldtype": "Float",
            "ts_right_align": "text-right"
        },
        {
            "fieldname": "rate",
            "label": "Rate",
            "fieldtype": "Float",
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
            "hidden": not other_work,
            "width": 150,
        },
        {
            "fieldname": "salary_balance",
            "label": "Salary Balance",
            "fieldtype": "Float",
            "ts_right_align": "text-right"
        },
		{
            "fieldname": "amount",
            "label": "Amount",
            "fieldtype": "Float",
            "ts_right_align": "text-right"
        },
		{
            "fieldname": "advance_deduction",
            "label": "Advance Deduction",
            "fieldtype": "Float",
            "ts_right_align": "text-right"
        },
		{
            "fieldname": "total_amount",
            "label": "Total Amount",
            "fieldtype": "Float",
            "ts_right_align": "text-right"
        },
        {
            "fieldname": "payment",
            "label": "Payment",
            "fieldtype": "Float",
            "default": None,
            "minWidth": 120,
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
    salary_slip=frappe.db.sql("""select salary_balance as total_unpaid_amount from `tabSalary Slip` where start_date >= %(from)s and end_date <=%(to)s and employee=%(emp)s and docstatus=1 order by posting_date desc,modified desc limit 1""",{"emp":employee, "from":from_date, "to":to_date},as_dict=True)
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
    return round((amount or 0), 2)

def get_employee_salary_slip_amount(employee, from_date, to_date):
    query=f"""
        SELECT SUM(ss.paid_amount)
        FROM `tabSalary Slip` ss
        WHERE ss.docstatus=1 AND ss.employee='{employee}' AND ss.start_date >= '{from_date}' AND ss.end_date <= '{to_date}'
    """
    res=frappe.db.sql(query)[0][0]
    return round((res or 0), 2) or ""

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
    debit_note = frappe.db.sql(f"""
                select
                    sum(jea.debit) as amount
                from `tabJournal Entry Account` jea
                inner join `tabJournal Entry` je 
                on jea.parenttype="Journal Entry" and jea.parent=je.name
                where
                    je.docstatus=1 and
                    je.voucher_type="Debit Note" and
                    je.posting_date between '{from_date}' and '{to_date}' and
                    jea.party_type='Employee' and
                    jea.party='{employee}' and
                    ifnull(je.salary_component, '')!=''
            """)[0][0]
    return round(((planned_deduction or 0) + (debit_note or 0)), 2) or 0#get_undeducted_advances(employee, from_date, to_date)

def get_undeducted_advances(employee, from_date, to_date):
    res= frappe.db.sql(f"""
        SELECT SUM(ads.amount - ifnull(ads.salary_slip_amount, 0))
        FROM `tabAdditional Salary` ads
        WHERE ads.docstatus=1 
        AND ads.employee="{employee}"
        AND ads.payroll_date <= '{to_date}'
    """)[0][0]
    return round((res or 0), 2)

def get_employees_to_add(filters, employees):
    employees=list(set(employees))
    emp_filters={"status": ["!=", "Inactive"], "name": ["not in", employees], "designation": "Job Worker"}
    if filters.get("employee") and filters.get("employee") in employees:
        return []
    
    elif filters.get("employee"):
        emp_filters["name"] = filters.get("employee")

    elif filters.get("site_name"):
        emp_list=[]
        emp=frappe.db.sql(f"""
            SELECT jw.name1
            FROM `tabTS Job Worker Details` jw
            WHERE jw.parenttype="Project" 
            AND jw.parent="{filters.get('site_name')}"
        """)
        for row in emp:
            emp_list.append(row[0])
        emp_filters["name"] = ["in", emp_list]

    elif filters.get("type"):
        if filters.get("type")=="Pavers":
            emp_filters["paver"] = 1
        else:
            emp_filters["compound_wall"] = 1

    rem = frappe.get_all("Employee", emp_filters, pluck='name')
    return [[emp]+ [None for i in range(11)] for emp in rem if (
        get_undeducted_advances(emp, filters.get("from_date"), filters.get("to_date")) or
        get_employee_salary_balance(emp, filters.get("from_date"), filters.get("to_date")) or
        get_employee_salary_slip_amount(emp, filters.get("from_date"), filters.get("to_date"))
    )]
