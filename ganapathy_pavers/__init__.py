
__version__ = '0.0.1'

from ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing import throw_error
import frappe

def uom_conversion(item, from_uom='', from_qty=0, to_uom=''):
    if(not from_uom):
        from_uom = frappe.get_value('Item', item, 'stock_uom')
    item_doc = frappe.get_doc('Item', item)
    from_conv = 0
    to_conv = 0
    for row in item_doc.uoms:
        if(row.uom == from_uom):
            from_conv = row.conversion_factor
        if(row.uom == to_uom):
            to_conv = row.conversion_factor
    if(not from_conv):
        throw_error(from_uom + " Bundle Conversion", item)
    if(not to_conv):
        throw_error(to_uom + " Bundle Conversion", item)
    
    return (float(from_qty) * from_conv) / to_conv


def get_valuation_rate(item_code, warehouse, posting_date=frappe.utils.nowdate()):
	rate=frappe.get_all("Stock Ledger Entry", {
			"item_code": item_code,
			"warehouse": warehouse,
			"posting_date": ["<=", posting_date],
		},
		pluck="valuation_rate", order_by="posting_date DESC", limit=1)
	
	if not rate:
		rate=frappe.get_all("Stock Ledger Entry", {
			"item_code": item_code,
			"warehouse": warehouse,
		},
		pluck="valuation_rate", order_by="posting_date DESC", limit=1)
	if not rate:
		rate=frappe.get_all("Stock Ledger Entry", {
			"item_code": item_code,
		},
		pluck="valuation_rate", order_by="posting_date DESC", limit=1)
	if not rate:
		rate=frappe.get_all("Item", {
			"name": item_code,
		},
		pluck="valuation_rate")
	if not rate:
		return 0
	return rate[0]


def get_buying_rate(item_code, warehouse, posting_date=frappe.utils.nowdate()):
	rate=frappe.get_all("Stock Ledger Entry", {
			"item_code": item_code,
			"warehouse": warehouse,
			"posting_date": ["<=", posting_date],
		},
		pluck="incoming_rate", order_by="posting_date DESC", limit=1)
	
	if not rate:
		rate=frappe.get_all("Stock Ledger Entry", {
			"item_code": item_code,
			"warehouse": warehouse,
		},
		pluck="incoming_rate", order_by="posting_date DESC", limit=1)
	if not rate:
		rate=frappe.get_all("Stock Ledger Entry", {
			"item_code": item_code,
		},
		pluck="incoming_rate", order_by="posting_date DESC", limit=1)
	if not rate:
		rate=frappe.get_all("Item", {
			"name": item_code,
		},
		pluck="last_purchase_rate")
	if not rate:
		return 0
	return rate[0]

def get_bank_details(company):
	doc=frappe.get_all("Bank Account", {"company": company, "account": frappe.get_value("Company", company, "default_bank_account")}, ["branch_name", "ifsc_code", "bank", "bank_account_no"])
	return doc[0] if doc else {"branch_name":"", "ifsc_code":"", "bank":"", "bank_account_no":""}
