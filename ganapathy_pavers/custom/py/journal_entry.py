import frappe
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
def get_production_details(date):
    res={'month': '', 'paver': 0, 'cw': 0, 'lego': 0, 'fp': 0}
    try:
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
                sqf=uom_conversion(data['item_code'], data['uom'], data['qty'], 'SQF')
                res['paver']+=(sqf or 0)
            elif item_group=="Compound Walls":
                _type=frappe.db.get_value("Item", data["item_code"], 'compound_wall_type')
                sqf=uom_conversion(data['item_code'], data['uom'], data['qty'], 'SQF')
                if _type in ["Post", "Slab"]:
                    res['cw']+=(sqf or 0)
                elif _type=="Fencing Post":
                    res['fp']+=(sqf or 0)
                elif _type=="Lego Block":
                    res['lego']+=(sqf or 0)
    except:
        pass
    return res

