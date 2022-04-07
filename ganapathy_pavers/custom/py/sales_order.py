import frappe

@frappe.whitelist()
def update_item(self,action):
    frappe.errprint(action)
    if(self.type=='Pavers'):
        items=[]
        frappe.errprint(self.items)
        for row in self.pavers:
            if(row.allocated_paver_area==0):
                frappe.throw("Area Cannot be Zero.")
            items.append(dict(
                item_code=row.item,
                qty=row.allocated_paver_area,
                rate=row.rate,
                amount=row.amount,
                item_name=frappe.get_value('Item', row.item,'item_name'),
                description=frappe.get_value('Item', row.item,'description'),
                uom=frappe.get_value('Item', row.item,'sales_uom'),
                conversion_factor=1
            ))
        self.update({
            'items': items
        })
        frappe.errprint(items)