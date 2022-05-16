import frappe



def update_qty_sitework(self,event):
    if(not self.is_return):
        for row in self.items:
            so=row.against_sales_order
            if(so):
                sw=frappe.get_value('Sales Order', so, 'site_work')
                if(sw):
                    doc=frappe.get_doc('Project', sw)
                    item_details=doc.item_details
                    raw_material=doc.raw_material
                    for item in range(len(item_details)):
                        if(item_details[item].item==row.item_code and item_details[item].sales_order==so):
                            item_details[item].delivered_qty=float(item_details[item].delivered_qty)+row.ts_qty
                    for item in range(len(raw_material)):
                        if(raw_material[item].item==row.item_code and raw_material[item].sales_order==so):
                            raw_material[item].delivered_quantity=float(raw_material[item].delivered_quantity)+row.qty
                    doc.update({
                        'item_details': item_details,
                        'raw_material': raw_material
                    })
                    doc.save()
        frappe.db.commit()



def reduce_qty_sitework(self,event):
    if(not self.is_return):
        for row in self.items:
            so=row.against_sales_order
            if(so):
                sw=frappe.get_value('Sales Order', so, 'site_work')
                if(sw):
                    doc=frappe.get_doc('Project', sw)
                    item_details=doc.item_details
                    raw_material=doc.raw_material
                    for item in range(len(item_details)):
                        if(item_details[item].item==row.item_code and item_details[item].sales_order==so):
                            item_details[item].delivered_qty=float(item_details[item].delivered_qty)-row.ts_qty
                    for item in range(len(raw_material)):
                        if(raw_material[item].item==row.item_code and raw_material[item].sales_order==so):
                            raw_material[item].delivered_quantity=float(raw_material[item].delivered_quantity)-row.qty
                            
                    doc.update({
                        'item_details': item_details,
                        'raw_material': raw_material
                    })
                    doc.save()
        frappe.db.commit()


def update_customer(self,event):
    cus=self.customer
    for row in self.items:
        so=row.against_sales_order
        if(so):
            doc=frappe.get_doc('Sales Order', so)
            if(cus!=doc.customer):
                frappe.db.set(doc, "customer", cus)
