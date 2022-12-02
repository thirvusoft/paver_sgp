import frappe
import json
from datetime import datetime
from ganapathy_pavers import uom_conversion
from frappe.utils.data import getdate
from dateutil.relativedelta import relativedelta


def journal_entry(self, event):
    for i in self.accounts:
        if i.party and i.party_type :
            if i.party_type:
                address=frappe.get_value(i.party_type, i.party,"primary_address")
                self.party_address=address
            self.party_name=i.party
            break

@frappe.whitelist()
def get_production_details(date=None, from_date=None, to_date=None):
    res={'month': '', 'paver': 0, 'cw': 0, 'lego': 0, 'fp': 0}
    try:
        exp=frappe.get_single("Expense Accounts")
        paver_uom, cw_uom, lg_uom, fp_uom = exp.paver_uom, exp.cw_uom, exp.lg_uom, exp.fp_uom
        if date and not from_date and not to_date:
            date=datetime.strptime(date, "%Y-%m-%d")
            to_date=date+relativedelta(day=1, months=+1, days=-1)
            from_date=date+relativedelta(day=1)
            res['month']=date.strftime("%B")
        query=f"""
            select sed.item_code, sum(sed.transfer_qty) as qty, sed.stock_uom as uom from `tabStock Entry Detail` as sed 
            left outer join `tabStock Entry` as se on se.name=sed.parent where se.docstatus=1 and 
            se.stock_entry_type='Manufacture' and sed.is_finished_item=1 and
            se.posting_date >= "{from_date}" and se.posting_date <= "{to_date}"
            group by sed.item_code, sed.uom;

        """
        query_res=frappe.db.sql(query, as_dict=True)
        for data in query_res:
            item_group=frappe.db.get_value("Item", data['item_code'], 'item_group')
            if item_group=="Pavers":
                if paver_uom:
                    sqf=uom_conversion(data['item_code'], data['uom'], data['qty'], paver_uom)
                    res['paver']+=(sqf or 0)
            elif item_group=="Compound Walls":
                _type=frappe.db.get_value("Item", data["item_code"], 'compound_wall_type')
                if _type in ["Post", "Slab"]:
                    if cw_uom:
                        sqf=uom_conversion(data['item_code'], data['uom'], data['qty'], cw_uom)
                        res['cw']+=(sqf or 0)
                elif _type=="Fencing Post":
                    if fp_uom:
                        sqf=uom_conversion(data['item_code'], data['uom'], data['qty'], fp_uom)
                        res['cw']+=(sqf or 0)
                elif _type=="Lego Block":
                    if lg_uom:
                        sqf=uom_conversion(data['item_code'], data['uom'], data['qty'], lg_uom)
                        res['cw']+=(sqf or 0)
    except:
        pass
    return res

@frappe.whitelist()
def split_expenses(common_exp):
    common_exp=json.loads(common_exp)
    com_acc=[]
    for row in common_exp:
        add=True
        if row.get("paver") and row.get("paver_account") and float(row.get("paver_amount")):
            com_acc.append({
                "account": row.get("paver_account"),
                "debit": row.get("paver_amount") or 0
            })
            add=False
        if row.get("compound_wall") and row.get("cw_account") and float(row.get("cw_amount")):
            com_acc.append({
                "account": row.get("cw_account"),
                "debit": row.get("cw_amount") or 0
            })
            add=False
        if row.get("lego_block") and row.get("lg_account") and float(row.get("lg_amount")):
            com_acc.append({
                "account": row.get("lg_account"),
                "debit": row.get("lg_amount") or 0
            })
            add=False
        if row.get("fencing_post") and row.get("fp_account") and float(row.get("fp_amount")):
            com_acc.append({
                "account": row.get("fp_account"),
                "debit": row.get("fp_amount") or 0
            })
            add=False
        if add:
            com_acc.append({
                "account": row.get("account"),
                "debit": row.get("debit") or 0
            })
    return com_acc
