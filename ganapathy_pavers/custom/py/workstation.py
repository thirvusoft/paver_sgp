import frappe

def validate(doc, action):
    employees=[i.ts_labour for i in doc.ts_labor]
    wages=0
    no_salary=[]
    for emp in employees:
        sal_struct = frappe.get_value("Salary Structure Assignment",{'employee':emp},"salary_structure")
        if(sal_struct):
            wages += frappe.get_value("Salary Structure", sal_struct,'hour_rate')
        else:no_salary.append(emp)
    if(len(no_salary)):
        frappe.throw("Salary Structure Assignment not found for employees "+frappe.bold(", ".join(list(set(no_salary)))))
