import frappe

primesite="tsgp" #"sgpprime.thirvusoft.co.in"
mainsite = "prime" #"sgp.thirvusoft.co.in"

doctypes = {
    "Sales Invoice": ["posting_date", "due_date"],
    "Purchase Invoice": ["posting_date"],
    "Journal Entry": ["posting_date"]
}
def posting_date():
    docnames, data = {}, {}
    maindocs = {}

    with frappe.init_site(mainsite):
        frappe.connect(site=mainsite)
        for doctype in doctypes:
            maindocs[doctype] = frappe.get_all(doctype, filters={
                "posting_date": [">=", "2023-04-01"], 
                "branch": "SG 1", 
                "docstatus": 1
                }, pluck="name")
            print(doctype, '   :::::::   ', len(maindocs[doctype]))

    with frappe.init_site(primesite):
        frappe.connect(site=primesite)
        for doctype in doctypes:
            print(doctype)
            print(len(frappe.get_all(doctype, filters={
                "name": ["not in", maindocs[doctype]], 
                "posting_date": [">=", "2023-04-01"], 
                "branch": "SG 1", 
                "docstatus": 1
            }, pluck="name")))
    
    return

    with frappe.init_site(mainsite):
        frappe.connect(site=mainsite)
        for doctype in docnames:
            data[doctype] = frappe.get_all(doctype, filters={"name": ["in", docnames[doctype]]}, fields=doctypes[doctype] + ["name"])
    
    frappe.init_site(primesite)
    frappe.connect(site=primesite)
    for doctype in data:
        for row in data[doctype]:
            for field in row:
                if field == 'name':
                    continue
                    
                frappe.db.set_value(doctype, row.name, field, row[field], update_modified=False)
                gl = frappe.get_all("GL Entry", filters={
                        "voucher_type": doctype,
                        "voucher_no": row.name,
                        field: ["is", "set"]
                    }, pluck="name")
                for g in gl:
                    frappe.db.set_value("GL Entry", g, field, row[field], update_modified=False)
                
