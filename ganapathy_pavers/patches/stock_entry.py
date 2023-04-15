import frappe
# ganapathy_pavers.patches.stock_entry.execute


def execute():
    adblue()
    fuel()

def fuel():
    fuel = frappe.get_all("Stock Entry", filters = [
        ["Stock Entry Detail", "s_warehouse", "=", "Barrel - GP"],
        ["vehicle_log", "is", "set"]
    ],
    fields=["name", "vehicle_log"])

    for se in fuel:
        vl=frappe.get_doc("Vehicle Log", se.vehicle_log)
        for i in frappe.get_all("Stock Entry Detail", {"parent": se.name}, pluck="name"):
            frappe.db.set_value("Stock Entry Detail", i, "expense_account", "Fuel - GP", update_modified=False)

            frappe.db.set_value("Stock Entry Detail", i, "expense_type", vl.expense_type, update_modified=False)

            frappe.db.set_value("Stock Entry Detail", i, "paver", vl.paver, update_modified=False)
            frappe.db.set_value("Stock Entry Detail", i, "is_shot_blast", vl.is_shot_blast, update_modified=False)
            frappe.db.set_value("Stock Entry Detail", i, "compound_wall", vl.compound_wall, update_modified=False)
            frappe.db.set_value("Stock Entry Detail", i, "fencing_post", vl.fencing_post, update_modified=False)
            frappe.db.set_value("Stock Entry Detail", i, "lego_block", vl.lego_block, update_modified=False)

            frappe.db.set_value("Stock Entry Detail", i, "machine1", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine1"]), update_modified=False)
            frappe.db.set_value("Stock Entry Detail", i, "machine2", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine2"]), update_modified=False)
            frappe.db.set_value("Stock Entry Detail", i, "machine3_night", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine3_night"]), update_modified=False)
            frappe.db.set_value("Stock Entry Detail", i, "machine3_day", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine3_day"]), update_modified=False)

        for i in frappe.get_all("GL Entry", {"voucher_type": "Stock Entry", "voucher_no": se.name}, pluck="name"):
            if frappe.get_value("GL Entry", i, "account")=="Cost of Goods Sold - GP":
                frappe.db.set_value("GL Entry", i, "account", "Fuel - GP", update_modified=False)
            else:
                frappe.db.set_value("GL Entry", i, "against", "Fuel - GP", update_modified=False)

            frappe.db.set_value("GL Entry", i, "expense_type", vl.expense_type, update_modified=False)

            frappe.db.set_value("GL Entry", i, "paver", vl.paver, update_modified=False)
            frappe.db.set_value("GL Entry", i, "is_shot_blast", vl.is_shot_blast, update_modified=False)
            frappe.db.set_value("GL Entry", i, "compound_wall", vl.compound_wall, update_modified=False)
            frappe.db.set_value("GL Entry", i, "fencing_post", vl.fencing_post, update_modified=False)
            frappe.db.set_value("GL Entry", i, "lego_block", vl.lego_block, update_modified=False)

            frappe.db.set_value("GL Entry", i, "machine1", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine1"]), update_modified=False)
            frappe.db.set_value("GL Entry", i, "machine2", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine2"]), update_modified=False)
            frappe.db.set_value("GL Entry", i, "machine3_night", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine3_night"]), update_modified=False)
            frappe.db.set_value("GL Entry", i, "machine3_day", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine3_day"]), update_modified=False)

def adblue():
    _adblue = frappe.get_all("Stock Entry", filters = [
        ["Stock Entry Detail", "s_warehouse", "=", "Adblue - GP"],
        ["vehicle_log", "is", "set"]
    ],
    fields=["name", "vehicle_log"])

    for se in _adblue:
        vl=frappe.get_doc("Vehicle Log", se.vehicle_log)
        for i in frappe.get_all("Stock Entry Detail", {"parent": se.name}, pluck="name"):
            frappe.db.set_value("Stock Entry Detail", i, "expense_account", "ADBLUE - GP", update_modified=False)

            frappe.db.set_value("Stock Entry Detail", i, "expense_type", vl.expense_type, update_modified=False)

            frappe.db.set_value("Stock Entry Detail", i, "paver", vl.paver, update_modified=False)
            frappe.db.set_value("Stock Entry Detail", i, "is_shot_blast", vl.is_shot_blast, update_modified=False)
            frappe.db.set_value("Stock Entry Detail", i, "compound_wall", vl.compound_wall, update_modified=False)
            frappe.db.set_value("Stock Entry Detail", i, "fencing_post", vl.fencing_post, update_modified=False)
            frappe.db.set_value("Stock Entry Detail", i, "lego_block", vl.lego_block, update_modified=False)

            frappe.db.set_value("Stock Entry Detail", i, "machine1", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine1"]), update_modified=False)
            frappe.db.set_value("Stock Entry Detail", i, "machine2", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine2"]), update_modified=False)
            frappe.db.set_value("Stock Entry Detail", i, "machine3_night", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine3_night"]), update_modified=False)
            frappe.db.set_value("Stock Entry Detail", i, "machine3_day", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine3_day"]), update_modified=False)

        for i in frappe.get_all("GL Entry", {"voucher_type": "Stock Entry", "voucher_no": se.name}, pluck="name"):
            if frappe.get_value("GL Entry", i, "account")=="Cost of Goods Sold - GP":
                frappe.db.set_value("GL Entry", i, "account", "ADBLUE - GP", update_modified=False)
            else:
                frappe.db.set_value("GL Entry", i, "against", "ADBLUE - GP", update_modified=False)
            
            frappe.db.set_value("GL Entry", i, "expense_type", vl.expense_type, update_modified=False)

            frappe.db.set_value("GL Entry", i, "paver", vl.paver, update_modified=False)
            frappe.db.set_value("GL Entry", i, "is_shot_blast", vl.is_shot_blast, update_modified=False)
            frappe.db.set_value("GL Entry", i, "compound_wall", vl.compound_wall, update_modified=False)
            frappe.db.set_value("GL Entry", i, "fencing_post", vl.fencing_post, update_modified=False)
            frappe.db.set_value("GL Entry", i, "lego_block", vl.lego_block, update_modified=False)

            frappe.db.set_value("GL Entry", i, "machine1", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine1"]), update_modified=False)
            frappe.db.set_value("GL Entry", i, "machine2", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine2"]), update_modified=False)
            frappe.db.set_value("GL Entry", i, "machine3_night", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine3_night"]), update_modified=False)
            frappe.db.set_value("GL Entry", i, "machine3_day", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine3_day"]), update_modified=False)
