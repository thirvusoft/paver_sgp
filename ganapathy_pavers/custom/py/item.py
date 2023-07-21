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

def update_paver_type_in_prod(self, event=None):
    if self.item_group == 'Pavers':
        mm = frappe.get_all("Material Manufacturing", filters = {'item_to_manufacture': self.name, 'paver_type': ['!=', self.paver_type]}, pluck='name')
        for prod in mm:
            frappe.db.set_value("Material Manufacturing", prod, 'paver_type', self.paver_type, update_modified=False)
