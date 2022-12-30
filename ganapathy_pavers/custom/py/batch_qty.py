from erpnext.stock.doctype.batch.batch import get_batch_qty
import frappe



batch_doc=frappe.get_all("Batch", filters={"disabled":0}, fields=["item","name"])
for i in batch_doc:
    bin_doc= get_batch_qty(batch_no=i["name"],item_code=i["item"])
    for j in bin_doc:
        frappe.db.set_value("Bin",{"warehouse":j["warehouse"],"item_code":i["item"]},"actual_qty",j['qty'])
        frappe.db.commit()