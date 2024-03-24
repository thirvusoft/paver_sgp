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
            {
                "fieldname": "sales_order_required",
                "fieldtype": "Select",
                "label": "Is Sales Order Required for Delivery Note Creation?",
                "insert_after" : "so_required",
                "options" : "No\nYes"
            },
        ]
    }
    create_custom_fields(custom_fields)

def create_types():
    from frappe.model.delete_doc import delete_doc
    __types = frappe.db.get_all("Paver Type", pluck="name") + frappe.db.get_all("Compound Wall Type", pluck="name")
    types = ['Internal', 'Others', 'Site', 'Vehicle']

    name = {'Paver': 'Pavers'}

    for i in __types:
        types.append((name.get(i) or i))
    
    for _type in types:
        if not frappe.db.exists("Types", _type):
            d = frappe.new_doc("Types")
            d.update({
                "type": _type
            })
            d.save()
    
    _types = frappe.db.get_all("Types", pluck="name")
    not_deletable = []
    deleted = []

    for _type in _types:
        if _type not in types:
            try:
                delete_doc("Types", _type, ignore_permissions=True)
                deleted.append(_type)
            except:
                not_deletable.append(_type)

    if deleted:
        print("Deleted unused type", ", ".join(deleted))

    if not_deletable:
        print("Types to be deleted manually", ", ".join(not_deletable))

def print_settings():
    custom_fields = {
        'Print Settings': [
            {
                "label": "Delivery Slip - Show Bundle UOM",
                "fieldname": "print_as_bundle",
                "fieldtype": "Check",
                "default": "1",
                "insert_after" : "print_taxes_with_zero_amount"
            },
        ]
    }
    create_custom_fields(custom_fields)
