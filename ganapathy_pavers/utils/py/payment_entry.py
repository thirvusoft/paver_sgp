import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
def create_additional_salary(doc,action):
    for i in doc.references:
        if(i.reference_doctype=='Employee Advance'):
            advance_doc=frappe.get_doc('Employee Advance',i.reference_name)
            if advance_doc.repay_unclaimed_amount_from_salary == 1:
                add_doc=frappe.new_doc('Additional Salary')
                add_doc.employee = doc.party
                add_doc.salary_component = 'Advance Amount'
                add_doc.payroll_date=doc.posting_date
                add_doc.amount=i.allocated_amount
                add_doc.ref_doctype='Employee Advance'
                add_doc.ref_docname=i.reference_name
                add_doc.insert()
                add_doc.submit()
        
def payment_entry_property_setter():                
    make_property_setter("Payment Entry", "branch", "reqd",1, "Check")
    make_property_setter("Payment Entry", "mode_of_payment", "reqd",1, "Check")
    make_property_setter("Payment Entry", "type", "reqd",1, "Check")

def site_to_project(doc, event=None):
    doc.project = doc.site_work