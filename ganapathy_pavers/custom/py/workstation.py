from ast import operator
import frappe


             
def total_salary(doc,action):
    if doc.ts_operator_table:
        total =0
        for i in doc.ts_operator_table:
            total+=i.ts_operator_wages
        doc.ts_sum_of_operator_wages = total
        doc.ts_no_of_operator =  len(doc.ts_operator_table)
        

            
    doc.no_of_total_employees = (doc.no_of_labours or 0) + (doc.ts_no_of_operator or 0)
    doc.sum_of_wages_per_hours = (doc.cal_wages1 or 0) + (doc.ts_sum_of_operator_wages)
        
@frappe.whitelist()
def operator_salary(operator):
    salary = sum(frappe.get_all("Salary Structure Assignment", filters={'employee':operator}, pluck='base')) / 26
    return salary


