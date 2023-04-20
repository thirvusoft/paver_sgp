
from email.utils import formatdate
from erpnext.accounts.doctype.account.account import get_account_currency
from erpnext.accounts.utils import get_fiscal_years
from erpnext.assets.doctype.asset.asset import is_cwip_accounting_enabled
from erpnext.controllers.accounts_controller import set_balance_in_account_currency
from erpnext.stock import get_warehouse_account_map
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import get_item_account_wise_additional_cost
from ganapathy_pavers.custom.py.journal_entry_override import get_workstations
import erpnext
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice, make_regional_gl_entries
from erpnext.accounts.general_ledger import check_if_in_list
import frappe
from frappe import _
from frappe.model.meta import get_field_precision
from frappe.utils.data import cint, flt
from six import iteritems


class _PurchaseInvoice(PurchaseInvoice):
    def get_gl_entries(self, warehouse_account=None):
        self.auto_accounting_for_stock = erpnext.is_perpetual_inventory_enabled(self.company)
        if self.auto_accounting_for_stock:
            self.stock_received_but_not_billed = self.get_company_default("stock_received_but_not_billed")
            self.expenses_included_in_valuation = self.get_company_default("expenses_included_in_valuation")
        else:
            self.stock_received_but_not_billed = None
            self.expenses_included_in_valuation = None

        self.negative_expense_to_be_booked = 0.0
        gl_entries = []

        self.make_supplier_gl_entry(gl_entries)
        
        self.make_item_gl_entries(gl_entries)
        
        self.make_discount_gl_entries(gl_entries)

        if self.check_asset_cwip_enabled():
            self.get_asset_gl_entry(gl_entries)

        self.make_tax_gl_entries(gl_entries)
        self.make_exchange_gain_loss_gl_entries(gl_entries)
        self.make_internal_transfer_gl_entries(gl_entries)

        gl_entries = make_regional_gl_entries(gl_entries, self)

        gl_entries = merge_similar_entries(gl_entries)

        self.make_payment_gl_entries(gl_entries)
        self.make_write_off_gl_entry(gl_entries)
        self.make_gle_for_rounding_adjustment(gl_entries)

        add_expense_to_gl_entries(self, gl_entries)

        return gl_entries

def add_expense_to_gl_entries(self, gl_entries):
        expense_name = ""
        if len(self.items) > 1:
            expense_name = self.expense_name
            if not expense_name:
                frappe.throw("Please Enter Expense Name")
        elif len(self.items) == 1:
             expense_name=self.items[0].get("item_code")

        for gl_dict in gl_entries:
            gl_dict.update({
                "expense_name": expense_name, # Customization
                "vehicle": self.get("vehicle") if self.get("expense_type") else "", # Customization
                "expense_type": self.get("expense_type"), # Customization
                "paver": self.get("paver"), # Customization
                "is_shot_blast": self.get("is_shot_blast"), # Customization
                "compound_wall": self.get("compound_wall"), # Customization
                "fencing_post": self.get("fencing_post"), # Customization
                "lego_block": self.get("lego_block"), # Customization
                "from_date": self.get("from_date"), # Customization
                "to_date": self.get("to_date"), # Customization
                "split_equally": self.get("split_equally"), # Customization
            })
            # Customization start
            for wrk in get_workstations(): 
                gl_dict.update({
                    wrk: self.get(wrk)
                })
            # Customization end


        return gl_entries

def merge_similar_entries(gl_map, precision=None):
	merged_gl_map = []
	accounting_dimensions = get_accounting_dimensions()
	for entry in gl_map:
		# if there is already an entry in this account then just add it
		# to that entry
		same_head = check_if_in_list(entry, merged_gl_map, accounting_dimensions + ["vehicle", "expense_type", "paver", "is_shot_blast", "compound_wall", "fencing_post", "lego_block", "from_date", "to_date", "split_equally"] + get_workstations()) # Customization
		if same_head:
			same_head.debit	= flt(same_head.debit) + flt(entry.debit)
			same_head.debit_in_account_currency	= \
				flt(same_head.debit_in_account_currency) + flt(entry.debit_in_account_currency)
			same_head.credit = flt(same_head.credit) + flt(entry.credit)
			same_head.credit_in_account_currency = \
				flt(same_head.credit_in_account_currency) + flt(entry.credit_in_account_currency)
		else:
			merged_gl_map.append(entry)

	company = gl_map[0].company if gl_map else erpnext.get_default_company()
	company_currency = erpnext.get_company_currency(company)

	if not precision:
		precision = get_field_precision(frappe.get_meta("GL Entry").get_field("debit"), company_currency)

	# filter zero debit and credit entries
	merged_gl_map = filter(lambda x: flt(x.debit, precision)!=0 or flt(x.credit, precision)!=0, merged_gl_map)
	merged_gl_map = list(merged_gl_map)

	return merged_gl_map