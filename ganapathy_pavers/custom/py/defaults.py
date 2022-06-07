import frappe

@frappe.whitelist()
def create_designation():
    if(not frappe.db.exists('Designation', 'Job Worker')):
        doc=frappe.new_doc('Designation')
        doc.update({
            'doctype': 'Designation',
            'designation_name': 'Job Worker'
        })
        doc.save()
        frappe.db.commit
    
    if(not frappe.db.exists('Designation', 'Operator')):
        doc=frappe.new_doc('Designation')
        doc.update({
            'doctype': 'Designation',
            'designation_name': 'Operator'
        })
        doc.save()
        frappe.db.commit
    
    if(not frappe.db.exists('Designation', 'Supervisor')):
        doc=frappe.new_doc('Designation')
        doc.update({
            'doctype': 'Designation',
            'designation_name': 'Supervisor'
        })
        doc.save()
        frappe.db.commit()
        
    doc=frappe.new_doc('Property Setter')
    doc.update({
        "doctype_or_field": "DocField",
        "doc_type":"Project",
        "field_name":"status",
        "property":"options",
        "value":"\nOpen\nCompleted\nCancelled\nStock Pending at Site"
    })
    doc.save()
    frappe.db.commit()
