import frappe

def validate_dsm_uom(doc, event=None):
    throw=True
    if doc.dsm_uom:
        for row in doc.uoms:
            if row.uom == doc.dsm_uom:
                throw=False
                return
        if throw:
            frappe.throw(f"""Please Enter UOM Conversion for <b>{doc.dsm_uom}</b> in Item <a href="/app/item/{doc.name}"><b>{doc.name}</b></a>""")