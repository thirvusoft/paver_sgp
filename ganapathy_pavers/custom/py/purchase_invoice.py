import json
import frappe

def update_pi_items(self, event=None):
    self.project = self.site_work
    if not self.site_work:
        self.items_add_under=""

    for row in self.items:
        row.site_work=self.site_work
        row.items_add_under=self.items_add_under

def site_work_details_from_pi(self, event=None):
    site_items={}
    
    for row in self.items:
        if row.site_work and row.items_add_under:
            if row.site_work not in site_items:
                site_items[row.site_work] = {}
            
            if row.items_add_under not in site_items[row.site_work]:
                site_items[row.site_work][row.items_add_under]=[]
            tax_rate=sum([r.tax_rate for r in frappe.get_doc("Item Tax Template", row.item_tax_template).taxes]) if row.item_tax_template else 0

            site_items[row.site_work][row.items_add_under].append({
                "item": row.item_code,
                "qty": row.qty,
                "uom": row.uom,
                "rate": row.rate,
                "amount": row.amount,
                "item_tax_template": row.item_tax_template,
                "tax_rate": tax_rate,
                "tax_amount": row.amount * tax_rate / 100,
                "purchase_invoice": self.name,
            })
    
    if event == "on_cancel":
        for site in site_items:
            sw_doc=frappe.get_doc("Project", site)
            for field in site_items[site]:
                res=[]
                for row in sw_doc.get(frappe.scrub(field), []):
                    if row.purchase_invoice != self.name:
                        res.append(row)
                sw_doc.update({
                    frappe.scrub(field): res,
                })
            
            sw_doc.save()
        return
            
    for site in site_items:
        sw_doc=frappe.get_doc("Project", site)
        for field in site_items[site]:
            for field_data in site_items[site][field]:
                if field == "Additional Cost":
                    sw_doc.append(frappe.scrub(field), {
                        "description": field_data["item"],
                        "qty": field_data["qty"],
                        "uom": field_data["uom"],
                        "rate": field_data["rate"],
                        "amount": field_data["amount"] + field_data["tax_amount"],
                        "item_tax_template": field_data["item_tax_template"],
                        "tax_rate": field_data["tax_rate"],
                        "tax_amount": field_data["tax_amount"],
                        "purchase_invoice": field_data["purchase_invoice"],
                    })
                elif field == "Raw Material":
                    sw_doc.append(frappe.scrub(field), field_data)
        sw_doc.save()


def create_service_vehicle_log(self, event=None):
    if not (self.vehicle and self.purpose=="Service"):
        return

    services = []
    for row in self.items:
        service = frappe.db.get_value("Service Item", {'item_code': row.item_code}, "name")
        if not service:
            frappe.throw(f"""Please link this item <b>{row.item_code}</b> to a <a href="/app/service-item"><b>Service</b></a>""")
        
        services.append({
            "service_item": service,
            "type": row.service_type,
            "expense_amount": row.amount,
            "description": row.description,
        })

    service_doc = frappe.new_doc("Vehicle Log")

    service_doc.update({
        "license_plate": self.vehicle,
        "date": self.posting_date,
        "odometer": frappe.db.get_value("Vehicle", self.vehicle, "fuel_odometer"),
        "select_purpose": self.purpose,
        "supplier1": self.supplier,
        "service_item_table": services,
        "reference_doctype": self.doctype,
        "reference_document": self.name,
    })

    service_doc.save()
    service_doc.submit()

@frappe.whitelist()
def create_service_logs(docnames=[]):
    if isinstance(docnames, str):
        try:
            docnames = json.loads(docnames)
        except:
            return 0
    
    pi=[]
    filters={"docstatus": 1, "vehicle": ["is", "set"], "purpose": "Service"}
    if docnames:
        filters["name"] = ["in", docnames]

    success = 0
    pi=frappe.get_all("Purchase Invoice", filters, ["name", "vehicle", "purpose"])
    for pi_doc in pi:
        if not frappe.get_all("Vehicle Log", {"docstatus": 1, "license_plate": pi_doc['vehicle'], "select_purpose": pi_doc["purpose"]}):
            create_service_vehicle_log(frappe.get_doc("Purchase Invoice", pi_doc["name"]))
            success+=1
    
    print(success)
    return success
