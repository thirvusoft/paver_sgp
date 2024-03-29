import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def property_setter():
    make_property_setter('Sales Invoice', 'project', 'allow_on_submit', 1, 'Check')
    make_property_setter('Payment Entry', 'project', 'allow_on_submit', 1, 'Check')
    make_property_setter('Lead', 'type', 'options', 'Types', 'Small Text')
    make_property_setter('Lead', 'type', 'fieldtype', 'Link', 'Select')
    
    
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
    

