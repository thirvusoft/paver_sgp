import frappe

def execute():
    doc=frappe.get_single("Item Variant Settings")
    doc.update({
        "fields": doc.fields+[{"field_name": "dsm_uom"}]
    })
    doc.save()
