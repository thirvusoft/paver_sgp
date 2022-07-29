import frappe

def create_multi_customer():
    if(not frappe.db.exists('Customer', 'MultiCustomer')):
        doc=frappe.new_doc('Customer')
        doc.update({
            'customer_name': 'MultiCustomer',
            'customer_type': 'Company',
            'customer_group': 'All Customer Groups',
            'territory': 'India'
        })
        doc.flags.ignore_mandatory=True
        doc.flags.ignore_permissions=True
        doc.save()