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
def expense_tree(from_date, to_date, company=erpnext.get_default_company(), parent = "", doctype='Account', vehicle=None, machine=[], expense_type=None, prod_details = []) -> list:
    prod_details = [frappe.scrub(prod) for prod in prod_details]
    root = get_account_balances(get_children(doctype, parent or company, company), company, from_date, to_date, vehicle, machine, expense_type, prod_details)
    return filter_empty(get_tree(root, company, from_date, to_date, vehicle, machine, expense_type, prod_details))

def get_tree(root, company, from_date, to_date, vehicle=None, machine=[], expense_type=None, prod_details = []):
        for i in root:
            child = get_tree(get_children('Account', i.value, company), company, from_date, to_date, vehicle, machine, expense_type, prod_details)
            i['child_nodes']=get_account_balances(child, company, from_date, to_date, vehicle, machine, expense_type, prod_details)
        return root

def get_account_balances(accounts, company, from_date, to_date, vehicle=None, machine=[], expense_type=None, prod_details = []):
    for account in accounts:
        account['balance'] = get_account_balance_on(account, company, from_date, to_date, vehicle, machine, expense_type, prod_details)
        # account['value'] = frappe.db.get_value("Account", account["value"], "account_name")

    return accounts

def get_account_balance_on(account, company, from_date, to_date, vehicle=None, machine=[], expense_type=None, prod_details = []):
    if(account.get('expandable')):
        return 0
    conditions=""

    if prod_details:
        conditions+=f""" and ({" or ".join([f"gl.{frappe.scrub(prod)}=1" for prod in prod_details])} 
        or (gl.paver=0 and gl.compound_wall=0 and gl.lego_block=0 and gl.fencing_post=0) 
        or (gl.paver=1 and gl.compound_wall=1 and gl.lego_block=1 and gl.fencing_post=1)) """

    if expense_type:
        conditions+=f" and gl.expense_type='{expense_type}'"

    if vehicle:
        conditions+=f" and IFNULL(gl.vehicle, '')!='' and gl.vehicle='{vehicle}'"
    if machine and sorted(machine)!=sorted(WORKSTATIONS):
        conditions+=f"""  AND
            ({" OR ".join([
                f''' IFNULL(gl.{frappe.scrub(macn)}, 0) '''
             for macn in machine])})
        """


    query=f"""
        select
            *
        from `tabGL Entry` gl
        where
            gl.company='{company}' and
            date(gl.posting_date)>='{from_date}' and
            date(gl.posting_date)<='{to_date}' and
            gl.is_cancelled=0
            and gl.account="{account['value']}"
            {conditions}
    """

    gl_entries=frappe.db.sql(query, as_dict=True)

    balance = calculate_exp_from_gl_entries(gl_entries, from_date, to_date, prod_details)

    return balance or 0

def calculate_exp_from_gl_entries(gl_entries, from_date, to_date, prod_details=[]):
    amount = 0
    for gl in gl_entries:
        rate = gl.get("debit", 0) or 0
        prod_sqf = get_gl_production_rate(gl, from_date, to_date, prod_details)
        amount += (rate) * prod_sqf

    return amount

def get_gl_production_rate(gl, from_date, to_date, prod_details=[]):
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
    
    machines=[]
    for wrk in WORKSTATIONS:
        if frappe.scrub(wrk) in gl and gl.get(frappe.scrub(wrk)):
            machines.append(wrk)

    machines.sort()

    if machines==sorted(WORKSTATIONS):  # If all machines are true then make it [], to get all machines prod_details
        machines=[]

    machine_key = json.dumps(machines)

    if machine_key not in machine_wise_prod_info:
        machine_wise_prod_info[machine_key] = get_production_details(from_date=from_date, to_date=to_date, machines=machines)
    
    num_total = sum([(machine_wise_prod_info[machine_key][i] or 0) for i in machine_wise_prod_info[machine_key] if ({'paver': "paver", 'cw': "compound_wall", "lego": "lego_block", "fp": "fencing_post"}.get(i) in prod_details)])
    den_total = sum([(machine_wise_prod_info[machine_key][i] or 0) for i in machine_wise_prod_info[machine_key] if {'paver': paver, 'cw': cw, "lego": lego, "fp": fp}.get(i) ])
    
    return (num_total or 0) / (den_total or 1)



month_start = "2023-03-01"
month_end = "2023-03-31"
def a(_type):
    res = expense_tree(
        month_start,
        month_end,
        parent="Expenses - GP",
        prod_details=["Paver"],
        expense_type="Manufacturing",
        # machine = ["Machine1", "Machine2"]
    )
    # print(
    #     res,
        # total_expense(month_start,
        # month_end,
        # parent="Expenses - GP",
        # prod_details=[_type],
        # expense_type="Manufacturing",
        # # machine = ["Machine1", "Machine2"]
        # )
        # )


# paver production report
"""
	from ganapathy_pavers.custom.py.expense import  expense_tree

	exp_tree=expense_tree(
		from_date=filters.get('from_date'),
        to_date=filters.get('to_date'),
        parent="Expenses - GP",
        prod_details=["Paver"],
        expense_type="Manufacturing",
		machine = machine
	)
	
""" 