import frappe

def paver_production():
    for i in frappe.get_all("Material Manufacturing", pluck="name"):
        d = frappe.get_doc("Material Manufacturing", i)
        d.db_set_total_production_sqft()

# ganapathy_pavers.patches.paver_manufacturing.paver_production