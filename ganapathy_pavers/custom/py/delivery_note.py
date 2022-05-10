import frappe


def update_qty_sitework(self,event):
    for row in self.items:
        so=row.against_sales_order
        if(so):
            sw=frappe.get_value('Sales Order', so, 'site_work')
            if(sw):
                doc=frappe.get_doc('Project', sw)
                item_details=doc.item_details
                for item in range(len(item_details)):
                    if(item_details[item].item==row.item_code and item_details[item].sales_order==so):
                        item_details[item].delivered_qty=float(item_details[item].delivered_qty)+row.ts_qty

                doc.update({
                    'item_details': item_details
                })
                doc.save()
    frappe.db.commit()



def reduce_qty_sitework(self,event):
    for row in self.items:
        so=row.against_sales_order
        if(so):
            sw=frappe.get_value('Sales Order', so, 'site_work')
            if(sw):
                doc=frappe.get_doc('Project', sw)
                item_details=doc.item_details
                for item in range(len(item_details)):
                    if(item_details[item].item==row.item_code and item_details[item].sales_order==so):
                        item_details[item].delivered_qty=float(item_details[item].delivered_qty)-row.ts_qty

                doc.update({
                    'item_details': item_details
                })
                doc.save()
    frappe.db.commit()