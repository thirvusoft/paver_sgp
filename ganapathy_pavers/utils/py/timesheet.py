import frappe
from erpnext.stock.doctype.stock_entry.stock_entry_utils import make_stock_entry
from erpnext.stock.doctype.batch.batch import make_batch

def stock_entry(doc,method=None):
    a=doc.end_date
    
    for data in doc.time_logs:
        batch=frappe.new_doc("Batch")
        batch.batch_id=a.strftime('%m/%d/%y')
        batch.item=data.item
        batch.insert()
        company = frappe.get_doc('Company',doc.company)
        abbr=company.abbr
        make_stock_entry(item_code=data.item,
        qty=data.total_production_pavers,
        to_warehouse="Finished Goods - "+abbr,
        batch_no =a.strftime('%m/%d/%y'))