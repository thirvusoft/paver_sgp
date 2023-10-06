import frappe
# ganapathy_pavers.patches.stock_entry.execute


def execute():
    vehicle_fuel()


def vehicle_fuel():
    _adblue = frappe.get_all("Journal Entry", filters = [
        ["Journal Entry Account", "expense_type", "is", "not set"],
        ["vehicle_log", "is", "set"],
        ["posting_date", "between", ["2023-03-01", "2023-03-31"]]
    ],
    fields=["name", "vehicle_log"])
    vl=[]
    
    for se in _adblue:
        vl=frappe.get_doc("Vehicle Log", se.vehicle_log)
        for i in frappe.get_all("Journal Entry Account", {"parent": se.name}, pluck="name"):

            frappe.db.set_value("Journal Entry Account", i, "vehicle", vl.license_plate, update_modified=False)
            frappe.db.set_value("Journal Entry Account", i, "expense_type", vl.expense_type, update_modified=False)

            frappe.db.set_value("Journal Entry Account", i, "paver", vl.paver, update_modified=False)
            frappe.db.set_value("Journal Entry Account", i, "is_shot_blast", vl.is_shot_blast, update_modified=False)
            frappe.db.set_value("Journal Entry Account", i, "compound_wall", vl.compound_wall, update_modified=False)
            frappe.db.set_value("Journal Entry Account", i, "fencing_post", vl.fencing_post, update_modified=False)
            frappe.db.set_value("Journal Entry Account", i, "lego_block", vl.lego_block, update_modified=False)

            frappe.db.set_value("Journal Entry Account", i, "machine1", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine1"]), update_modified=False)
            frappe.db.set_value("Journal Entry Account", i, "machine2", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine2"]), update_modified=False)
            frappe.db.set_value("Journal Entry Account", i, "machine3_night", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine3_night"]), update_modified=False)
            frappe.db.set_value("Journal Entry Account", i, "machine3_day", sum([1 for wrk in vl.workstations if frappe.scrub(wrk.workstation)=="machine3_day"]), update_modified=False)

        for i in frappe.get_all("GL Entry", {"voucher_type": "Journal Entry", "voucher_no": se.name}, pluck="name"):
            
            frappe.db.set_value("GL Entry", i, "vehicle", vl.license_plate, update_modified=False)
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


def site_work_additional_cost():
    stock_entry = frappe.get_all("Stock Entry", {"internal_fuel_consumption":["is","set"],"site_work":["is","set"],"docstatus":1}, pluck="name")
    print(len(stock_entry))
    if stock_entry:
        for i in stock_entry:
            se_doc=frappe.get_doc("Stock Entry", i)
            if se_doc:
                sw_doc=frappe.get_doc("Project",se_doc.site_work)
                total_qty=0
                for j in se_doc.items:
                    total_qty += j.qty


                sw_doc.append("additional_cost", {
                    "description": se_doc.internal_fuel_consumption,
                    "qty": total_qty,
                    "nos":total_qty,
                    "amount": se_doc.total_outgoing_value,
                    "stock_entry":se_doc.name
                    
                })
        
                sw_doc.save()