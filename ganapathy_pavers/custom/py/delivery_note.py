import frappe



def update_qty_sitework(self,event):
    if(not self.is_return):
        for row in self.items:
            so=row.against_sales_order
            if(so):
                sw=frappe.get_value('Sales Order', so, 'site_work')
                if(sw):
                    item_group=frappe.get_value('Item', row.item_code, 'item_group')
                    doc=frappe.get_doc('Project', sw)
                    delivery_detail=doc.delivery_detail
                    create=1
                    for item in range(len(delivery_detail)):
                        if(row.item_code==delivery_detail[item].item and item_group!='Raw Material'):
                            create=0
                            delivery_detail[item].delivered_bundle+=row.ts_qty
                            delivery_detail[item].delivered_pieces+=row.pieces
                    raw_material=doc.raw_material
                    for item in range(len(raw_material)):
                        if(row.item_code==raw_material[item].item and item_group=='Raw Material'):
                            raw_material[item].delivered_quantity+=row.qty
                    if(create and item_group!='Raw Material'):
                        delivery_detail.append({
                            'item':row.item_code,
                            'delivered_bundle':row.ts_qty,
                            'delivered_pieces':row.pieces
                        })
                    doc.update({
                        'raw_material': raw_material,
                        'delivery_detail': delivery_detail
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
                    item_group=frappe.get_value('Item', row.item_code, 'item_group')
                    doc=frappe.get_doc('Project', sw)
                    delivery_detail=doc.delivery_detail
                    create=1
                    for item in range(len(delivery_detail)):
                        if(row.item_code==delivery_detail[item].item and item_group!='Raw Material'):
                            create=0
                            delivery_detail[item].delivered_bundle-=row.ts_qty
                            delivery_detail[item].delivered_pieces-=row.pieces
                    raw_material=doc.raw_material
                    for item in range(len(raw_material)):
                        if(row.item_code==raw_material[item].item and item_group=='Raw Material'):
                            raw_material[item].delivered_quantity-=row.qty
                    if(create and item_group!='Raw Material'):
                        delivery_detail.append({
                            'item':row.item_code,
                            'delivered_bundle':row.ts_qty,
                            'delivered_pieces':row.pieces
                        })
                    doc.update({
                        'raw_material': raw_material,
                        'delivery_detail': delivery_detail
                    })
                    doc.save()
        frappe.db.commit()




def update_return_qty_sitework(self,event):
    if(self.is_return):
        for row in self.items:
            so=row.against_sales_order
            if(so):
                sw=frappe.get_value('Sales Order', so, 'site_work')
                if(sw):
                    item_group=frappe.get_value('Item', row.item_code, 'item_group')
                    doc=frappe.get_doc('Project', sw)
                    delivery_detail=doc.delivery_detail
                    create=1
                    for item in range(len(delivery_detail)):
                        if(row.item_code==delivery_detail[item].item and item_group!='Raw Material'):
                            create=0
                            delivery_detail[item].returned_bundle+=row.ts_qty
                            delivery_detail[item].returned_pieces+=row.pieces
                    raw_material=doc.raw_material
                    for item in range(len(raw_material)):
                        if(row.item_code==raw_material[item].item and item_group=='Raw Material'):
                            raw_material[item].returned_quantity+=row.qty
                    if(create and item_group!='Raw Material'):
                        delivery_detail.append({
                            'item':row.item_code,
                            'returned_bundle':row.ts_qty,
                            'returned_pieces':row.pieces
                        })
                    doc.update({
                        'raw_material': raw_material,
                        'delivery_detail': delivery_detail
                    })
                    doc.save()
        frappe.db.commit()




def reduce_return_qty_sitework(self,event):
    if(self.is_return):
        for row in self.items:
            so=row.against_sales_order
            if(so):
                sw=frappe.get_value('Sales Order', so, 'site_work')
                if(sw):
                    item_group=frappe.get_value('Item', row.item_code, 'item_group')
                    doc=frappe.get_doc('Project', sw)
                    delivery_detail=doc.delivery_detail
                    create=1
                    for item in range(len(delivery_detail)):
                        if(row.item_code==delivery_detail[item].item and item_group!='Raw Material'):
                            create=0
                            delivery_detail[item].returned_bundle-=row.ts_qty
                            delivery_detail[item].returned_pieces-=row.pieces
                    raw_material=doc.raw_material
                    for item in range(len(raw_material)):
                        if(row.item_code==raw_material[item].item and item_group=='Raw Material'):
                            raw_material[item].returned_quantity-=row.qty
                    if(create and item_group!='Raw Material'):
                        delivery_detail.append({
                            'item':row.item_code,
                            'returned_bundle':row.ts_qty,
                            'returned_pieces':row.pieces
                        })
                    doc.update({
                        'raw_material': raw_material,
                        'delivery_detail': delivery_detail
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

def validate(doc,action):
    
    for d in doc.items:
        if d.pieces:
            doc.value_pieces = True
        if d.ts_qty:
            doc.value_bundle = True

        
  
def odometer_validate(doc,action):
    if(doc.return_odometer_value):
        doc.total_distance=doc.return_odometer_value-doc.current_odometer_value
        frappe.db.set_value("Delivery Note" , doc.name, "total_distance",doc.return_odometer_value-doc.current_odometer_value)
        


