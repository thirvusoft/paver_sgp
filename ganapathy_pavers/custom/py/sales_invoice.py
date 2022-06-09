import frappe
from erpnext.controllers.taxes_and_totals import get_itemised_tax
from erpnext.controllers.taxes_and_totals import get_itemised_taxable_amount
def update_customer(self,event):
    cus=self.customer
    for row in self.items:
        so=row.sales_order
        if(so):
            doc=frappe.get_doc('Sales Order', so)
            if(cus!=doc.customer):
                frappe.db.set(doc, "customer", cus)

	



# def tax_finder(document, event):

#     itemised_tax = get_itemised_tax(document.taxes)
#     itemised_taxable_amount = get_itemised_taxable_amount(document.sales_invoice_print_items_table)
#     print(itemised_tax),
#     print(itemised_taxable_amount) 
        #   if document:
        #           if document.tax_category:
        #                 si_items=document.sales_invoice_print_items_table
        #                 if document:   
        #                         itemised_tax, itemised_taxable_amount = get_itemised_tax_breakup_data(document)
        #                         if itemised_tax:
        #                                         item_name=list(itemised_tax.keys())
        #                                         item_tax=list(itemised_tax.values())
        #                         if itemised_taxable_amount:
        #                                         taxable_amount=list(itemised_taxable_amount.values())
        #                         if item_name:
        #                                         item_d2=[]
        #                                         for i in range(0,len(item_tax),1):
        #                                                 item_d2.append(list(item_tax[i].values()))
        #                                         if(document.tax_category=="In-State"):
        #                                                 tax_sgst=[]
        #                                                 tax_cgst=[]
        #                                                 for i in range(0,len(item_d2),1):
        #                                                         tax_sgst.append(item_d2[i][0]["tax_amount"])
        #                                                         tax_cgst.append(item_d2[i][1]["tax_amount"])
        #                                                 for i in range (0,len(item_name),1):
        #                                                         si_items[i].update({
        #                                                                 "taxable_amount":taxable_amount[i],
        #                                                                 "sgst":tax_sgst[i],
        #                                                                 "cgst":tax_cgst[i],
                                                                    
        #                                                         })
        #                                                 document.update({
        #                                                         'items':si_items
        #                                                 })
        #                                         if(document.tax_category=="Out-State"):
        #                                                 tax_igst=[]
        #                                                 for i in range(0,len(item_d2),1):
        #                                                         tax_igst.append(item_d2[i][0]["tax_amount"])
        #                                                 print(document.tax_category)
        #                                                 print(item_d2)
        #                                                 print(tax_igst)
        #                                                 for i in range (0,len(item_name),1):
        #                                                         si_items[i].update({
        #                                                                 "taxable_amount":taxable_amount[i],
        #                                                                 "igst":tax_igst[i]
        #                                                         })
        #                                                 document.update({
        #                                                         'items':si_items
        #                                                 })
                                                
                                                