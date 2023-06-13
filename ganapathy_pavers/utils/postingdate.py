import frappe


def posting_date():
    doctypes = {
        "Sales Invoice": ["posting_date", "due_date"],
        "Purchase Invoice": ["posting_date"],
        "journal_entry": ["posting_date"]
    }
    docnames, data = {}, {}
    with frappe.init_site("sgpprime.thirvusoft.co.in"):
        frappe.connect(site="sgpprime.thirvusoft.co.in")
        for doctype in doctypes:
            print(doctype)
            docnames[doctype] = frappe.get_all(doctype, pluck="name")
    
    with frappe.init_site("sgp.thirvusoft.co.in"):
        frappe.connect(site="sgp.thirvusoft.co.in")
        for doctype in docnames:
            data[doctype] = frappe.get_all(doctype, filters={"name": ["in", docnames[doctype]]}, fields=doctypes[doctype] + ["name"])
    print(data)
    frappe.init_site("sgpprime.thirvusoft.co.in")
    frappe.connect(site="sgpprime.thirvusoft.co.in")

    for doctype in data:
        for row in data[doctype]:
            for field in row:
                if field == 'name':
                    continue
                frappe.db.set_value(doctype, row.name, field, row[field], update_modified=False)
                print({
                        "voucher_type": doctype, 
                        "voucher_no": row["name"],
                        field: ["is", "set"]
                    })
                gl = frappe.get_all("GL Entry", filters={
                        "voucher_type": doctype, 
                        "voucher_no": row["name"],
                        field: ["is", "set"]
                    }, pluck="name")
                for g in gl:
                    frappe.db.set_value("GL Entry", g, field, row[field], update_modified=False)
                
                                    
