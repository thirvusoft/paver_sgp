from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions
from erpnext.accounts.general_ledger import check_if_in_list, make_reverse_gl_entries, save_entries, update_net_values, validate_accounting_period
from frappe.model.meta import get_field_precision
from ganapathy_pavers.custom.py.journal_entry_override import get_workstations
import erpnext
from erpnext.controllers.stock_controller import StockController
from erpnext.stock import get_warehouse_account_map
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
from erpnext.stock.stock_ledger import get_valuation_rate
import frappe
from frappe import _
from frappe.utils.data import cint, flt
from six import iteritems
from ganapathy_pavers import uom_conversion

def update_asset(self, event):
    fg_completed_qty=0
    for row in self.items:
        if row.is_finished_item:
            fg_completed_qty+=(uom_conversion(row.item_code, row.stock_uom, row.transfer_qty, 'Nos') or 0)
    if(self.stock_entry_type=="Manufacture" and self.bom_no and fg_completed_qty):
        asset=frappe.get_value('BOM', self.bom_no, 'asset_name')
        if(asset):
            doc=frappe.get_doc('Asset', asset)
            if(event=='on_submit'):
                doc.update({
                    'current_number_of_strokes': float(fg_completed_qty)+float(float(doc.current_number_of_strokes) or 0)
                })  
            if(event=='on_cancel'):
                doc.update({
                    'current_number_of_strokes': -float(fg_completed_qty)+float(float(doc.current_number_of_strokes) or 0)
                })
            if((float(doc.notification_alert_at or 0)<float(doc.current_number_of_strokes or 0)) and doc.to_notify!=1):
                doc.update({
                    'to_notify': 1
                })
            elif((float(doc.notification_alert_at or 0)>float(doc.current_number_of_strokes or 0)) and doc.to_notify!=0):
                doc.update({
                    'to_notify': 0
                })
            doc.flags.ignore_mandatory=True
            doc.flags.ignore_permission=True
            doc.save('Update')

            

class _StockController(StockController):
    def make_gl_entries(self, gl_entries=None, from_repost=False):
        if self.docstatus == 2:
            make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

        provisional_accounting_for_non_stock_items = \
            cint(frappe.db.get_value('Company', self.company, 'enable_provisional_accounting_for_non_stock_items'))

        if cint(erpnext.is_perpetual_inventory_enabled(self.company)) or provisional_accounting_for_non_stock_items:
            warehouse_account = get_warehouse_account_map(self.company)

            if self.docstatus==1:
                if not gl_entries:
                    gl_entries = self.get_gl_entries(warehouse_account)
                make_gl_entries(gl_entries, from_repost=from_repost)

        elif self.doctype in ['Purchase Receipt', 'Purchase Invoice'] and self.docstatus == 1:
            gl_entries = []
            gl_entries = self.get_asset_gl_entry(gl_entries)
            make_gl_entries(gl_entries, from_repost=from_repost)
            
    def get_gl_entries(self, warehouse_account=None, default_expense_account=None,
        default_cost_center=None):

        if not warehouse_account:
            warehouse_account = get_warehouse_account_map(self.company)

        sle_map = self.get_stock_ledger_details()
        voucher_details = self.get_voucher_details(default_expense_account, default_cost_center, sle_map)

        gl_list = []
        warehouse_with_no_account = []
        precision = self.get_debit_field_precision()
        for item_row in voucher_details:

            sle_list = sle_map.get(item_row.name)
            if sle_list:
                for sle in sle_list:
                    if warehouse_account.get(sle.warehouse):
                        # from warehouse account

                        self.check_expense_account(item_row)

                        # expense account/ target_warehouse / source_warehouse
                        if item_row.get('target_warehouse'):
                            warehouse = item_row.get('target_warehouse')
                            expense_account = warehouse_account[warehouse]["account"]
                        else:
                            expense_account = item_row.expense_account

                        gl_list.append(self.get_gl_dict({
                            "internal_fuel_consumption": self.get("internal_fuel_consumption"), # Customization
                            "vehicle": item_row.get("vehicle"), # Customization
                            "expense_type": item_row.get("expense_type"), # Customization
                            "paver": item_row.get("paver"), # Customization
                            "is_shot_blast": item_row.get("is_shot_blast"), # Customization
                            "compound_wall": item_row.get("compound_wall"), # Customization
                            "fencing_post": item_row.get("fencing_post"), # Customization
                            "lego_block": item_row.get("lego_block"), # Customization
                            "from_date": item_row.get("from_date"), # Customization
                            "to_date": item_row.get("to_date"), # Customization
                            "split_equally": item_row.get("split_equally"), # Customization
                            "account": warehouse_account[sle.warehouse]["account"],
                            "against": expense_account,
                            "cost_center": item_row.cost_center,
                            "project": self.get("site_work") or item_row.project or self.get('project'),
                            "remarks": self.get("remarks") or _("Accounting Entry for Stock"),
                            "debit": flt(sle.stock_value_difference, precision),
                            "is_opening": item_row.get("is_opening") or self.get("is_opening") or "No",
                        }, warehouse_account[sle.warehouse]["account_currency"], item=item_row))

                        gl_list.append(self.get_gl_dict({
                            "internal_fuel_consumption": self.get("internal_fuel_consumption"), # Customization
                            "vehicle": item_row.get("vehicle"), # Customization
                            "expense_type": item_row.get("expense_type"), # Customization
                            "paver": item_row.get("paver"), # Customization
                            "is_shot_blast": item_row.get("is_shot_blast"), # Customization
                            "compound_wall": item_row.get("compound_wall"), # Customization
                            "fencing_post": item_row.get("fencing_post"), # Customization
                            "lego_block": item_row.get("lego_block"), # Customization
                            "from_date": item_row.get("from_date"), # Customization
                            "to_date": item_row.get("to_date"), # Customization
                            "split_equally": item_row.get("split_equally"), # Customization
                            "account": expense_account,
                            "against": warehouse_account[sle.warehouse]["account"],
                            "cost_center": item_row.cost_center,
                            "remarks": self.get("remarks") or _("Accounting Entry for Stock"),
                            "credit": flt(sle.stock_value_difference, precision),
                            "project": self.get("site_work") or item_row.get("project") or self.get("project"),
                            "is_opening": item_row.get("is_opening") or self.get("is_opening") or "No"
                        }, item=item_row))
                        # Customization start
                        for wrk in get_workstations():
                            for gl_dict in gl_list: 
                                gl_dict.update({
                                    wrk: item_row.get(wrk)
                                })
                        # Customization end

                    elif sle.warehouse not in warehouse_with_no_account:
                        warehouse_with_no_account.append(sle.warehouse)

        if warehouse_with_no_account:
            for wh in warehouse_with_no_account:
                if frappe.db.get_value("Warehouse", wh, "company"):
                    frappe.throw(_("Warehouse {0} is not linked to any account, please mention the account in the warehouse record or set default inventory account in company {1}.").format(wh, self.company))

        return process_gl_map(gl_list, precision=precision)

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

def merge_similar_entries(gl_map, precision=None):
    merged_gl_map = []
    accounting_dimensions = get_accounting_dimensions()
    for entry in gl_map:
        # if there is already an entry in this account then just add it
        # to that entry
        same_head = check_if_in_list(entry, merged_gl_map, accounting_dimensions + ["vehicle", "expense_type", "paver", "is_shot_blast", "compound_wall", "fencing_post", "lego_block", "from_date", "to_date", "split_equally"] + get_workstations())
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

class Tsstockentry(StockEntry, _StockController):
    def get_gl_entries(self, warehouse_account):
        gl_entries = super(StockEntry, self).get_gl_entries(warehouse_account)

        if self.purpose in ("Repack", "Manufacture"):
            total_basic_amount = sum(flt(t.basic_amount) for t in self.get("items") if t.is_finished_item)
        else:
            total_basic_amount = sum(flt(t.basic_amount) for t in self.get("items") if t.t_warehouse)

        divide_based_on = total_basic_amount

        if self.get("additional_costs") and not total_basic_amount:
            # if total_basic_amount is 0, distribute additional charges based on qty
            divide_based_on = sum(item.qty for item in list(self.get("items")))

        item_account_wise_additional_cost = {}

        for t in self.get("additional_costs"):
            for d in self.get("items"):
                if self.purpose in ("Repack", "Manufacture") and not d.is_finished_item:
                    continue
                elif not d.t_warehouse:
                    continue

                item_account_wise_additional_cost.setdefault((d.item_code, d.name), {})
                item_account_wise_additional_cost[(d.item_code, d.name)].setdefault(t.expense_account, {
                    "amount": 0.0,
                    "base_amount": 0.0
                })

                multiply_based_on = d.basic_amount if total_basic_amount else d.qty

                item_account_wise_additional_cost[(d.item_code, d.name)][t.expense_account]["amount"] += \
                    flt(t.amount * multiply_based_on) / divide_based_on

                item_account_wise_additional_cost[(d.item_code, d.name)][t.expense_account]["base_amount"] += \
                    flt(t.base_amount * multiply_based_on) / divide_based_on

        if item_account_wise_additional_cost:
            for d in self.get("items"):
                for account, amount in iteritems(item_account_wise_additional_cost.get((d.item_code, d.name), {})):
                    if not amount: continue

                    gl_entries.append(self.get_gl_dict({
                        "account": account,
                        "against": d.expense_account,
                        "cost_center": d.cost_center,
                        "remarks": self.get("remarks") or _("Accounting Entry for Stock"),
                        "credit_in_account_currency": flt(amount["amount"]),
                        "credit": flt(amount["base_amount"])
                    }, item=d))

                    gl_entries.append(self.get_gl_dict({
                        "account": d.expense_account,
                        "against": account,
                        "cost_center": d.cost_center,
                        "remarks": self.get("remarks") or _("Accounting Entry for Stock"),
                        "credit": -1 * amount['base_amount'] # put it as negative credit instead of debit purposefully
                    }, item=d))

        return process_gl_map(gl_entries)
    
    def set_basic_rate(self, reset_outgoing_rate=True, raise_error_if_no_rate=True):
           # Set rate for outgoing items
            outgoing_items_cost = self.set_rate_for_outgoing_items(
                reset_outgoing_rate, raise_error_if_no_rate
            )
            finished_item_qty = sum(
                d.transfer_qty for d in self.items if d.is_finished_item or d.is_process_loss
            )

            # Set basic rate for incoming items
            for d in self.get("items"):
                if d.s_warehouse or d.set_basic_rate_manually:
                    continue

                if d.allow_zero_valuation_rate:
                    d.basic_rate = 0.0
                elif d.is_finished_item:
                    if self.purpose == "Manufacture":
                        d.basic_rate = self.get_basic_rate_for_manufactured_item(
                            finished_item_qty, outgoing_items_cost
                        )
                    elif self.purpose == "Repack":
                        d.basic_rate = self.get_basic_rate_for_repacked_items(d.transfer_qty, outgoing_items_cost)

                if not d.basic_rate and not d.allow_zero_valuation_rate:
                    d.basic_rate = get_valuation_rate(
                        d.item_code,
                        d.t_warehouse,
                        self.doctype,
                        self.name,
                        d.allow_zero_valuation_rate,
                        currency=erpnext.get_company_currency(self.company),
                        company=self.company,
                        raise_error_if_no_rate=raise_error_if_no_rate,
                    )

                # do not round off basic rate to avoid precision loss
                d.basic_rate = flt(d.basic_rate)
                if d.is_process_loss:
                    d.basic_rate = flt(0.0)
                d.basic_amount = flt(flt(d.transfer_qty) * flt(d.basic_rate), d.precision("basic_amount"))
         #start
            if self.get("usb"):
                for i in self.items:
                    rate = frappe.get_value("BOM Item", {'parenttype': 'Material Manufacturing', 'parent':self.usb, 'item_code':i.item_code}, 'rate') or 0
                    if(rate):
                        i.basic_rate = rate
                        i.basic_amount = rate * i.transfer_qty
                return
            #End


def basic_rate_validation(doc,event):
    if doc.site_work:
        doc.project=doc.site_work
    if(doc.usb or doc.cw_usb or doc.shot_blast or doc.shot_blast_costing):
        for item in doc.items:
            admin_exp = frappe.db.get_value("Item", item.item_code, "administrative_cost") or 0
            
            if (item.basic_rate_hidden and item.conversion_factor):
                item.basic_rate = item.basic_rate_hidden/(item.conversion_factor)
                item.valuation_rate = item.basic_rate_hidden/(item.conversion_factor)
            
            if admin_exp:
                item.basic_rate = (item.basic_rate or 0) + (admin_exp or 0)
                item.valuation_rate = (item.basic_rate or 0)

def expense_account(self, event = None):
    """
        Set Internal Fuel Consumtion expense account
    """
    default_acc = None
    for row in self.items:
        if row.item_group == "Fuel":
            if not default_acc:
                default_acc = frappe.db.get_value("Company", self.company, "default_internal_fuel_consumption_account")
                if not default_acc:
                    frappe.throw(f"""
                        Please set <b>Default Internal Fuel Consumption Account</b> in Company <a href="/app/company/{self.company}"><b>{self.company}</b></a>
                    """)
                row.expense_account = default_acc

# general ledger functions

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


def remove_additional_cost(self,event):
    sites = frappe.get_all("Project", filters = [
        ["Additional Costs", "stock_entry", "=", self.name]
        ], pluck="name")
    if sites:
        for site in sites:
            sw_doc=frappe.get_doc("Project", site)
            add_costs=[]
            for row in sw_doc.additional_cost:
                if row.stock_entry != self.name:
                    add_costs.append(row)
            sw_doc.update({
                "additional_cost": add_costs 
            })
            sw_doc.save()
    
    return

def add_additional_cost(self,event):
    if self.internal_fuel_consumption and self.site_work:
        sw_doc=frappe.get_doc("Project",self.site_work)
        total_qty=0
        for i in self.items:
            total_qty += i.qty

        sw_doc.append("additional_cost", {
            "description": self.internal_fuel_consumption,
            "qty": total_qty,
            "nos":total_qty,
            "amount": self.total_outgoing_value,
            "stock_entry":self.name
            
        })
        sw_doc.save()
