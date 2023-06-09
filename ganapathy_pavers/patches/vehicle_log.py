import frappe

def execute():
    for i in frappe.get_all("Vehicle", ["name", "operator"]):
        if i.operator:
            opr=frappe.db.get_value("Driver", i.operator, "employee")
            frappe.db.set_value("Vehicle", i.name, "operator_employee", opr, update_modified=False)
            for j in frappe.get_all("Vehicle Log", {"license_plate": i.name, "operator": ["is", "not set"]}):
                frappe.db.set_value("Vehicle Log", j.name, "operator", opr, update_modified=False)


# ganapathy_pavers.patches.vehicle_log.vl_to_dn_created

def vl_to_dn_created():
    vl=frappe.get_all("Vehicle Log", {"docstatus": 1, "select_purpose": "Goods Supply", "delivery_note": ["is", "set"]}, pluck="delivery_note", group_by="delivery_note")
    for i in vl:
        frappe.db.set_value("Delivery Note", i, "vehicle_log_created", 1, update_modified=False)
    print(len(vl))
