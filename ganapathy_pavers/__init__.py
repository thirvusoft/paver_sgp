
__version__ = '0.0.1'

from ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing import throw_error
import frappe

def uom_conversion(item : str, from_uom='', from_qty=0.0, to_uom='', throw_err=True) -> float:
	''' 
		For converting rate, pass from as to and to as from uoms
	'''
	if (not to_uom):
		return from_qty
	if(not from_uom):
		from_uom = frappe.get_value('Item', item, 'stock_uom')

	from_conv = frappe.db.get_value("UOM Conversion Detail", {'parent': item, 'parenttype': 'Item', 'uom': from_uom}, 'conversion_factor') or 0
	to_conv = frappe.db.get_value("UOM Conversion Detail", {'parent': item, 'parenttype': 'Item', 'uom': to_uom}, 'conversion_factor') or 0

	if(not from_conv):
		if throw_err:
			throw_error(from_uom + " Conversion", item)
		else:
			return 0.0
	
	if(not to_conv):
		if throw_err:
			throw_error(to_uom + " Conversion", item)
		else:
			return 0.0

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


def get_item_price(args, item_code, ignore_party=False, to_uom=None):
	"""
		Get name, price_list_rate from Item Price based on conditions
			Check if the desired qty is within the increment of the packing list.
		:param args: dict (or frappe._dict) with mandatory fields price_list, uom
			optional fields transaction_date, customer, supplier
		:param item_code: str, Item Doctype field item_code
	"""

	args['item_code'] = item_code

	conditions = """where item_code=%(item_code)s
		and price_list=%(price_list)s"""

	if args.get("uom"):
		conditions+= f"""
			and ifnull(uom, '') in ('', {args.get("uom")})
		"""

	conditions += "and ifnull(batch_no, '') in ('', %(batch_no)s)"

	if not ignore_party:
		if args.get("customer"):
			conditions += " and customer=%(customer)s"
		elif args.get("supplier"):
			conditions += " and supplier=%(supplier)s"
		else:
			conditions += "and (customer is null or customer = '') and (supplier is null or supplier = '')"

	if args.get('transaction_date'):
		conditions += """ and %(transaction_date)s between
			ifnull(valid_from, '2000-01-01') and ifnull(valid_upto, '2500-12-31')"""

	if args.get('posting_date'):
		conditions += """ and %(posting_date)s between
			ifnull(valid_from, '2000-01-01') and ifnull(valid_upto, '2500-12-31')"""

	rates = frappe.db.sql(""" select name, price_list_rate, uom
		from `tabItem Price` {conditions}
		order by valid_from desc, batch_no desc, uom desc """.format(conditions=conditions), args, as_list=True)

	for rate in rates:
		if to_uom and item_code and rate[2]:
			rate[1] = uom_conversion(item=item_code, from_uom=to_uom, from_qty=rate[1], to_uom=rate[2])

	return rates
