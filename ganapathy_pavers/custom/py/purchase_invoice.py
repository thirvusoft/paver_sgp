import frappe

def update_pi_items(self, event=None):
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
                        "amount": field_data["amount"],
                        "item_tax_template": field_data["item_tax_template"],
                        "tax_rate": field_data["tax_rate"],
                        "tax_amount": field_data["tax_amount"],
                        "purchase_invoice": field_data["purchase_invoice"],
                    })
                elif field == "Raw Material":
                    sw_doc.append(frappe.scrub(field), field_data)
        sw_doc.save()
