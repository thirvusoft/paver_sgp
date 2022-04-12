import frappe

@frappe.whitelist()
def create_designation(self, event):
    doc=frappe.new_doc('Designation')
    doc.update({
        'doctype': 'Designation',
        'designation_name': 'Job Worker'
    })
    doc.save()
    frappe.db.commit