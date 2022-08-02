from ast import operator
import frappe

def validate(doc, action):
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
    if doc.no_of_operators !=0:
        if doc.division_factors2 == 0:
            frappe.throw("Zero is not allowed kindly give above zero in division factors")
        else:
            doc.cal_wages2 = ((salary or 0)/doc.division_factors2)*doc.no_of_operators
            
    else:
        doc.cal_wages2 = 0
        doc.division_factors2 = 0
    if doc.no_of_common_operators !=0:
        if doc.division_factors3 == 0:
            frappe.throw("Zero is not allowed kindly give above zero in division factors")
        else:
            doc.cal_wages3 = ((salary or 0)/doc.division_factors3)*doc.no_of_common_operators    
    else:
        doc.cal_wages3 = 0
        doc.division_factors3 = 0
    if doc.routine_operators !=0:
        if doc.division_factors4 == 0:
            frappe.throw("Zero is not allowed kindly give above zero in division factors")
        else:
            doc.cal_wages4 = ((salary or 0)/doc.division_factors4)*doc.routine_operators
            
    else:
        doc.cal_wages4 = 0
            
    doc.no_of_total_employees = (doc.no_of_labours or 0) + (doc.no_of_operators or 0) + (doc.no_of_common_operators or 0) + (doc.routine_operators or 0)
    doc.sum_of_wages_per_hours = (doc.cal_wages1 or 0) + (doc.cal_wages2 or 0) + (doc.cal_wages3 or 0) + (doc.cal_wages4 or 0)
        
     