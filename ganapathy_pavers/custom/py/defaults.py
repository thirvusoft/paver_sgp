import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

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
        "value":"\nOpen\nCompleted\nTo Bill\nBilled\nCancelled\nStock Pending at Site\nRework"
    })
    doc.save()
    frappe.db.commit()


def create_asset_category():
    if(not frappe.db.exists('Asset Category', 'Mould')):
        doc=frappe.get_doc({
            'doctype': 'Asset Category',
            'asset_category_name': 'Mould'
            })
        doc.flags.ignore_mandatory=True
        doc.save()

def create_role():
    if(not frappe.db.exists('Role', 'Admin')):
        doc=frappe.get_doc({
            'doctype': 'Role',
            'role_name': 'Admin'
        })
        doc.flags.ignore_mandatory=True
        doc.save()

def selling_settings():
    custom_fields = {
        'Selling Settings': [
            {
                "fieldname": "col_break_sgp_4567",
                "fieldtype": "Column Break",
                "insert_after" : "hide_tax_id"
            },
            {
                "fieldname": "sw_sales_invoice",
                "fieldtype": "Check",
                "label": "Site Work Mandatory in Sales Invoice",
                "insert_after" : "col_break_sgp_4567"
            },
        ]
    }
    create_custom_fields(custom_fields)
