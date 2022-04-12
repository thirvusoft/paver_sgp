import frappe

@frappe.whitelist()
def create_designation():
    doc=frappe.new_doc('Designation')
    doc.update({
        'doctype': 'Designation',
        'designation_name': 'Job Worker'
    })
    doc.save()
    doc=frappe.new_doc('Designation')
    doc.update({
        'doctype': 'Designation',
        'designation_name': 'Supervisor'
    })
    doc.save()
    frappe.db.commit()