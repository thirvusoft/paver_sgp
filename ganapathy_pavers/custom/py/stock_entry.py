from ganapathy_pavers.custom.py.journal_entry_override import get_workstations
import erpnext
from erpnext.accounts.general_ledger import process_gl_map
from erpnext.controllers.stock_controller import StockController
from erpnext.stock import get_warehouse_account_map
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
from erpnext.stock.stock_ledger import get_valuation_rate
import frappe
from frappe import _
from frappe.utils.data import flt
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

class Tsstockentry(StockEntry, _StockController):
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
    if(doc.usb or doc.cw_usb):
        for item in doc.items:
            if (item.basic_rate_hidden and item.conversion_factor):
                item.basic_rate = item.basic_rate_hidden/(item.conversion_factor)
                item.valuation_rate = item.basic_rate_hidden/(item.conversion_factor)

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
