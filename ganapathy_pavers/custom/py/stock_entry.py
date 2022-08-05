import erpnext
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
from erpnext.stock.stock_ledger import get_valuation_rate
import frappe
from frappe.utils.data import flt

def update_asset(self, event):
    if(self.stock_entry_type=="Manufacture" and self.bom_no and self.fg_completed_qty):
        asset=frappe.get_value('BOM', self.bom_no, 'asset_name')
        if(asset):
            doc=frappe.get_doc('Asset', asset)
            if(event=='on_submit'):
                doc.update({
                    'current_number_of_strokes': float(self.fg_completed_qty)+float(float(doc.current_number_of_strokes) or 0)
                })  
            if(event=='on_cancel'):
                doc.update({
                    'current_number_of_strokes': -float(self.fg_completed_qty)+float(float(doc.current_number_of_strokes) or 0)
                })
            if((float(doc.notification_alert_at or 0)<float(doc.current_number_of_strokes or 0)) and doc.to_notify!=1):
                doc.update({
                    'to_notify': 1
                })
            elif((float(doc.notification_alert_at or 0)>float(doc.current_number_of_strokes or 0)) and doc.to_notify!=0):
                doc.update({
                    'to_notify': 0
                })
            doc.save('Update')

class Tsstockentry(StockEntry):
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
