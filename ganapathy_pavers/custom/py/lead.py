import frappe

def property_setter():
    doc=frappe.new_doc("Property Setter")
    doc.update({
        'doctype_or_field' : 'DocField',
        'doc_type' : 'Lead',
        'field_name' : 'type',
        'property': 'options',
        'property_type' : 'Select',
        'value' : 'Compound Wall\nPaver'
        
    })
    doc.save()
    doc.insert(ignore_permissions=True)