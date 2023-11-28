import json
import frappe
import erpnext
from erpnext.accounts.utils import get_children
from ganapathy_pavers.custom.py.journal_entry import get_ITEM_TYPES, get_production_details

machine_wise_prod_info = {}
WORKSTATIONS = frappe.get_all("Workstation", {"used_in_expense_splitup": 1}, pluck="name")
ITEM_TYPES = get_ITEM_TYPES()
ITEM_TYPES_FN = [frappe.scrub(i_type) for i_type in ITEM_TYPES]

VEHICLE_WISE = {}

def filter_empty(gl_entries, vehicle_summary, workstations, group_two_wheeler):
    res = []

    for acc in gl_entries:
        acc["references"] = sorted(acc.get("references") or [], key=lambda x: (x.get("account") or ""))
        if acc.get("vehicle") and vehicle_summary:
            _key = acc.get("vehicle")
            if group_two_wheeler and frappe.db.get_value("Vehicle", acc.get("vehicle"), "wheels") == 2:
                _key = "TWO WHEELER"
                for ref in acc["references"]:
                    ref["title"] = acc.get("vehicle")
            for i in acc['references']:
                    i["account"] = acc.get("account_name")
            if _key not in VEHICLE_WISE:
                _par_acc = acc.copy()
                _par_acc["account_name"] = _par_acc["value"] = _key
                VEHICLE_WISE[_key] = _par_acc
            else:
                for prod in ITEM_TYPES_FN:
                    if not VEHICLE_WISE[_key].get(prod):
                        VEHICLE_WISE[_key][prod] = 0
                    VEHICLE_WISE[_key][prod] += (acc.get(prod) or 0)
                    
                for wrk in WORKSTATIONS:
                    if not VEHICLE_WISE[_key].get(frappe.scrub(wrk)):
                        VEHICLE_WISE[_key][frappe.scrub(frappe.scrub(wrk))] = 0
                    VEHICLE_WISE[_key][frappe.scrub(wrk)] += (acc.get(frappe.scrub(wrk)) or 0)

                VEHICLE_WISE[_key]["balance"] += acc.get("balance") or 0
                VEHICLE_WISE[_key]["references"].extend(acc.get("references") or {})

        elif acc.get("expandable"):
            acc["child_nodes"] = filter_empty(gl_entries=acc.get("child_nodes") or [], vehicle_summary=vehicle_summary, workstations=workstations, group_two_wheeler=group_two_wheeler)
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
def expense_tree(
        from_date,
        to_date, 
        company = None, 
        parent = "", 
        vehicle = None, 
        machine = [], 
        expense_type = None, 
        prod_details = "", 
        filter_unwanted_groups = True, 
        vehicle_summary = False, 
        vehicle_purpose=[], 
        all_expenses=False, 
        with_liability=True, 
        group_two_wheeler=True
    ) -> list:
    
    WORKSTATIONS = frappe.get_all("Workstation", {"used_in_expense_splitup": 1}, pluck="name")
    ITEM_TYPES = get_ITEM_TYPES()
    ITEM_TYPES_FN = [frappe.scrub(i_type) for i_type in ITEM_TYPES]

    if not company:
        company=erpnext.get_default_company()
        
    if isinstance(prod_details, list):
        if prod_details:
            prod_details=prod_details[0]
        else:
            prod_details=""
    if not machine:
        machine=[]
    
    _machine = []
    gl_fields = [r.fieldname for r in frappe.get_meta('GL Entry').fields]
    for mach in machine:
        if frappe.scrub(mach) in gl_fields:
            _machine.append(mach)
    machine = _machine
    if not parent:
        parent=frappe.db.get_all("Account", {"root_type": "Expense", "parent_account":["is", "not set"], "is_group": 1, "company": company}, pluck="name")
        if parent:
            parent=parent[0]
        else:
            parent=None

    prod_details = frappe.scrub(prod_details)

    root = get_account_balances(
                accounts=get_children(
                            doctype='Account', 
                            parent=parent or company, 
                            company=company), 
                company=company, 
                from_date=from_date, 
                to_date=to_date, 
                vehicle=vehicle, 
                machine=machine, 
                expense_type=expense_type, 
                prod_details=prod_details,
                all_expenses=all_expenses
                )
    if with_liability:
        liability_acc=frappe.db.get_all("Account", {"root_type": "Liability", "parent_account":["is", "not set"], "is_group": 1, "company": company}, pluck="name")
        if liability_acc:
            liability_acc=liability_acc[0]
            root += get_account_balances(
                        accounts=get_children(
                                    doctype='Account', 
                                    parent=liability_acc or company, 
                                    company=company), 
                        company=company, 
                        from_date=from_date, 
                        to_date=to_date, 
                        vehicle=vehicle, 
                        machine=machine, 
                        expense_type=expense_type, 
                        prod_details=prod_details,
                        all_expenses=all_expenses
                        )
    
    res = get_tree(
            root=root, 
            company=company, 
            from_date=from_date, 
            to_date=to_date, 
            vehicle=vehicle, 
            machine=machine, 
            expense_type=expense_type, 
            prod_details=prod_details,
            all_expenses=all_expenses
            )

    res.append(get_vehicle_expense_based_on_km(
        from_date=from_date,
        to_date=to_date,
        vehicle=vehicle,
        machine=machine,
        expense_type=expense_type,
        prod_details=prod_details,
        purpose=vehicle_purpose or [],
        all_expenses=all_expenses
        ))
    driver_operator_salary = get_vehicle_driver_operator_salary(
        from_date=from_date,
        to_date=to_date,
        vehicle=vehicle,
        machine=machine,
        expense_type=expense_type,
        prod_details=prod_details,
        purpose=(vehicle_purpose or [])+["Goods Supply", "Raw Material", "Site Visit"],
        driver_employee=None,
        operator_employee=None,
        all_expenses=all_expenses
    )
    res.extend(driver_operator_salary)

    purchase_expense = get_purchase_expense(
        company=company, 
        from_date=from_date, 
        to_date=to_date, 
        vehicle=vehicle, 
        machine=machine, 
        expense_type=expense_type, 
        prod_details=prod_details,
        all_expenses=all_expenses
    )
    res.append({
        "value": "OTHER EXP",
        "account_name": "OTHER EXP",
        "expandable": 1,
        "balance": 0,
        "child_nodes": purchase_expense,
    })

    if expense_type == "Manufacturing":
        per_sqf_exp = per_sqft_production_expense(
            from_date=from_date, 
            to_date=to_date, 
            machines=machine, 
            prod_details=prod_details, 
            all_expenses=all_expenses
        )
        res.append({
            "value": "OTHER EXP",
            "account_name": "OTHER EXP",
            "expandable": 1,
            "child_nodes": per_sqf_exp,
        })

    res = filter_empty(gl_entries=res, vehicle_summary=vehicle_summary, workstations=WORKSTATIONS, group_two_wheeler=group_two_wheeler)

    if filter_unwanted_groups:
        res = flatten_hierarchy(res)
    
    for veh in VEHICLE_WISE:
        VEHICLE_WISE[veh]["references"] = sorted(VEHICLE_WISE[veh].get("references") or [], key=lambda x: x.get("account") or "")

    if VEHICLE_WISE:
        vehicle_accs = {
            "expandable": 1,
            "value": "Vehicle Expenses",
            "account_name": "Vehicle Expenses",
            "child_nodes": sorted(list(VEHICLE_WISE.values()), key = lambda x: x.get("vehicle") or "")
        }
        res.append(vehicle_accs)

    machine_wise_prod_info.clear()
    VEHICLE_WISE.clear()
    WORKSTATIONS.clear()
    ITEM_TYPES_FN.clear()
    return res

def get_tree(root, company, from_date, to_date, vehicle=None, machine=[], expense_type=None, prod_details = "", all_expenses = False):
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
                        prod_details=prod_details,
                        all_expenses=all_expenses
                        )
            i['child_nodes']=get_account_balances(
                                accounts=child, 
                                company=company, 
                                from_date=from_date, 
                                to_date=to_date, 
                                vehicle=vehicle, 
                                machine=machine, 
                                expense_type=expense_type, 
                                prod_details=prod_details,
                                all_expenses=all_expenses
                                )
        return root

def get_account_balances(accounts, company, from_date, to_date, vehicle=None, machine=[], expense_type=None, prod_details = "", all_expenses = False):
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
                                prod_details=prod_details,
                                all_expenses=all_expenses
                                )
        
    return accounts

def get_account_balance_on(account, company, from_date, to_date, expense_name="", vehicle=None, machine=[], expense_type=None, prod_details = "", all_expenses = False):
    if(account.get('expandable')):
        account['balance'] = 0
        account["references"] = []
        account['vehicle'] = ""
        return account
    
    conditions=" and gl.debit>0 "
    account_condition = f""" and gl.account="{account['value']}" """

    if expense_name:
        account_condition = f""" and gl.expense_name="{account['value']}" """
    else:
        conditions+=""" and ifnull(gl.expense_name, "")="" """

    if prod_details:
        conditions+=f""" and (gl.{frappe.scrub(prod_details)}=1
        or ({" and ".join([f'gl.{i_type}=0' for i_type in ITEM_TYPES_FN])})
        or ({" and ".join([f'gl.{i_type}=1' for i_type in ITEM_TYPES_FN])})) """

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
                for wrk in WORKSTATIONS ] + [" 1=1 "])})
                 OR
                ({" AND ".join([
                    f''' IFNULL(gl.{frappe.scrub(wrk)}, 0)=1 '''
                for wrk in WORKSTATIONS ] + [" 1=1 "])})
            )
        """
    gl_vehicles = []

    if expense_type == "Manufacturing" or all_expenses:
        gl_vehicles = frappe.db.sql(f"""
            select
                DISTINCT 
                    gl.vehicle as vehicle,
                    gl.internal_fuel_consumption as internal_fuel_consumption
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
                {account_condition}
                and ifnull(gl.expense_type, "") != ""
                {conditions}
                ORDER BY gl.vehicle, gl.internal_fuel_consumption
        """, as_dict=True)
    
    if gl_vehicles and gl_vehicles[0] and sum([1 for gl_veh in gl_vehicles if gl_veh.get("vehicle") or gl_veh.get("internal_fuel_consumption")]):
        # get vehicle wise expense for each account
        gl_veh_accounts=[]
        for gl_veh in gl_vehicles:
            veh=gl_veh.get("vehicle")
            ifc = gl_veh.get("internal_fuel_consumption")
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
                        {account_condition}
                        and ifnull(gl.expense_type, "") != ""
                        {conditions}
                        and IFNULL(gl.vehicle, "")="{veh or ""}"
                        and IFNULL(gl.internal_fuel_consumption, "")="{ifc or ""}"
                """


            gl_entries=frappe.db.sql(query, as_dict=True)
            
            _account = {
                    "value": f"""{f'''{veh} ''' if veh else ""}{f'''{ifc} ''' if ifc else ""}{account["value"]}""",
                    "expandable": 0,
                    "root_type": account.get("root_type"),
                    "account_currency": account.get("account_currency"),
                    "parent": account.get('value'),
                    "child_nodes": [],
                    "account_name": f"""{account.get("account_name")}""",
                    "vehicle": veh or ifc
                }
            
            _account = calculate_exp_from_gl_entries(
                account=_account,
                gl_entries=gl_entries,
                from_date=from_date,
                to_date=to_date,
                expense_type=expense_type,
                prod_details=prod_details,
                machines=machine,
                all_expenses=all_expenses
                )
            gl_veh_accounts.append(_account)
            
        account['balance']=0
        account["expandable"]=1
        account["references"] = []
        account['vehicle'] = ""
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
                END
            and gl.is_cancelled=0
            and ifnull(gl.expense_type, "") != ""
            {account_condition}
            {conditions}
    """

    gl_entries=frappe.db.sql(query, as_dict=True)

    account = calculate_exp_from_gl_entries(
        account=account,
        gl_entries=gl_entries,
        from_date=from_date,
        to_date=to_date,
        expense_type=expense_type,
        prod_details=prod_details,
        machines=machine,
        all_expenses=all_expenses
        )
    account["vehicle"] = ""
    return account

def calculate_exp_from_gl_entries(account, gl_entries, from_date, to_date, expense_type=None, prod_details="", machines=[], all_expenses=False):
    if all_expenses and expense_type!="Vehicle":
        production_details = {i_type: [] for i_type in ITEM_TYPES_FN}
        
        if "paver" in production_details:
            production_details["paver"] = WORKSTATIONS
            
        for prod in production_details:
            amount = 0
            if not production_details.get(prod):
                for gl in gl_entries:
                    rate = gl.get("debit", 0) or 0
                    if expense_type=="Manufacturing" and prod:
                        prod_sqf = get_gl_production_rate(
                                    gl=gl,
                                    from_date=from_date,
                                    to_date=to_date,
                                    prod_details=prod,
                                    all_expenses=all_expenses
                                )
                    else:
                        prod_sqf=1
                    amount += (rate) * prod_sqf
                    
                account[prod] = amount or 0
            
            else:
                for _machine in production_details.get(prod):
                    amount = 0
                    for gl in gl_entries:
                        rate = gl.get("debit", 0) or 0
                        if expense_type=="Manufacturing" and prod:
                            prod_sqf = get_gl_production_rate(
                                        gl=gl,
                                        from_date=from_date,
                                        to_date=to_date,
                                        prod_details=prod,
                                        machines=[_machine],
                                        all_expenses=all_expenses
                                    )
                        else:
                            prod_sqf=1
                        amount += (rate) * prod_sqf
                        
                    account[frappe.scrub(_machine)] = amount or 0

    amount = 0
    references = []
    for gl in gl_entries:
        rate = gl.get("debit", 0) or 0
        if expense_type=="Manufacturing" and prod_details:
            prod_sqf = get_gl_production_rate(
                        gl=gl,
                        from_date=from_date,
                        to_date=to_date,
                        prod_details=prod_details,
                        machines=machines,
                        all_expenses=all_expenses
                    )
        else:
            prod_sqf=1
        amount += (rate) * prod_sqf
        
        _add = True
        for ref in references:
            if ref.get("doctype") == gl.voucher_type and ref.get("docname") == gl.voucher_no:
                if not ref.get("amount"):
                    ref["amount"] = 0
                ref["amount"] += (rate) * prod_sqf
                _add = False
                break
        if _add:
            references.append({
                'doctype': gl.voucher_type,
                'docname': gl.voucher_no,
                'amount': (rate) * prod_sqf
            })

    account['balance'] = amount or 0
    account["references"] = references or []
    return account

def get_gl_production_rate(gl, from_date, to_date, prod_details="", machines=[], all_expenses=False):
    if not machines:
        machines=WORKSTATIONS
    item_exp = {i_type: 0 for i_type in ITEM_TYPES_FN}
    if sum([1 for i in item_exp if gl.get(i)]) == len(item_exp):
        item_exp = {i_type: 1 for i_type in ITEM_TYPES_FN}
    elif sum([1 for i in item_exp if gl.get(i)]) == 0:
        item_exp = {i_type: 1 for i_type in ITEM_TYPES_FN}
    else:
        item_exp = {i_type: (1 if gl.get(i_type) else 0) for i_type in ITEM_TYPES_FN}
    
    gl_machines=[]
    for wrk in WORKSTATIONS:
        if frappe.scrub(wrk) in gl and gl.get(frappe.scrub(wrk)):
            gl_machines.append(wrk)

    gl_machines.sort()
    machines=sorted([i for i in machines if ((i in gl_machines) or not gl_machines)])

    if all_expenses and ((not gl.get(prod_details) and (sum([gl.get(i) for i in ITEM_TYPES_FN]))) or (prod_details=="paver" and (not machines and gl_machines))):
        return 0
    
    if gl_machines==sorted(WORKSTATIONS):  
        # If all machines, then make it [], to get all machines prod_details
        gl_machines=[]

    gl_machine_key = json.dumps(gl_machines)
    machine_key = json.dumps(machines)

    if gl.get("split_equally"):
        res = 0
        for mach in machines:
            num_total = 1
            den_total = sum([(item_exp.get(i) or 0) for i in item_exp if i!="paver"]) + (len(list(set([frappe.db.get_value("Workstation", mac, "location") for mac in (gl_machines or WORKSTATIONS)]))) if (item_exp.get("paver") or (sum(list(item_exp.values())) == 0)) else 0)
            if prod_details == "paver" and mach:
                gl_m_location = [frappe.db.get_value("Workstation", mac, "location") for mac in (gl_machines or WORKSTATIONS)]
                den_total *= gl_m_location.count(frappe.db.get_value("Workstation", mach, "location"))
            
            res+= (num_total or 0) / (den_total or 1)
            if prod_details != "paver":
                break
        return res

    if gl_machine_key not in machine_wise_prod_info:
        machine_wise_prod_info[gl_machine_key] = get_production_details(from_date=from_date, to_date=to_date, machines=gl_machines, ITEM_TYPES=ITEM_TYPES)
    if machine_key not in machine_wise_prod_info:
        machine_wise_prod_info[machine_key] = get_production_details(from_date=from_date, to_date=to_date, machines=machines, ITEM_TYPES=ITEM_TYPES)

    num_total = machine_wise_prod_info[machine_key].get(prod_details) or 0
    den_total = sum([(machine_wise_prod_info[gl_machine_key][i] or 0) for i in machine_wise_prod_info[gl_machine_key] if item_exp.get(i) ])
    
    return (num_total or 0) / (den_total or 1)

def get_vehicle_expense_based_on_km(from_date, to_date, vehicle = None, machine = [], expense_type = None, prod_details = "", purpose = [], all_expenses=False):
    conditions = ""
    
    if from_date:
        conditions += f""" and date(vl.date)>='{from_date}' """
    if to_date:
        conditions += f""" and date(vl.date)<='{to_date}' """
    if vehicle:
        conditions += f""" and vl.license_plate='{vehicle}' """
    if expense_type:
        conditions += f""" and vl.expense_type='{expense_type}' """
    if prod_details:
        conditions += f""" and vl.{frappe.scrub(prod_details)}=1 """
    
    veh_maint = frappe.db.sql(f"""
        select
            vl.license_plate as vehicle,
            md.maintenance
        from `tabVehicle Log` vl
        inner join `tabMaintenance Details` md on md.parenttype = "Vehicle" and md.parent = vl.license_plate
        inner join `tabVehicle Log Purpose` vlp on vlp.parenttype = "Maintenance type" and vlp.parent = md.maintenance and vlp.parentfield = "vehicle_log_purpose_per_km"
        where 
            vl.docstatus = 1 and
            md.expense_calculation_per_km = 1 and
            {f'''vl.select_purpose in {f"('{purpose[0]}')" if len(purpose)==1 else tuple(purpose)} and ''' if purpose else ""}
            vl.select_purpose = vlp.select_purpose 
            {conditions}
        group by vl.license_plate, md.maintenance
    """, as_dict=True)
    
    if machine and sorted(machine) != sorted(WORKSTATIONS):
        conditions += f""" and ((
                select 
                    count(ts_wrk.workstation) 
                from `tabTS Workstation` ts_wrk 
                WHERE 
                    ts_wrk.parenttype = "Vehicle Log" and 
                    ts_wrk.parent = vl.name and 
                    ts_wrk.workstation in {f"('{machine[0]}')" if len(machine)==1 else tuple(machine)}
            )
             OR
            IFNULL((
                SELECT GROUP_CONCAT(DISTINCT ts_wrk.workstation SEPARATOR ', ') 
                FROM `tabTS Workstation` ts_wrk 
                WHERE 
                    ts_wrk.parenttype = "Vehicle Log" and 
                    ts_wrk.parent = vl.name
                ORDER BY ts_wrk.workstation
            ), "") in ("", "{", ".join(sorted(WORKSTATIONS))}")
            )
        """

    vehicle_accs=[]
    for veh in veh_maint:
        _account={
            "expandable": 0,
            "value": f"{veh.vehicle} {veh.maintenance}",
            "account_name": veh.maintenance,
            "vehicle": veh.vehicle,
            "child_nodes": [],
            "per_km_exp": 1
        }

        _account = get_vehicle_expense(
            account=_account,
            from_date=from_date,
            to_date=to_date,
            vehicle=veh.vehicle,
            machine=machine,
            expense_type=expense_type,
            prod_details=prod_details,
            purpose=purpose or [],
            maintenance=veh.maintenance,
            conditions=conditions,
            all_expenses=all_expenses
            )

        vehicle_accs.append(_account)

    return {
            "expandable": 1,
            "value": f"VEHICLE",
            "account_name": "VEHICLE",
            "balance": 0,
            "references": [],
            "child_nodes": vehicle_accs,
        }

def get_vehicle_expense(account, from_date, to_date, vehicle = None, machine = [], expense_type = None, prod_details = "", purpose = [], maintenance = "", conditions = "", all_expenses = False):
    wrk_fields = ",".join([f""" CASE WHEN (
        SELECT COUNT(ts_wrk.workstation)
        FROM `tabTS Workstation` ts_wrk 
        WHERE ts_wrk.parenttype = "Vehicle Log" and ts_wrk.parent = vl.name and ts_wrk.workstation = '{wrk}'
    ) THEN 1 ELSE 0 END as {frappe.scrub(wrk)}""" for wrk in WORKSTATIONS])

    if vehicle:
        conditions += f""" and vl.license_plate='{vehicle}' """
    if maintenance:
        conditions += f""" and md.maintenance = "{maintenance}" """
    
    query = f"""
        select 
            vl.license_plate as vehicle,
            md.maintenance as account,
            vl.today_odometer_value as distance,
            vl.today_odometer_value * ifnull(md.expense, 0) as debit,
            {
                "".join([f'vl.{i_type}, ' for i_type in ITEM_TYPES_FN])
            }
            "Vehicle Log" as voucher_type,
            vl.name as voucher_no
            {f", {wrk_fields}" if wrk_fields else ""}
        from `tabVehicle Log` vl
        inner join `tabMaintenance Details` md on md.parenttype = "Vehicle" and md.parent = vl.license_plate
        inner join `tabVehicle Log Purpose` vlp on vlp.parenttype = "Maintenance type" and vlp.parent = md.maintenance and vlp.parentfield = "vehicle_log_purpose_per_km"
        where 
            vl.docstatus = 1 and
            md.expense_calculation_per_km = 1 and
            {f'''vl.select_purpose in {f"('{purpose[0]}')" if len(purpose)==1 else tuple(purpose)} and ''' if purpose else ""}
            vl.select_purpose = vlp.select_purpose 
            {conditions}
    """
    
    vl_entries = frappe.db.sql(query, as_dict=True)

    account = calculate_exp_from_gl_entries(
        account=account,
        gl_entries=vl_entries,
        from_date=from_date,
        to_date=to_date,
        expense_type=expense_type,
        prod_details=prod_details,
        machines=machine,
        all_expenses=all_expenses
    )
    return account

def get_vehicle_driver_operator_salary(from_date, to_date, driver_employee=None, operator_employee=None, vehicle = None, machine = [], expense_type = None, prod_details = "", purpose = [], all_expenses = False):
    conditions = ""

    if driver_employee:
        conditions += f""" and vl.employee="{driver_employee}" """
    if operator_employee:
        conditions += f""" and vl.operator="{operator_employee}" """
    if from_date:
        conditions += f""" and vl.date >= "{from_date}" """
    if to_date:
        conditions += f""" and vl.date <= "{to_date}" """
    if vehicle:
        conditions += f""" and vl.license_plate = "{vehicle}" """
    if expense_type:
        conditions += f""" and vl.expense_type = "{expense_type}" """
    if prod_details:
        conditions += f""" and vl.{prod_details} = 1 """
    if purpose:
        conditions += f""" and vl.select_purpose in {f"('{purpose[0]}')" if len(purpose)==1 else tuple(purpose)} """
    if machine and sorted(machine) != sorted(WORKSTATIONS):
        conditions += f""" and 
            ((
                select 
                    count(ts_wrk.workstation) 
                from `tabTS Workstation` ts_wrk 
                WHERE 
                    ts_wrk.parenttype = "Vehicle Log" and 
                    ts_wrk.parent = vl.name and 
                    ts_wrk.workstation in {f"('{machine[0]}')" if len(machine)==1 else tuple(machine)}
            )
             OR
            IFNULL((
                SELECT GROUP_CONCAT(DISTINCT ts_wrk.workstation SEPARATOR ', ') 
                FROM `tabTS Workstation` ts_wrk 
                WHERE 
                    ts_wrk.parenttype = "Vehicle Log" and 
                    ts_wrk.parent = vl.name
                ORDER BY ts_wrk.workstation
                ), "") in ("", "{", ".join(sorted(WORKSTATIONS))}")
            )
        """
        
    wrk_fields = ",".join([f""" CASE WHEN (
        SELECT COUNT(ts_wrk.workstation)
        FROM `tabTS Workstation` ts_wrk 
        WHERE ts_wrk.parenttype = "Vehicle Log" and ts_wrk.parent = vl.name and ts_wrk.workstation = '{wrk}'
    ) THEN 1 ELSE 0 END as {frappe.scrub(wrk)}""" for wrk in WORKSTATIONS])

    veh_details = frappe.db.sql(f"""
        select
            DISTINCT vl.license_plate as vehicle
        from `tabVehicle Log` vl
        where 
            vl.docstatus = 1 
            {conditions}
    """, as_dict=True)

    res = []
    for employee_field in ["employee"]: #["employee", "operator"]:
        vehicle_accs = []
        for veh in veh_details:
            account = {
                "expandable": 0,
                "value": f"""{veh.vehicle} {"DRIVER" if employee_field == "employee" else "OPERATOR" if employee_field == "operator" else ""} SALARY""",
                "account_name": f"""{"DRIVER" if employee_field == "employee" else "OPERATOR" if employee_field == "operator" else ""} SALARY""",
                "vehicle": veh.vehicle,
                "child_nodes": []
            }
            account = get_vehicle_salary(
                account = account,
                from_date=from_date,
                to_date=to_date,
                vehicle=veh.vehicle,
                machine=machine,
                expense_type=expense_type,
                prod_details=prod_details,
                wrk_fields = wrk_fields,
                conditions = conditions,
                employee_field = employee_field,
                all_expenses=all_expenses
            )
            vehicle_accs.append(account)

        res.append({
            "expandable": 1,
            "value": f"""VEHICLE {"DRIVER" if employee_field == "employee" else "OPERATOR" if employee_field == "operator" else ""} SALARY""",
            "account_name": f"""VEHICLE {"DRIVER" if employee_field == "employee" else "OPERATOR" if employee_field == "operator" else ""} SALARY""",
            "balance": 0,
            "references": [],
            "child_nodes": vehicle_accs,
        })
    
    return res

def get_vehicle_salary(account, from_date, to_date, vehicle = None, machine = [], expense_type = None, prod_details = "", wrk_fields = "", conditions = "", employee_field = "employee", all_expenses=False):
    if vehicle:
        conditions += f""" and vl.license_plate = "{vehicle}" """
    
    query = f"""
        SELECT
            vl.license_plate as vehicle,
            "{"Driver" if employee_field == "employee" else "Operator" if employee_field == "operator" else ""} Salary" as account,
            vl.{employee_field} as employee,
            vl.today_odometer_value as distance,
            (
                vl.today_odometer_value/(
                    select sum(_vl.today_odometer_value)
                    from `tabVehicle Log` _vl
                    where 
                        _vl.docstatus = 1 and
                        _vl.{employee_field} = vl.{employee_field} and
                        _vl.date = vl.date and
                        _vl.select_purpose in ("Raw Material", "Goods Supply", "Material Shifting", "Site Visit", "Internal Material Transfer")
                )*ifnull((
                    select drv.salary_per_day
                    from `tabDriver` drv
                    where drv.employee = vl.{employee_field}
                    limit 1
                ), 0)
            ) as debit,
            "Vehicle Log" as voucher_type,
            vl.name as voucher_no,
            {
                ", ".join([f'vl.{i_type}' for i_type in ITEM_TYPES_FN])
            }
            {f", {wrk_fields}" if wrk_fields else ""}
        FROM `tabVehicle Log` vl
        WHERE
            vl.docstatus = 1
            {conditions}
        
    """   
    
    vl_entries = frappe.db.sql(query, as_dict=True)
    account = calculate_exp_from_gl_entries(
        account=account,
        gl_entries=vl_entries,
        from_date=from_date,
        to_date=to_date,
        expense_type=expense_type,
        prod_details=prod_details,
        machines=machine,
        all_expenses=all_expenses
    )

    return account

def expense_map(expense):
    return {
        "value": expense,
        "balance": 0,
        "account_name": expense,
        "expandable": 0,
        "child_nodes": [],
        "root_type": "",
        "parent": "OTHER EXP"
    }

def get_purchase_expense(company, from_date, to_date, vehicle=None, machine=[], expense_type=None, prod_details = "", all_expenses = False):
    expense_names = list(set(frappe.get_all("GL Entry", filters={"expense_name": ["is", "set"], "is_cancelled": 0}, pluck="expense_name")))
    accounts = list(map(expense_map, expense_names))
    res = get_purchase_account_balances(
                accounts=accounts,
                company=company, 
                from_date=from_date, 
                to_date=to_date, 
                vehicle=vehicle, 
                machine=machine, 
                expense_type=expense_type, 
                prod_details=prod_details,
                all_expenses=all_expenses
                )
    return res

def get_purchase_account_balances(accounts, company, from_date, to_date, vehicle=None, machine=[], expense_type=None, prod_details = "", all_expenses = False):
    for account in accounts:
        account['account_name'] = account["value"]
        account = get_account_balance_on(
                                account=account, 
                                expense_name=account['value'],
                                company=company, 
                                from_date=from_date, 
                                to_date=to_date, 
                                vehicle=vehicle, 
                                machine=machine, 
                                expense_type=expense_type, 
                                prod_details=prod_details,
                                all_expenses=all_expenses
                                )
        
    return accounts

def per_sqft_production_expense(from_date, to_date, machines, prod_details, all_expenses=False):
    conditions = ""
    WORKSTATIONS = frappe.get_all("Workstation", {"used_in_expense_splitup": 1}, pluck="name")
    
    if not machines:
        machines = WORKSTATIONS

    if prod_details:
        conditions+=f""" and (exp.{frappe.scrub(prod_details)}=1
        or ({" and ".join([f'exp.{i_type}=0' for i_type in ITEM_TYPES_FN])}) 
        or ({" and ".join([f'exp.{i_type}=1' for i_type in ITEM_TYPES_FN])})) """

    if machines and sorted(machines)!=sorted(WORKSTATIONS):
        conditions+=f"""  AND
            (
                ({" OR ".join([
                    f''' IFNULL(exp.{frappe.scrub(macn)}, 0) '''
                for macn in machines])}
                ) OR
                ({" AND ".join([
                    f''' IFNULL(exp.{frappe.scrub(wrk)}, 0)=0 '''
                for wrk in WORKSTATIONS ] + [" 1=1 "])})
                OR
                ({" AND ".join([
                    f''' IFNULL(exp.{frappe.scrub(wrk)}, 0)=1 '''
                for wrk in WORKSTATIONS ] + [" 1=1 "])})
            )
        """

    query = f"""
        select
            DISTINCT exp.expense_name
        from `tabProduction Expense Table` exp
        where
            exp.parenttype="Production Expense"
            and exp.parent="Production Expense"
            {conditions}
    """

    res = []
    entries = frappe.db.sql(query, as_dict=True)
    for row in entries:
        exp_child = {
            "value": row.expense_name,
            "account_name": row.expense_name,
            "child_nodes": [],
            "parent": "OTHER EXP",
            "expandable": 0,
            "balance": 0
        }
        if all_expenses:
            exp = {i_type: [] for i_type in ITEM_TYPES_FN}
            if exp.get("paver"):
                exp["paver"] = WORKSTATIONS
            for prod in exp:
                if not exp[prod]:
                    expense = get_per_sqft_expense(
                            from_date=from_date, 
                            to_date=to_date, 
                            machines=[], 
                            prod_details=prod,
                            expense_name=row.expense_name, 
                            all_expenses=all_expenses
                        )
                    exp_child["balance"] += (expense or 0)
                    exp_child[prod] = expense or 0
                else:
                    for mach in exp[prod]:
                        expense = get_per_sqft_expense(
                                from_date=from_date, 
                                to_date=to_date, 
                                machines=[mach], 
                                prod_details=prod,
                                expense_name=row.expense_name, 
                                all_expenses=all_expenses
                            )
                        if not exp_child.get(prod):
                            exp_child[prod] = 0
                        exp_child[prod] += (expense or 0)
                        exp_child["balance"] += (expense or 0)
                        exp_child[frappe.scrub(mach)] = expense or 0
        else:
            expense = get_per_sqft_expense(
                    from_date=from_date, 
                    to_date=to_date, 
                    machines=machines, 
                    prod_details=prod_details,
                    expense_name=row.expense_name, 
                    all_expenses=all_expenses
                )
            exp_child["balance"] = expense
        
        res.append(exp_child)

    return res

def get_per_sqft_expense(from_date, to_date, machines, prod_details, expense_name, all_expenses=False):
    conditions = ""
    WORKSTATIONS = frappe.get_all("Workstation", {"used_in_expense_splitup": 1}, pluck="name")
    
    if not machines:
        machines = WORKSTATIONS

    if prod_details:
        conditions+=f""" and (exp.{frappe.scrub(prod_details)}=1
        or ({" and ".join([f'exp.{i_type}=0' for i_type in ITEM_TYPES_FN])}) 
        or ({" and ".join([f'exp.{i_type}=1' for i_type in ITEM_TYPES_FN])})) """

    if expense_name:
        conditions+=f""" and exp.expense_name='{expense_name}' """

    if machines and sorted(machines)!=sorted(WORKSTATIONS):
        conditions+=f"""  AND
            (
                ({" OR ".join([
                    f''' IFNULL(exp.{frappe.scrub(macn)}, 0) '''
                for macn in machines])}
                ) OR
                ({" AND ".join([
                    f''' IFNULL(exp.{frappe.scrub(wrk)}, 0)=0 '''
                for wrk in WORKSTATIONS ] + [" 1=1 "])})
                OR
                ({" AND ".join([
                    f''' IFNULL(exp.{frappe.scrub(wrk)}, 0)=1 '''
                for wrk in WORKSTATIONS ] + [" 1=1 "])})
            )
        """

    query = f"""
        select
            *
        from `tabProduction Expense Table` exp
        where
            exp.parenttype="Production Expense"
            and exp.parent="Production Expense"
            {conditions}
    """

    entries = frappe.db.sql(query, as_dict=True)
    expense_amount = 0

    for row in entries:
        exp_machines=[]
        for wrk in WORKSTATIONS:
            if frappe.scrub(wrk) in row and row.get(frappe.scrub(wrk)):
                exp_machines.append(wrk)

        exp_machines.sort()
        exp_machines=sorted([i for i in machines if ((i in exp_machines) or not exp_machines)])
        
        if exp_machines==sorted(WORKSTATIONS):  
            # If all machines, then make it [], to get all machines prod_details
            exp_machines=[]
        
        exp_machine_key = json.dumps(exp_machines)
        if exp_machine_key not in machine_wise_prod_info:
            machine_wise_prod_info[exp_machine_key] = get_production_details(from_date=from_date, to_date=to_date, machines=exp_machines, ITEM_TYPES=ITEM_TYPES)
        
        sqf = machine_wise_prod_info[exp_machine_key].get(prod_details) or 0

        expense_amount+=(sqf or 0) * (row.cost_per_sqft or 0)

    return expense_amount
