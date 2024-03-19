from erpnext.stock.doctype.delivery_note.delivery_note import DeliveryNote
import frappe
import ganapathy_pavers
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

class _DeliveryNote(DeliveryNote):
    def get_print_settings(self):
        print_setting_fields = ["print_as_bundle"]

        return print_setting_fields

def update_qty_sitework(self,event):
    if(self.doctype=='Sales Invoice' and self.update_stock==0):
        if self.site_work:
            doc=frappe.get_doc('Project', self.site_work)
            doc.save()
        return
    if(not self.is_return):
        for row in self.items:
            so=(row.against_sales_order if self.doctype=='Delivery Note' else row.sales_order)
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
                            delivery_detail[item].delivered_stock_qty+=row.stock_qty
                            delivery_detail[item].delivered_bundle+=row.ts_qty
                            delivery_detail[item].delivered_pieces+=row.pieces
                    raw_material=doc.raw_material
                    for item in range(len(raw_material)):
                        ts_so=(row.against_sales_order if self.doctype=='Delivery Note' else row.sales_order)
                        if(row.item_code==raw_material[item].item and item_group=='Raw Material' and ts_so==raw_material[item].sales_order):
                            raw_material[item].delivered_quantity+=row.qty
                    if(create and item_group!='Raw Material'):
                        delivery_detail.append({
                            'item':row.item_code,
                            'delivered_stock_qty': row.stock_qty,
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
    if(self.doctype=='Sales Invoice' and self.update_stock==0):
        if self.site_work:
            doc=frappe.get_doc('Project', self.site_work)
            doc.save()
        return
    if(not self.is_return):
        for row in self.items:
            so=(row.against_sales_order if self.doctype=='Delivery Note' else row.sales_order)
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
                            delivery_detail[item].delivered_stock_qty-=row.stock_qty
                            delivery_detail[item].delivered_bundle-=row.ts_qty
                            delivery_detail[item].delivered_pieces-=row.pieces
                    raw_material=doc.raw_material
                    for item in range(len(raw_material)):
                        ts_so=(row.against_sales_order if self.doctype=='Delivery Note' else row.sales_order)
                        if(row.item_code==raw_material[item].item and item_group=='Raw Material' and ts_so==raw_material[item].sales_order):
                            raw_material[item].delivered_quantity-=row.qty
                    if(create and item_group!='Raw Material'):
                        delivery_detail.append({
                            'item':row.item_code,
                            'delivered_stock_qty': row.stock_qty,
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
    if(self.doctype=='Sales Invoice' and self.update_stock==0):
        return
    if(self.is_return):
        for row in self.items:
            so=(row.against_sales_order if self.doctype=='Delivery Note' else row.sales_order)
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
                            delivery_detail[item].returned_stock_qty+=row.stock_qty
                            delivery_detail[item].returned_bundle+=row.ts_qty
                            delivery_detail[item].returned_pieces+=row.pieces
                    raw_material=doc.raw_material
                    for item in range(len(raw_material)):
                        ts_so=(row.against_sales_order if self.doctype=='Delivery Note' else row.sales_order)
                        if(row.item_code==raw_material[item].item and item_group=='Raw Material'  and ts_so==raw_material[item].sales_order):
                            raw_material[item].returned_quantity+=row.qty
                    if(create and item_group!='Raw Material'):
                        delivery_detail.append({
                            'item':row.item_code,
                            'returned_stock_qty':row.stock_qty,
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
    if(self.doctype=='Sales Invoice' and self.update_stock==0):
        return
    if(self.is_return):
        for row in self.items:
            so=(row.against_sales_order if self.doctype=='Delivery Note' else row.sales_order)
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
                            delivery_detail[item].returned_stock_qty-=row.stock_qty
                            delivery_detail[item].returned_bundle-=row.ts_qty
                            delivery_detail[item].returned_pieces-=row.pieces
                    raw_material=doc.raw_material
                    for item in range(len(raw_material)):
                        ts_so=(row.against_sales_order if self.doctype=='Delivery Note' else row.sales_order)
                        if(row.item_code==raw_material[item].item and item_group=='Raw Material' and ts_so==raw_material[item].sales_order):
                            raw_material[item].returned_quantity-=row.qty
                    if(create and item_group!='Raw Material'):
                        delivery_detail.append({
                            'item':row.item_code,
                            'returned_stock_qty':row.stock_qty,
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
        if d.so_detail:
            d.unacc = frappe.db.get_value('Sales Order Item', d.so_detail, 'unacc')
        
        # if d.item_group in ['Pavers', 'Compound Walls']:
        #     bdl = ganapathy_pavers.uom_conversion(d.item_code, d.uom, d.qty, 'Bdl', 0)
        #     pieces = ganapathy_pavers.uom_conversion(d.item_code, 'Bdl', (bdl or 0)%1, 'Nos', 0)
        #     d.ts_qty = int(bdl) or 0
        #     d.pieces = pieces or 0


        if d.pieces:
            doc.value_pieces = True
        if d.ts_qty:
            doc.value_bundle = True
    
    if doc.transporter == "Own Transporter" and doc.own_vehicle_no:
        vehicle_capacity_uoms = frappe.get_all("Weight and UOM", {'parent': doc.own_vehicle_no, 'parenttype': 'Vehicle'}, pluck='uom', group_by='uom')
        filled_uoms=[]
        for row in doc.vehicle_capacity:
            if row.uom in vehicle_capacity_uoms:
                filled_uoms.append(row.uom)
                row.actual_weight = frappe.get_value("Weight and UOM", {'parent': doc.own_vehicle_no, 'parenttype': 'Vehicle', 'uom': row.uom}, 'weight') or 0
                row.difference = (row.weight or 0) - (row.actual_weight or 0)
        
        for i in vehicle_capacity_uoms:
            if i not in filled_uoms:
                actual_weight = frappe.get_value("Weight and UOM", {'parent': doc.own_vehicle_no, 'parenttype': 'Vehicle', 'uom': i}, 'weight') or 0
                doc.append('vehicle_capacity', {
                    'uom': i,
                    'actual_weight': actual_weight or 0,
                    'weight': 0,
                    'difference': -1 * (actual_weight or 0),
                })

     
def sales_order_required(self,event):
    """check in manage account if sales order required or not"""
    if frappe.db.get_value("Selling Settings", None, "sales_order_required") == "Yes" and not self.is_sample_delivery:
        for d in self.get("items"):
            if not d.against_sales_order:
                frappe.throw(("Sales Order required for Item {0}").format(d.item_code))



def other_vehicle_link():
    make_property_setter("Delivery Note", "vehicle_no", "fieldtype", "Link", "Select", validate_fields_for_doctype=False)
    make_property_setter("Delivery Note", "vehicle_no", "options", "Other Vehicle", "Small Text")

@frappe.whitelist()
def update_customer_in_delivery_note(delivery_note, customer):
    if frappe.db.get_value('Delivery Note', delivery_note, 'per_billed'):
        frappe.throw(f"Couldn't update customer for billed delivery note {delivery_note}")
    
    customer_name = frappe.db.get_value('Customer', customer, 'customer_name')
    dn = frappe.get_doc('Delivery Note', delivery_note)

    if not frappe.db.get_value('Project', dn.site_work, 'is_multi_customer'):
        frappe.throw(f'{dn.site_work} is not a multi customer site')

    dn.update({
        'customer': customer,
        'customer_name': customer_name
    })
    dn.flags.ignore_validate_update_after_submit = True
    dn.save()
