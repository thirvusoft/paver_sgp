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
            conditions += f""" and "{site_type}" in (select _t.type from `tabEmployee Production Type` _t where _t.parent=emp.name and _t.parenttype='Employee' and _t.parentfield='production') """
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
                                    {2} order by jwd.idx, jwd.sqft_allocated)as total_cal
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
                                    group by jwd.name1{2},jwd.sqft_allocated, jwd.start_date, jwd.end_date, jwd.description_for_other_work, jwd.rate order by jwd.idx, jwd.sqft_allocated)as total_cal
                                """.format(conditions+" and jwd.other_work = 1",adv_conditions, "", "sum(jwd.completed_bundle), sum(jwd.sqft_allocated), avg(jwd.rate)" if filters.get("group_site_work") else "jwd.completed_bundle, jwd.sqft_allocated, jwd.rate", "sum(jwd.amount)" if filters.get("group_site_work") else "jwd.amount"))
    data = [list(i) for i in (report_data or tuple())]
    final_data = []
    c = 0
    if filters.get("group_site_work"):
        data1={}
        count={}
        for idx in range(len(data)):
            _key=f"{data[idx][0]}---{data[idx][1]}-------{data[idx][5]}"
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
            emp_sal=get_employee_salary_balance(employee=row[0], from_date=from_date, to_date=to_date)
            row[8]=emp_sal.get("amount")
    data.sort(key = lambda x:(x[0] or ""))
    
    _data = []
    for idx in range(len(data)):
        _data.append(data[idx])
        if idx+1 == len(data) or data[idx+1][0] != data[idx][0]:
            credit = frappe.db.sql(f"""
                select
                    jea.party,
                    sum(jea.credit) as amount,
                    je.salary_component as component,
                    GROUP_CONCAT(CONCAT(je.name, '', round(jea.credit, 2), ' ', ifnull(je.user_remark, '')) SEPARATOR '\n') as remarks
                from `tabJournal Entry Account` jea
                inner join `tabJournal Entry` je 
                on jea.parenttype="Journal Entry" and jea.parent=je.name
                where
                    ifnull((
                        select count(ssc.name)
                        from `tabSite work Details` ssc
                        where 
                            ssc.parenttype="Salary Slip" and
                            ssc.docstatus=1 and
                            ssc.journal_entry = je.name
                    ), 0)=0 and 
                    je.docstatus=1 and
                    je.voucher_type="Credit Note" and
                    je.posting_date <= '{to_date}' and
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
                    data[idx][8],
                    credit[0].amount,
                    '',
                    '',
                    '',
                    '',
                    credit[0].remarks
                ])
    data = _data

    emp_data = []
    if(len(data)):
        start = 0
        for i in range(len(data)-1):
            if (data[i][0] != data[i+1][0]):
                adv=get_employee_salary_slip_advance_deduction(data[i][0], from_date, to_date, data[i][10])
                remarks=adv.get("remarks")
                adv=adv.get("amount")
                data[i][10]=None
                data[i][11]=None
                credit_remark=data[i][14] if len(data[i]) >= 15 else ''
                if len(data[i]) >= 15:
                    data[i][14]=None
                employee_id=data[i][0]
                data[i][0]=frappe.db.get_value("Employee", data[i][0], "employee_name")
                emp_data.append(data[i]+[None, None, None])
                total = [" " for i in range(15)]
                total[0] = data[i][0]
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
                total[13]=remarks
                total[14] = credit_remark
                
                emp_data[-1][8]=None
                final_data.append([total[0], '', 'DETAILS']+[None]*12)
                final_data+=emp_data+[([None]+total[1:])]+[[None]*15]
                emp_data=[]
                start = i+1	
                c=0
            else:
                data[i][0]=frappe.db.get_value("Employee", data[i][0], "employee_name")
                data[i][8]=None
                data[i][11]=None
                if(c==0):data[i][10]=None
                else:data[i][10]=None
                c+=1
                emp_data.append(data[i]+[None, None, None])
        adv=get_employee_salary_slip_advance_deduction(data[-1][0], from_date, to_date, data[-1][10])
        remarks=adv.get("remarks")
        adv=adv.get("amount")
        data[-1][10]=None
        data[-1][11]=None
        credit_remark=data[-1][14] if len(data[-1]) == 15 else ''
        if len(data[-1]) >= 15:
                    data[-1][14]=None
        employee_id=data[-1][0]
        data[-1][0]=frappe.db.get_value("Employee", data[-1][0], "employee_name")
        emp_data.append(data[-1]+[None, None, None])
        total = [" " for i in range(15)]
        total[0] = data[-1][0]
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
        total[13]=remarks
        total[14] = credit_remark
        emp_data[-1][8]=None
        final_data.append([total[0], '', 'DETAILS']+[None]*12)
        final_data+=emp_data+[([None]+total[1:])]+[[None]*15]
        emp_data=[]
    other_work=0
    for row in final_data:
        if row[6]:
            row[6]="Yes"
            other_work=1
        else:
            row[6]=""
            row[7]=""
    columns = get_columns(other_work)
    data = add_total_row(final_data, index = 11)

    return columns, data

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
        },
        {
            "fieldname": "debit_remarks",
            "label": "Debit Remarks",
            "fieldtype": "Small Text",
            "default": None,
            "minWidth": 120,
            "hidden": 1,
            "ts_right_align": "text-right"
        },
        {
            "fieldname": "credit_remarks",
            "label": "Credit Remarks",
            "fieldtype": "Small Text",
            "default": None,
            "minWidth": 120,
            "hidden": 1,
            "ts_right_align": "text-right"
        }
		]
	
	return columns

def get_employee_salary_balance(employee, from_date, to_date):
    remarks = ""
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
    credit_conditions = f"""
    and je.posting_date < '{from_date}'
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

        credit_note_amount = frappe.db.sql(f"""
                select
                    sum(jea.credit) as amount,
                    GROUP_CONCAT(CONCAT(je.name, '', round(jea.credit, 2), ' ', ifnull(je.user_remark, '')) SEPARATOR '\n') as remarks
                from `tabJournal Entry Account` jea
                inner join `tabJournal Entry` je 
                on jea.parenttype="Journal Entry" and jea.parent=je.name
                where
                    ifnull((
                        select count(ssc.name)
                        from `tabSite work Details` ssc
                        where 
                            ssc.parenttype="Salary Slip" and
                            ssc.docstatus=1 and
                            ssc.journal_entry = je.name
                    ), 0)=0 and 
                    je.docstatus=1 and
                    je.voucher_type="Credit Note" and
                    jea.party_type='Employee' and
                    jea.party='{employee}' and
                    ifnull(je.salary_component, '')!=''
                    {credit_conditions}
            """, as_dict=True)
        if credit_note_amount and credit_note_amount[0] and credit_note_amount[0].get("amount"):
            amount = (amount or 0) + (credit_note_amount[0].get("amount") or 0)

    if salary_slip:
        return {"amount": salary_slip[0]["total_unpaid_amount"]+amount, "remarks": remarks}

    elif(salary_slip1):
        return {"amount": salary_slip1[0]["total_unpaid_amount"]+amount, "remarks": remarks}
    
    elif (not frappe.db.exists("Salary Slip", {"docstatus": 1, "employee": employee})):
        emp_sal_bal = frappe.db.get_value("Employee", employee, "salary_balance")
        return {"amount": emp_sal_bal+amount, "remarks": remarks}
    
    return {"amount": round((amount or 0), 2), "remarks": remarks}

def get_employee_salary_slip_amount(employee, from_date, to_date):
    query=f"""
        SELECT SUM(ss.paid_amount)
        FROM `tabSalary Slip` ss
        WHERE ss.docstatus=1 AND ss.employee='{employee}' AND ss.start_date >= '{from_date}' AND ss.end_date <= '{to_date}'
    """
    res=frappe.db.sql(query)[0][0]
    return round((res or 0), 2) or ""

def get_employee_salary_slip_advance_deduction(employee, from_date, to_date, adv=None):
    if frappe.db.get_all('Salary Slip', {'employee': employee, 'start_date': [">=", from_date], 'end_date': ["<=", to_date], "docstatus": 1}):
        query=f"""
            SELECT SUM(ss.total_deduction)
            FROM `tabSalary Slip` ss
            WHERE ss.docstatus=1 AND ss.employee='{employee}' AND ss.start_date >= '{from_date}' AND ss.end_date <= '{to_date}'
        """
        res=frappe.db.sql(query)[0][0]
        return {"amount": res}
    planned_deduction=0
    planned_deduction=(frappe.db.sql(f"""
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
    """)[0][0] or 0) + (get_undeducted_planned_advances(employee, from_date, to_date) or 0)
    debit_note = frappe.db.sql(f"""
                select
                    sum(jea.debit) as amount,
                    GROUP_CONCAT(CONCAT(je.name, '', round(jea.debit, 2), ' ', ifnull(je.user_remark, '')) SEPARATOR '\n') as remarks
                from `tabJournal Entry Account` jea
                inner join `tabJournal Entry` je 
                on jea.parenttype="Journal Entry" and jea.parent=je.name
                where
                    je.docstatus=1 and
                    je.voucher_type="Debit Note" and
                    je.posting_date <= '{to_date}' and
                    ifnull((
                        select count(ssc.name)
                        from `tabSalary Detail` ssc
                        where 
                            ssc.parenttype="Salary Slip" and
                            ssc.parentfield="deductions" and
                            ssc.docstatus=1 and
                            ssc.journal_entry = je.name
                    ), 0)=0 and 
                    jea.party_type='Employee' and
                    jea.party='{employee}' and
                    ifnull(je.salary_component, '')!=''
                order by je.posting_date, je.creation
            """, as_dict=True)
    debit = 0
    remarks = ""
    if debit_note and debit_note[0] and debit_note[0].get("amount"):
        debit = debit_note[0].get("amount")
        remarks = debit_note[0].get("remarks")

    return {"amount": round(((planned_deduction or 0) + (debit or 0)), 2) or 0, "remarks": remarks}

def get_undeducted_planned_advances(employee, from_date, to_date):
    res= frappe.db.sql(f"""
        SELECT
            ROUND(SUM(ded_pl.amount - IFNULL(
                (
                    SELECT
                        SUM(ssr.amount)
                    FROM `tabSalary Slip Reference` ssr
                    WHERE
                        ssr.parenttype = 'Additional Salary' AND
                        IFNULL((
                            SELECT
                                COUNT(*)
                            FROM `tabSalary Slip` sal_slip
                            WHERE
                                ded_pl.date BETWEEN sal_slip.start_date and sal_slip.end_date and
                                sal_slip.name = ssr.salary_slip
                        ), 0) > 0 AND
                        IFNULL((
                            SELECT
                                COUNT(*)
                            FROM `tabAdditional Salary` a_sal
                            WHERE
                                a_sal.name = ssr.parent and
                                a_sal.ref_doctype = 'Employee Advance' AND 
                                a_sal.ref_docname = ded_pl.parent
                        ), 0) > 0
                )
            , 0)), 2)
        FROM `tabDeduction Planning` ded_pl
        INNER JOIN `tabEmployee Advance` e_adv
        ON ded_pl.parent = e_adv.name AND ded_pl.parenttype = 'Employee Advance'
        WHERE
            ded_pl.date < '{from_date}' AND
            e_adv.employee = '{employee}' AND
            e_adv.docstatus = 1 AND
            e_adv.repay_unclaimed_amount_from_salary = 1
    """)[0][0]
    
    return round((res or 0), 2)

def get_employees_to_add(filters, employees):
    employees=list(set(employees))
    emp_filters = [
        ["status", "=", "Active"],
        ["name", "not in", employees],
        ["designation", '=', "Job Worker"]
    ]
    if filters.get("employee") and filters.get("employee") in employees:
        return []
    
    elif filters.get("employee"):
        emp_filters.append(["name", "=", filters.get("employee")])

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
        emp_filters.append(["name", "in", emp_list])

    elif filters.get("type"):
        emp_filters.append(["Employee Production Type", "type", "=", filters.get("type")])

    rem = frappe.get_all("Employee", emp_filters, pluck='name')
    return [[emp]+ [None for i in range(11)] for emp in rem if (
        get_undeducted_planned_advances(emp, filters.get("from_date"), filters.get("to_date")) or
        get_employee_salary_balance(emp, filters.get("from_date"), filters.get("to_date")).get("amount") or
        get_employee_salary_slip_amount(emp, filters.get("from_date"), filters.get("to_date")) or
        (get_employee_salary_slip_advance_deduction(emp, filters.get("from_date"), filters.get("to_date")) or {}).get("amount")
    )]
