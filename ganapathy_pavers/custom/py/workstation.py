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
    if doc.cost_per_hours != 0:
        if (doc.division_factors1 and doc.division_factors2 and doc.division_factors3 )== 0:
            frappe.throw("Zero is not allowed kindly give above zero in division factors")
        else:
            doc.cal_wages1 = (doc.cost_per_hours * doc.no_of_labours) / doc.division_factors1
            doc.cal_wages2 = (doc.cost_per_hours * doc.no_of_operators) / doc.division_factors2
            doc.cal_wages3 = (doc.cost_per_hours * doc.no_of_common_operators) / doc.division_factors3
            doc.no_of_total_employees = doc.no_of_labours + doc.no_of_operators + doc.no_of_common_operators
            doc.sum_of_wages_per_hours = doc.cal_wages1 + doc.cal_wages2 + doc.cal_wages3

