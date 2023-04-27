
__version__ = '0.0.1'

from ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing import throw_error
import frappe

def uom_conversion(item : str, from_uom='', from_qty=0, to_uom='') -> float:
	if (not to_uom):
		return from_qty
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
		throw_error(from_uom + " Conversion", item)
	if(not to_conv):
		throw_error(to_uom + " Conversion", item)

	return (float(from_qty) * from_conv) / to_conv


def get_valuation_rate(item_code : str, warehouse : str, posting_date=None) -> float:
	if not posting_date:
		posting_date = frappe.utils.nowdate()
	rate=frappe.get_all("Stock Ledger Entry", {
			"item_code": item_code,
			"warehouse": warehouse,
			"posting_date": ["<=", posting_date],
			"is_cancelled": 0,
		},
		pluck="valuation_rate", order_by="posting_date DESC", limit=1)
	
	if not rate:
		rate=frappe.get_all("Stock Ledger Entry", {
			"item_code": item_code,
			"warehouse": warehouse,
			"is_cancelled": 0,
		},
		pluck="valuation_rate", order_by="posting_date DESC", limit=1)
	if not rate:
		rate=frappe.get_all("Stock Ledger Entry", {
			"item_code": item_code,
			"is_cancelled": 0,
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


def get_buying_rate(item_code : str, warehouse : str, posting_date=None) -> float:
	if not posting_date:
		posting_date = frappe.utils.nowdate()
	rate=frappe.get_all("Stock Ledger Entry", {
			"item_code": item_code,
			"warehouse": warehouse,
			"posting_date": ["<=", posting_date],
			"is_cancelled": 0,
		},
		pluck="incoming_rate", order_by="posting_date DESC", limit=1)
	
	if not rate:
		rate=frappe.get_all("Stock Ledger Entry", {
			"item_code": item_code,
			"warehouse": warehouse,
			"is_cancelled": 0,
		},
		pluck="incoming_rate", order_by="posting_date DESC", limit=1)
	if not rate:
		rate=frappe.get_all("Stock Ledger Entry", {
			"item_code": item_code,
			"is_cancelled": 0,
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

def custom_safe_eval(code, eval_globals=None, eval_locals=None):
	"""A safer `eval`"""
	whitelisted_globals = {"int": int, "float": float, "long": int, "round": round,"frappe":frappe,"len":len}

	UNSAFE_ATTRIBUTES = {
		# Generator Attributes
		"gi_frame",
		"gi_code",
		# Coroutine Attributes
		"cr_frame",
		"cr_code",
		"cr_origin",
		# Async Generator Attributes
		"ag_code",
		"ag_frame",
		# Traceback Attributes
		"tb_frame",
		"tb_next",
		# Format Attributes
		"format",
		"format_map",
	}

	for attribute in UNSAFE_ATTRIBUTES:
		if attribute in code:
			frappe.throw('Illegal rule {0}. Cannot use "{1}"'.format(frappe.bold(code), attribute))

	if "__" in code:
		frappe.throw('Illegal rule {0}. Cannot use "__"'.format(frappe.bold(code)))

	if not eval_globals:
		eval_globals = {}

	eval_globals["__builtins__"] = {}
	eval_globals.update(whitelisted_globals)
	return eval(code, eval_globals, eval_locals)

def get_bank_details(company : str) -> dict:
	doc=frappe.get_all("Bank Account", {"company": company, "account": frappe.get_value("Company", company, "default_bank_account")}, ["branch_name", "ifsc_code", "bank", "bank_account_no"])
	return doc[0] if doc else {"branch_name":"", "ifsc_code":"", "bank":"", "bank_account_no":""}

def custom_safe_eval(code, eval_globals=None, eval_locals=None):
	"""A safer `eval`"""
	whitelisted_globals = {"int": int, "float": float, "long": int, "round": round,"frappe":frappe,"len":len}

	UNSAFE_ATTRIBUTES = {
		# Generator Attributes
		"gi_frame",
		"gi_code",
		# Coroutine Attributes
		"cr_frame",
		"cr_code",
		"cr_origin",
		# Async Generator Attributes
		"ag_code",
		"ag_frame",
		# Traceback Attributes
		"tb_frame",
		"tb_next",
		# Format Attributes
		"format",
		"format_map",
	}

	for attribute in UNSAFE_ATTRIBUTES:
		if attribute in code:
			frappe.throw('Illegal rule {0}. Cannot use "{1}"'.format(frappe.bold(code), attribute))

	if "__" in code:
		frappe.throw('Illegal rule {0}. Cannot use "__"'.format(frappe.bold(code)))

	if not eval_globals:
		eval_globals = {}

	eval_globals["__builtins__"] = {}
	eval_globals.update(whitelisted_globals)
	return eval(code, eval_globals, eval_locals)
