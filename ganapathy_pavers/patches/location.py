import frappe
def execute():
    if(not frappe.db.exists('Location', 'Unit1')):
        doc = frappe.new_doc('Location')
        doc.update({
            'location_name': 'Unit1'
        })
        doc.flags.ignore_mandatory = True
        doc.save()