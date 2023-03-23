import copy
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.model.utils.rename_field import rename_field
         
def total_no_salary(doc,action):
    if doc.ts_operators_table:
        total =0
        for i in doc.ts_operators_table:
            total+=i.ts_operator_wages
        doc.ts_sum_of_operator_wages = total
        doc.ts_no_of_operator =  len(doc.ts_operators_table)
        
    doc.no_of_total_employees = (doc.no_of_labours or 0) + (doc.ts_no_of_operator or 0)
    doc.sum_of_wages_per_hours = (doc.cal_wages1 or 0) + (doc.ts_sum_of_operator_wages or 0)
        
@frappe.whitelist()
def operator_salary(operator):
    salary = sum(frappe.get_all("Salary Structure Assignment", filters={'employee':operator, 'docstatus': 1}, pluck='base')) / 26
    return salary

def make_custom_field(self, event=None):
    if self.used_in_expense_splitup:
        for doctype in ["Journal Entry Account", "GL Entry"]:
            custom_fields={
                doctype: [
                        dict(
                            fieldname=frappe.scrub(self.name),
                            label=f"{self.name}",
                            fieldtype="Check",
                            insert_after="workstation",
                            depends_on="""eval:doc.expense_type=="Manufacturing" """,
                        ),]
                }
            create_custom_fields(custom_fields)
    else:
        remove_custom_field(self)

def rename_custom_field(self, event, oldname, newname, merge):
    if oldname == newname:
        return
    make_custom_field(self)
    for doctype in ["Journal Entry Account", "GL Entry"]:
        rename_field(doctype, frappe.scrub(oldname), frappe.scrub(newname))
    
    _self = copy.deepcopy(self)
    _self.name = oldname
    remove_custom_field(_self, event)

def remove_custom_field(self, event=None):
    #check field exists
    if not [row for row in frappe.get_meta("GL Entry").fields if row.fieldname==frappe.scrub(self.name)]:
        for i in frappe.get_all("Custom Field", {"dt": ["in", ["Journal Entry Account", "GL Entry"]],"fieldname": frappe.scrub(self.name)}, pluck = "name"):
            frappe.delete_doc("Custom Field", i)
        return 
    
    #if field exists
    gl_links = frappe.get_all("GL Entry", filters = {frappe.scrub(self.name): 1}, fields = ["voucher_type", "voucher_no"], group_by="voucher_no, voucher_type")

    if gl_links and not event == "after_rename":
        messgae = "This document is used in Expense entries <ul>"
        for i in gl_links:
            messgae += f"<li><a href='/app/{i.voucher_type}/{i.voucher_no}'>{i.voucher_no}</a></li>"
        
        messgae += "</ul>"

        frappe.throw(messgae)
    
    for i in frappe.get_all("Custom Field", {"dt": ["in", ["Journal Entry Account", "GL Entry"]],"fieldname": frappe.scrub(self.name)}, pluck = "name"):
        frappe.delete_doc("Custom Field", i)
    

