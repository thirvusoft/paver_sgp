from ast import operator
import frappe

def validate(doc, action):
    # employees=[i.ts_labour for i in doc.ts_labor]
    # wages=0
    # no_salary=[]
    # for emp in employees:
    #     sal_struct = frappe.get_value("Salary Structure Assignment",{'employee':emp},"salary_structure")
    #     if(sal_struct):
    #         wages += frappe.get_value("Salary Structure", sal_struct,'hour_rate')
    #     else:no_salary.append(emp)
    # if(len(no_salary)):
    #     frappe.throw("Salary Structure Assignment not found for employees "+frappe.bold(", ".join(list(set(no_salary)))))
    emp = frappe.get_all("Employee",filters={"designation":'Operator'}, pluck='name')
    salary = sum(frappe.get_all("Salary Structure Assignment", filters={'employee':['in',emp]}, pluck='base')) / 26
    if doc.cost_per_hours != 0:
        if doc.no_of_labours !=0:
            if doc.division_factors1 == 0:
                frappe.throw("Zero is not allowed kindly give above zero in division factors")
            else:
                doc.cal_wages1 = ((doc.cost_per_hours or 0 )* (doc.no_of_labours or 0)) / (doc.division_factors1 or 1)
            
        else:
             doc.cal_wages1 = 0
             doc.division_factors1 = 0
    if doc.no_of_operators !=0:
        if doc.division_factors2 == 0:
            frappe.throw("Zero is not allowed kindly give above zero in division factors")
        else:
            doc.cal_wages2 = ((salary or 0)/doc.division_factors2 or 0)*doc.no_of_operators
            
    else:
        doc.cal_wages2 = 0
        doc.division_factors2 = 0
    if doc.no_of_common_operators !=0:
        if doc.division_factors3 == 0:
            frappe.throw("Zero is not allowed kindly give above zero in division factors")
        else:
            doc.cal_wages3 = ((salary or 0)/doc.division_factors3 or 0)*doc.no_of_common_operators    
    else:
        doc.cal_wages3 = 0
        doc.division_factors3 = 0
    if doc.routine_operators !=0:
        if doc.division_factors4 == 0:
            frappe.throw("Zero is not allowed kindly give above zero in division factors")
        else:
            doc.cal_wages4 = ((salary or 0)/doc.division_factors4 or 0)*doc.routine_operators
            
    else:
        doc.cal_wages4 = 0
        doc.division_factors4 = 0
            
        doc.no_of_total_employees = (doc.no_of_labours or 0) + (doc.no_of_operators or 0) + (doc.no_of_common_operators or 0) + (doc.routine_operators or 0)
        doc.sum_of_wages_per_hours = (doc.cal_wages1 or 0) + (doc.cal_wages2 or 0) + (doc.cal_wages3 or 0) + (doc.cal_wages4 or 0)
        
        # if (doc.no_of_operators and doc.no_of_common_operators and doc.routine_operators) != 0:
        #     if (doc.division_factors1 and doc.division_factors2 and doc.division_factors3 and doc.division_factors4)== 0:
                
        #         frappe.throw("Zero is not allowed kindly give above zero in division factors")
        #     else:
        #         doc.cal_wages1 = ((doc.cost_per_hours or 0 )* (doc.no_of_labours or 0)) / (doc.division_factors1 or 1)
        #         emp = frappe.get_all("Employee",filters={"designation":'Operator'}, pluck='name')
        #         salary = sum(frappe.get_all("Salary Structure Assignment", filters={'employee':['in',emp]}, pluck='base')) / 26
        #         doc.cal_wages2 = ((salary or 0)/doc.division_factors2 or 0)*doc.no_of_operators 
        #         doc.cal_wages3 = ((salary or 0)/doc.division_factors3 or 0)*doc.no_of_common_operators
        #         doc.cal_wages4 = ((salary or 0)/doc.division_factors4 or 0)*doc.routine_operators
        #         doc.no_of_total_employees = (doc.no_of_labours or 0) + (doc.no_of_operators or 0) + (doc.no_of_common_operators or 0) + (doc.routine_operators or 0)
        #         doc.sum_of_wages_per_hours = (doc.cal_wages1 or 0) + (doc.cal_wages2 or 0) + (doc.cal_wages3 or 0) + (doc.cal_wages4 or 0)
        