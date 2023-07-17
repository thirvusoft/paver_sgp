import frappe
import json
from datetime import datetime
from ganapathy_pavers import uom_conversion
from dateutil.relativedelta import relativedelta
from frappe.utils import add_days


def journal_entry(self, event):
    for i in self.accounts:
        if i.party and i.party_type and i.party_type!="Employee":
            if i.party_type:
                address=frappe.get_value(i.party_type, i.party,"primary_address")
                self.party_address=address
            self.party_name=i.party
            break

@frappe.whitelist()
def get_production_details(date=None, from_date=None, to_date=None, machines=[], item=None, paver_type=None):
    if not machines:
        machines = []
    res={'month': '', 'paver': 0, 'cw': 0, 'lego': 0, 'fp': 0}
    try:
        if (isinstance(machines, str)):
            try:
                machines=json.loads(machines)
            except:
                machines=[]
        if date and not from_date and not to_date:
            date=datetime.strptime(date, "%Y-%m-%d")
            to_date=date+relativedelta(day=1, months=+1, days=-1)
            from_date=date+relativedelta(day=1)
            res['month']=date.strftime("%B")
        cw_filt = {'docstatus':['!=', 2], 'type': ['in', ['Post', 'Slab']]}
        lg_filt ={'docstatus':['!=', 2], 'type': 'Lego Block'}
        fp_filt ={'docstatus':['!=', 2], 'type': 'Fencing Post'}
        pm_filt = {'docstatus':['!=', 2], "is_sample": 0}
        if(from_date):
            pm_filt['from_time'] = ['>=', add_days(from_date,1)]
            cw_filt['molding_date'] = ['>=', from_date]
            lg_filt['molding_date'] = ['>=', from_date]
            fp_filt['molding_date'] = ['>=', from_date]

        if(to_date):
            pm_filt['to'] = ['<=', add_days(to_date,1)]
            cw_filt['molding_date'] = ['<=', to_date]
            lg_filt['molding_date'] = ['<=', to_date]
            fp_filt['molding_date'] = ['<=', to_date]
        if(from_date and to_date):
            pm_filt['from_time'] = ['between', (from_date, to_date)]
            cw_filt['molding_date'] = ['between', (from_date, to_date)]
            lg_filt['molding_date'] = ['between', (from_date, to_date)]
            fp_filt['molding_date'] = ['between', (from_date, to_date)]
        if(machines):
            pm_filt["work_station"] = ["in", machines]
        
        if paver_type:
            pm_filt["paver_type"] = paver_type

        res['paver'] = sum(frappe.db.get_all('Material Manufacturing', filters=pm_filt, pluck='total_production_sqft'))
        res['cw'] = sum(frappe.db.get_all('CW Manufacturing', filters=cw_filt, pluck='production_sqft'))
        res['lego'] = sum(frappe.db.get_all('CW Manufacturing', filters=lg_filt, pluck='production_sqft'))
        res['fp'] = sum(frappe.db.get_all('CW Manufacturing', filters=fp_filt, pluck='production_sqft'))
    except:
        pass
    return res

@frappe.whitelist()
def get_production_info(date=None, from_date=None, to_date=None):
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
        if row.get("paver", 0) and row.get("paver_account", 0) and float(row.get("paver_amount", 0) or 0):
            com_acc.append({
                "account": row.get("paver_account"),
                "debit": row.get("paver_amount") or 0,
                "vehicle": row.get("vehicle", ""),
            })
            add=False
        if row.get("compound_wall", 0) and row.get("cw_account", 0) and float(row.get("cw_amount", 0) or 0):
            com_acc.append({
                "account": row.get("cw_account"),
                "debit": row.get("cw_amount") or 0,
                "vehicle": row.get("vehicle", ""),
            })
            add=False
        if row.get("lego_block") and row.get("lg_account") and float(row.get("lg_amount", 0) or 0):
            com_acc.append({
                "account": row.get("lg_account"),
                "debit": row.get("lg_amount") or 0,
                "vehicle": row.get("vehicle", ""),
            })
            add=False
        if row.get("fencing_post") and row.get("fp_account") and float(row.get("fp_amount", 0) or 0):
            com_acc.append({
                "account": row.get("fp_account"),
                "debit": row.get("fp_amount") or 0,
                "vehicle": row.get("vehicle", ""),
            })
            add=False
        if add:
            com_acc.append({
                "account": row.get("account"),
                "debit": row.get("debit") or 0,
                "vehicle": row.get("vehicle", ""),
            })
    return com_acc

def site_work_additional_cost(self, event = None):
    if not self.is_site_expense:
        return
    if event=="on_cancel":
        sites = frappe.get_all("Project", filters = [
            ["Additional Costs", "journal_entry", "=", self.name]
            ], pluck="name")
        if sites:
            for site in sites:
                sw_doc=frappe.get_doc("Project", site)
                add_costs=[]
                for row in sw_doc.additional_cost:
                    if row.journal_entry != self.name:
                        add_costs.append(row)
                sw_doc.update({
                    "additional_cost": add_costs 
                })
                sw_doc.save()
        
        return
    
    if not self.site_work:
        return
    
    sw_doc = frappe.get_doc("Project", self.site_work)

    for row in self.accounts:
        if row.debit:
            sw_doc.append("additional_cost", {
                "description": frappe.get_value("Account", row.account, "account_name"),
                "amount": row.debit,
                "journal_entry": self.name,
            })
    sw_doc.save()    
