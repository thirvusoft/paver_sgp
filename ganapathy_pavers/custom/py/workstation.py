import frappe
@frappe.whitelist()
def hour_salary_finder(ts_employee):
    ts_employee_list=eval(ts_employee)
    ts_emp_wages_per_hour=0
    for ts_employee in ts_employee_list:
        ts_structure_name=frappe.get_all("Salary Structure Assignment",filters={"employee":ts_employee},fields={"salary_structure"})
        ts_structure_details=frappe.get_doc("Salary Structure",ts_structure_name[0]["salary_structure"])
        ts_emp_wages_per_hour=ts_emp_wages_per_hour+ts_structure_details.__dict__["hour_rate"]
    # ts_avg_wages_per_hour=ts_emp_wages_per_hour/len(ts_employee_list)
    # return ts_avg_wages_per_hour
    return ts_emp_wages_per_hour
    
