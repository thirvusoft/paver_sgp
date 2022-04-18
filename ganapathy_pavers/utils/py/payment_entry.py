import frappe
def create_additional_salary(doc,action):
    for i in doc.references:
        if(i.reference_doctype=='Employee Advance'):
            advance_doc=frappe.get_doc('Employee Advance',i.reference_name)
            if advance_doc.repay_unclaimed_amount_from_salary == 1:
                add_doc=frappe.new_doc('Additional Salary')
                add_doc.employee = doc.party
                add_doc.salary_component = 'Additional Salary'
                add_doc.payroll_date=doc.posting_date
                add_doc.amount=i.allocated_amount
                add_doc.ref_doctype='Employee Advance'
                add_doc.ref_docname=i.reference_name
                add_doc.insert()
                add_doc.submit()
                frappe.db.commit()