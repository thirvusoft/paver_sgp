import frappe

def purchase_receipt_rawmaterial(self, event):
    for i in self.items:
        if not i.warehouse:
            frappe.throw("Please select warehouse")
        # if i.item_group=="Raw Material":
        #     warehouse_rm=i.warehouse.split("-")
        #     if(len(warehouse_rm)>=0):
        #         if((i.warehouse).split("-")[0]).strip()!="Rawmaterial warehouse":
        #             frappe.throw(f"Please select Accepted Warehouse as {frappe.bold('Rawmaterial warehouse')} for item: "+frappe.bold(i.item_code))

    