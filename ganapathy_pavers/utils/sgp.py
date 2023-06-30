import frappe

primesite="prime" #"sgpprime.thirvusoft.co.in"
mainsite = "tsgp" #"sgp.thirvusoft.co.in"

doctypes = {
    "Sales Invoice": ["posting_date", "due_date"],
    "Purchase Invoice": ["posting_date"],
    "Journal Entry": ["posting_date"]
}
def posting_date():
    docnames, data = {}, {}
    # docs = {}
    with frappe.init_site(primesite):
        frappe.connect(site=primesite)
        for doctype in doctypes:
            print(doctype)
            docnames[doctype] = frappe.get_all(doctype, pluck="name")
            # docs[doctype] = {}
            # for i in frappe.get_all(doctype, fields=doctypes[doctype]+["name"]):
            #     docs[doctype][i.name] = i
    
    with frappe.init_site(mainsite):
        frappe.connect(site=mainsite)
        for doctype in docnames:
            data[doctype] = frappe.get_all(doctype, filters={"name": ["in", docnames[doctype]]}, fields=doctypes[doctype] + ["name"])
    
    frappe.init_site(primesite)
    frappe.connect(site=primesite)
    # diff = []
    for doctype in data:
        for row in data[doctype]:
            for field in row:
                if field == 'name':
                    continue
                    
                # if (row[field] != docs[doctype][row.name][field]):
                #     print(row.name, field, row[field], docs[doctype][row.name][field])
                
                # continue
                frappe.db.set_value(doctype, row.name, field, row[field], update_modified=False)
                gl = frappe.get_all("GL Entry", filters={
                        "voucher_type": doctype,
                        "voucher_no": row.name,
                        field: ["is", "set"]
                    }, pluck="name")
                for g in gl:
                    frappe.db.set_value("GL Entry", g, field, row[field], update_modified=False)
                
    # print(*diff, end='\n')  
