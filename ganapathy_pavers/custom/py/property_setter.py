import frappe

def property_setter():
    doc=frappe.new_doc("Property Setter")
    doc.update({
        'doctype_or_field' : 'DocField',
        'doc_type' : 'Lead',
        'field_name' : 'type',
        'property': 'options',
        'property_type' : 'Select',
        'value' : '\nCompound Wall\nPavers\nU Drain'
        
    })
    doc.save()
    doc.insert(ignore_permissions=True)
    
    
    doc2=frappe.new_doc("Property Setter")
    doc2.update({
        'doctype_or_field' : 'DocField',
        'doc_type' : 'Purchase Order',
        'field_name' : 'naming_series',
        'property': 'options',
        'property_type' : 'Data',
        'value' : 'PO-.MM.-.YY.-'
        
    })
    doc2.save()
    doc2.insert(ignore_permissions=True)
    

