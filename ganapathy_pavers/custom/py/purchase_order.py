import frappe

def getdate(doc, event):
    doc.required_by_date = doc.schedule_date

def purchasenotification():
    notification = frappe.get_all(
			"Purchase Order",
			fields=["*"],
			filters={"per_received": 0, "required_by_date": frappe.utils.nowdate()},
            pluck="name"
		)
    for i in notification:
        doc=frappe.new_doc('Notification Log')
        doc.update({
        'subject': f'Goods for this PO({ i }) has not been received',
        'type': 'Alert',
        'document_type': 'Purchase Order',
        'message': f'The Purchase Order { i } does not have a purchase receipt'
        })
        doc.flags.ignore_permissions=True
        doc.save()

@frappe.whitelist()
def update_status(status, name):
    po = frappe.get_doc("Purchase Order", name)
    po.update_status(status)
    po.update_delivered_qty_in_sales_order()
    update_drop_ship_items_in_sw(po, event="before_cancel" if status == "Submitted" else "on_update_after_submit")

def update_drop_ship_items_in_sw(self, event=None):
    items = {}
    mul = 1
    if event=="before_cancel":
        if self.get_db_value("status") != "Delivered":
            return
        mul=-1

    for row in self.items:
        if row.delivered_by_supplier and row.sales_order:
            sw = frappe.get_value("Sales Order", row.sales_order, "site_work") or self.site_work
            if sw:
                if sw not in items:
                    items[sw]=[]

                items[sw].append({
                    "item": row.item_code,
                    "qty": row.qty * mul,
                    "stock_qty": row.stock_qty * mul,
                    "item_group": row.item_group,
                    "sales_order": row.sales_order,
                })

    for sw in items:
        sw_doc=frappe.get_doc("Project", sw)

        for item in items[sw]:
            create=1
            if item.get("item_group")!='Raw Material':
                for sw_row in sw_doc.deliverey_detail:
                    if sw_row.item == item.get('item'):
                        sw_row.delivered_stock_qty = (sw_row.get('delivered_stock_qty', 0) or 0) + item.get("qty")
                        create=0
                if(create):
                    sw_doc.update("delivery_detail", {
                        'item':item.get("item"),
                        'delivered_stock_qty': item.get("stock_qty"),
                    })
            else:
                for sw_row in sw_doc.raw_material:
                    if sw_row.item == item.get('item') and sw_row.get("sales_order") == item.get("sales_order"):
                        sw_row.delivered_quantity = (sw_row.get('delivered_quantity', 0) or 0) + item.get("qty")
        
        sw_doc.flags.ignore_mandatory = True
        sw_doc.save()
            