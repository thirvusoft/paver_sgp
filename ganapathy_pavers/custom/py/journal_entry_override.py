from frappe.model.meta import get_field_precision
from frappe.utils.data import flt
import erpnext, frappe
from frappe import _
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions
from erpnext.accounts.doctype.journal_entry.journal_entry import JournalEntry
from erpnext.accounts.general_ledger import check_if_in_list, make_reverse_gl_entries, save_entries, update_net_values, validate_accounting_period



class _JournalEntry(JournalEntry):
    def make_gl_entries(self, cancel=0, adv_adj=0):
        gl_map = []
        for d in self.get("accounts"):
            if d.debit or d.credit:
                r = [d.user_remark, self.remark]
                r = [x for x in r if x]
                remarks = "\n".join(r)
                gl_dict = {
                        "account": d.account,
                        "vehicle": d.vehicle, # Customization
                        "expense_type": d.expense_type, # Customization
                        "paver": d.paver, # Customization
                        "is_shot_blast": d.is_shot_blast, # Customization
                        "compound_wall": d.compound_wall, # Customization
                        "fencing_post": d.fencing_post, # Customization
                        "lego_block": d.lego_block, # Customization
                        "party_type": d.party_type,
                        "due_date": self.due_date,
                        "party": d.party,
                        "against": d.against_account,
                        "debit": flt(d.debit, d.precision("debit")),
                        "credit": flt(d.credit, d.precision("credit")),
                        "account_currency": d.account_currency,
                        "debit_in_account_currency": flt(d.debit_in_account_currency, d.precision("debit_in_account_currency")),
                        "credit_in_account_currency": flt(d.credit_in_account_currency, d.precision("credit_in_account_currency")),
                        "against_voucher_type": d.reference_type,
                        "against_voucher": d.reference_name,
                        "remarks": remarks,
                        "voucher_detail_no": d.reference_detail_no,
                        "cost_center": d.cost_center,
                        "project": d.project,
                        "finance_book": self.finance_book
                    }
                # Customization start
                for wrk in get_workstations(): 
                    gl_dict.update({
                        wrk: d.get(wrk)
                    })
                # Customization end

                gl_map.append(
                    self.get_gl_dict(gl_dict, item=d)
                )

        if self.voucher_type in ('Deferred Revenue', 'Deferred Expense'):
            update_outstanding = 'No'
        else:
            update_outstanding = 'Yes'

        if gl_map:
            make_gl_entries(gl_map, cancel=cancel, adv_adj=adv_adj, update_outstanding=update_outstanding)

# General Ledger Functions
def make_gl_entries(gl_map, cancel=False, adv_adj=False, merge_entries=True, update_outstanding='Yes', from_repost=False):
    if gl_map:
        if not cancel:
            validate_accounting_period(gl_map)
            gl_map = process_gl_map(gl_map, merge_entries)
            if gl_map and len(gl_map) > 1:
                save_entries(gl_map, adv_adj, update_outstanding, from_repost)
            # Post GL Map proccess there may no be any GL Entries
            elif gl_map:
                frappe.throw(_("Incorrect number of General Ledger Entries found. You might have selected a wrong Account in the transaction."))
        else:
            make_reverse_gl_entries(gl_map, adv_adj=adv_adj, update_outstanding=update_outstanding)


def process_gl_map(gl_map, merge_entries=True, precision=None):
    if merge_entries:
        gl_map = merge_similar_entries(gl_map, precision)
    for entry in gl_map:
        # toggle debit, credit if negative entry
        if flt(entry.debit) < 0:
            entry.credit = flt(entry.credit) - flt(entry.debit)
            entry.debit = 0.0

        if flt(entry.debit_in_account_currency) < 0:
            entry.credit_in_account_currency = \
                flt(entry.credit_in_account_currency) - flt(entry.debit_in_account_currency)
            entry.debit_in_account_currency = 0.0

        if flt(entry.credit) < 0:
            entry.debit = flt(entry.debit) - flt(entry.credit)
            entry.credit = 0.0

        if flt(entry.credit_in_account_currency) < 0:
            entry.debit_in_account_currency = \
                flt(entry.debit_in_account_currency) - flt(entry.credit_in_account_currency)
            entry.credit_in_account_currency = 0.0

        update_net_values(entry)

    return gl_map

def get_workstations():
    return [frappe.scrub(i) for i in frappe.get_all("Workstation", {"used_in_expense_splitup": 1}, pluck="name")]

def merge_similar_entries(gl_map, precision=None):
    merged_gl_map = []
    accounting_dimensions = get_accounting_dimensions()
    for entry in gl_map:
        # if there is already an entry in this account then just add it
        # to that entry
        same_head = check_if_in_list(entry, merged_gl_map, accounting_dimensions + ["vehicle", "expense_type", "paver", "is_shot_blast", "compound_wall", "fencing_post", "lego_block",] + get_workstations()) # Customization
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