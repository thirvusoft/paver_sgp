import json
import frappe
import erpnext
from erpnext.accounts.utils import get_children
from ganapathy_pavers.custom.py.journal_entry import get_production_details

machine_wise_prod_info = {}
WORKSTATIONS = frappe.get_all("Workstation", {"used_in_expense_splitup": 1}, pluck="name")


def filter_empty(gl_entries):
    res = []

    for acc in gl_entries:
        if acc.get("expandable"):
            acc["child_nodes"] = filter_empty(acc.get("child_nodes") or [])
            if acc["child_nodes"]:
                res.append(acc)
        else:
            if acc.get("balance"):
                res.append(acc)

    return res

def flatten_hierarchy(gl_entries):
    if len(gl_entries)==1:
        if len(gl_entries[0]['child_nodes'])==1:
            gl_entries = flatten_hierarchy(gl_entries[0]['child_nodes'])
        elif len(gl_entries[0]['child_nodes'])>1:
            gl_entries=gl_entries[0]['child_nodes']
        
    return gl_entries

@frappe.whitelist()
def total_expense(*args, **_args):
    res = expense_tree(*args, **_args)
    return calculate_total(res)

def calculate_total(gl_entries):
    res = 0

    for acc in gl_entries:
        if acc.get("expandable"):
            res += (calculate_total(acc.get("child_nodes") or []) or 0)
        else:
            if acc.get("balance"):
                res += (acc.get("balance") or 0)
    return res

@frappe.whitelist()
def expense_tree(from_date, to_date, company=erpnext.get_default_company(), parent = "", doctype='Account', vehicle=None, machine=[], expense_type=None, prod_details = "", filter_unwanted_groups=True) -> list:
    if isinstance(prod_details, list):
        if prod_details:
            prod_details=prod_details[0]
        else:
            prod_details=""
    if not machine:
        machine=[]
    if not parent:
        parent=frappe.db.get_all("Account", {"root_type": "Expense", "parent_account":["is", "not set"], "is_group": 1, "company": company}, pluck="name")
        if parent:
            parent=parent[0]
        else:
            parent=None

    prod_details = frappe.scrub(prod_details)
    root = get_account_balances(
                accounts=get_children(
                            doctype=doctype, 
                            parent=parent or company, 
                            company=company), 
                company=company, 
                from_date=from_date, 
                to_date=to_date, 
                vehicle=vehicle, 
                machine=machine, 
                expense_type=expense_type, 
                prod_details=prod_details)
    
    res = get_tree(
            root=root, 
            company=company, 
            from_date=from_date, 
            to_date=to_date, 
            vehicle=vehicle, 
            machine=machine, 
            expense_type=expense_type, 
            prod_details=prod_details
            )
    
    res = filter_empty(res)

    if filter_unwanted_groups:
        res = flatten_hierarchy(res)

    return res

def get_tree(root, company, from_date, to_date, vehicle=None, machine=[], expense_type=None, prod_details = ""):
        for i in root:
            child = get_tree(
                        root=get_children(
                                doctype='Account',
                                parent=i.value,
                                company=company
                                ), 
                        company=company, 
                        from_date=from_date, 
                        to_date=to_date, 
                        vehicle=vehicle, 
                        machine=machine, 
                        expense_type=expense_type, 
                        prod_details=prod_details)
            i['child_nodes']=get_account_balances(
                                accounts=child, 
                                company=company, 
                                from_date=from_date, 
                                to_date=to_date, 
                                vehicle=vehicle, 
                                machine=machine, 
                                expense_type=expense_type, 
                                prod_details=prod_details
                                )
        return root

def get_account_balances(accounts, company, from_date, to_date, vehicle=None, machine=[], expense_type=None, prod_details = ""):
    for account in accounts:
        account['account_name'] = frappe.db.get_value("Account", account["value"], "account_name")
        account = get_account_balance_on(
                                account=account, 
                                company=company, 
                                from_date=from_date, 
                                to_date=to_date, 
                                vehicle=vehicle, 
                                machine=machine, 
                                expense_type=expense_type, 
                                prod_details=prod_details
                                )
        
    return accounts

def get_account_balance_on(account, company, from_date, to_date, vehicle=None, machine=[], expense_type=None, prod_details = ""):
    if(account.get('expandable')):
        account['balance'] = 0
        account["references"] = []
        return account
    conditions=""

    if prod_details:
        conditions+=f""" and (gl.{frappe.scrub(prod_details)}=1
        or (gl.paver=0 and gl.compound_wall=0 and gl.lego_block=0 and gl.fencing_post=0) 
        or (gl.paver=1 and gl.compound_wall=1 and gl.lego_block=1 and gl.fencing_post=1)) """

    if expense_type:
        conditions+=f" and gl.expense_type='{expense_type}'"

    if vehicle:
        conditions+=f" and IFNULL(gl.vehicle, '')!='' and gl.vehicle='{vehicle}'"
    if machine and sorted(machine)!=sorted(WORKSTATIONS):
        conditions+=f"""  AND
            (
                ({" OR ".join([
                    f''' IFNULL(gl.{frappe.scrub(macn)}, 0) '''
                for macn in machine])}
                ) OR
                ({" AND ".join([
                    f''' IFNULL(gl.{frappe.scrub(wrk)}, 0)=0 '''
                for wrk in WORKSTATIONS ])})
                 OR
                ({" AND ".join([
                    f''' IFNULL(gl.{frappe.scrub(wrk)}, 0)=1 '''
                for wrk in WORKSTATIONS ])})
            )
        """
    gl_vehicles = []

    if expense_type == "Manufacturing":
        gl_vehicles = frappe.db.sql(f"""
            select
                DISTINCT(gl.vehicle)
            from `tabGL Entry` gl
            where
                gl.company='{company}' and
                CASE
                    WHEN IFNULL(gl.from_date, "")!="" and IFNULL(gl.to_date, "")!=""
                    THEN (
                        (gl.from_date BETWEEN '{from_date}' AND '{to_date}' OR gl.to_date BETWEEN '{from_date}' AND '{to_date}')
                        OR ('{from_date}' BETWEEN gl.from_date AND gl.to_date OR '{to_date}' BETWEEN gl.from_date AND gl.to_date)
                    )
                    ELSE (date(gl.posting_date)>='{from_date}' and
                        date(gl.posting_date)<='{to_date}')
                    END and
                gl.is_cancelled=0
                and gl.account="{account['value']}"
                {conditions}
                ORDER BY gl.vehicle
        """, as_list=True)

    if gl_vehicles and gl_vehicles[0] and gl_vehicles[0][0]:
        # get vehicle wise expense for each account
        gl_veh_accounts=[]
        for veh in gl_vehicles:
            veh=veh[0]
            
            query=f"""
                    select
                        *,
                        CASE
                            WHEN IFNULL(gl.from_date, "")!="" and IFNULL(gl.to_date, "")!=""
                                THEN gl.debit/
                                TIMESTAMPDIFF(DAY, gl.from_date ,  DATE_ADD(gl.to_date, INTERVAL 1 DAY))*
                                DATEDIFF(DATE_ADD(LEAST('{to_date}', gl.to_date), INTERVAL 1 DAY), GREATEST('{from_date}', gl.from_date))
                            ELSE gl.debit
                        END as debit
                    from `tabGL Entry` gl
                    where
                        gl.company='{company}' and
                        CASE
                            WHEN IFNULL(gl.from_date, "")!="" and IFNULL(gl.to_date, "")!=""
                            THEN (
                                (gl.from_date BETWEEN '{from_date}' AND '{to_date}' OR gl.to_date BETWEEN '{from_date}' AND '{to_date}')
                                OR ('{from_date}' BETWEEN gl.from_date AND gl.to_date OR '{to_date}' BETWEEN gl.from_date AND gl.to_date)
                            )
                            ELSE (date(gl.posting_date)>='{from_date}' and
                                date(gl.posting_date)<='{to_date}')
                            END and
                        gl.is_cancelled=0
                        and gl.account="{account['value']}"
                        {conditions}
                        and gl.vehicle='{veh}'
                """


            gl_entries=frappe.db.sql(query, as_dict=True)
            
            balance, references = calculate_exp_from_gl_entries(
                gl_entries=gl_entries,
                from_date=from_date,
                to_date=to_date,
                expense_type=expense_type,
                prod_details=prod_details,
                machines=machine
                )
            gl_veh_accounts.append({
                    "value": f"""{veh} {account["value"]}""",
                    "expandable": 0,
                    "root_type": account["root_type"],
                    "account_currency": account["account_currency"],
                    "parent": account['value'],
                    "child_nodes": [],
                    "balance": balance,
                    "references": references,
                    "account_name": f"""{veh} {account["account_name"]}"""
                })
            
        account['balance']=0
        account["expandable"]=1
        account["references"] = []
        account["child_nodes"] = gl_veh_accounts

        return account
    
    query=f"""
        select
            *,
            CASE
                WHEN IFNULL(gl.from_date, "")!="" and IFNULL(gl.to_date, "")!=""
                    THEN gl.debit/
                    TIMESTAMPDIFF(DAY, gl.from_date ,  DATE_ADD(gl.to_date, INTERVAL 1 DAY))*
                    DATEDIFF(DATE_ADD(LEAST('{to_date}', gl.to_date), INTERVAL 1 DAY), GREATEST('{from_date}', gl.from_date))    
                ELSE gl.debit
            END as debit
        from `tabGL Entry` gl
        where
            gl.company='{company}' and
            CASE
                WHEN IFNULL(gl.from_date, "")!="" and IFNULL(gl.to_date, "")!=""
                THEN (
                    (gl.from_date BETWEEN '{from_date}' AND '{to_date}' OR gl.to_date BETWEEN '{from_date}' AND '{to_date}')
                    OR ('{from_date}' BETWEEN gl.from_date AND gl.to_date OR '{to_date}' BETWEEN gl.from_date AND gl.to_date)
                )
                ELSE (date(gl.posting_date)>='{from_date}' and
                     date(gl.posting_date)<='{to_date}')
                END and
            gl.is_cancelled=0
            and gl.account="{account['value']}"
            {conditions}
    """

    gl_entries=frappe.db.sql(query, as_dict=True)

    balance, references = calculate_exp_from_gl_entries(
        gl_entries=gl_entries,
        from_date=from_date,
        to_date=to_date,
        expense_type=expense_type,
        prod_details=prod_details,
        machines=machine
        )
    account['balance'] = balance or 0
    account["references"] = references or []
    return account

def calculate_exp_from_gl_entries(gl_entries, from_date, to_date, expense_type=None, prod_details="", machines=[]):
    amount = 0
    references = []
    for gl in gl_entries:
        references.append({
            "doctype": gl.voucher_type,
            "docname": gl.voucher_no
        })
        rate = gl.get("debit", 0) or 0
        if expense_type=="Manufacturing":
            prod_sqf = get_gl_production_rate(
                        gl=gl,
                        from_date=from_date,
                        to_date=to_date,
                        prod_details=prod_details,
                        machines=machines
                    )
        else:
            prod_sqf=1
        amount += (rate) * prod_sqf

    return amount, references or []

def get_gl_production_rate(gl, from_date, to_date, prod_details="", machines=[]):
    if not machines:
        machines=WORKSTATIONS
    paver, cw, fp, lego = 0, 0, 0, 0
    if (gl.get("paver") and gl.get("compound_wall") and gl.get("lego_block") and gl.get("fencing_post")):
        paver, cw, fp, lego = 1, 1, 1 ,1
    elif ( (not gl.get("paver")) and (not  gl.get("compound_wall")) and (not  gl.get("lego_block")) and (not  gl.get("fencing_post"))):
        paver, cw, fp, lego = 1, 1, 1 ,1
    else:
        if gl.get("paver"):
            paver = 1
        if gl.get("compound_wall"):
            cw = 1
        if gl.get("lego_block"):
            lego = 1
        if gl.get("fencing_post"):
            fp = 1
    
    gl_machines=[]
    for wrk in WORKSTATIONS:
        if frappe.scrub(wrk) in gl and gl.get(frappe.scrub(wrk)):
            gl_machines.append(wrk)

    gl_machines.sort()

    
    machines=sorted([i for i in machines if ((i in gl_machines) or not gl_machines)])
    if gl_machines==sorted(WORKSTATIONS):  
        # If all machines, then make it [], to get all machines prod_details
        gl_machines=[]

    gl_machine_key = json.dumps(gl_machines)
    machine_key = json.dumps(machines)

    if gl_machine_key not in machine_wise_prod_info:
        machine_wise_prod_info[gl_machine_key] = get_production_details(from_date=from_date, to_date=to_date, machines=gl_machines)
    if machine_key not in machine_wise_prod_info:
        machine_wise_prod_info[machine_key] = get_production_details(from_date=from_date, to_date=to_date, machines=machines)

    num_total = machine_wise_prod_info[machine_key].get({"paver": 'paver', "compound_wall": 'cw', "lego_block": "lego", "fencing_post": "fp"}.get(prod_details)) or 0
    den_total = sum([(machine_wise_prod_info[gl_machine_key][i] or 0) for i in machine_wise_prod_info[gl_machine_key] if {'paver': paver, 'cw': cw, "lego": lego, "fp": fp}.get(i) ])

    return (num_total or 0) / (den_total or 1)
