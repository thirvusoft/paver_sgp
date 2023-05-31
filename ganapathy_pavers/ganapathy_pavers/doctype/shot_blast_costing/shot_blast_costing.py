# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

# import frappe
import datetime
import json
from erpnext.stock.doctype.batch.batch import get_batch_qty
import frappe
from frappe import _, scrub
from frappe.desk.reportview import get_filters_cond, get_match_cond
from frappe.model.document import Document
from erpnext.controllers.queries import get_fields
from frappe.utils.data import nowdate
from ganapathy_pavers.utils.py.sitework_printformat import get_paver_production_rate

uom_conv_query = lambda: f"""
            taken_pieces * (
                ifnull((
                    SELECT
                        uom.conversion_factor
                    FROM `tabUOM Conversion Detail` uom
                    WHERE
                        uom.parenttype='Item' and
                        uom.parent=item_name and
                        uom.uom='Nos'
                    limit 1
                )    
                , 0)
                /
                ifnull((
                    SELECT
                        uom.conversion_factor
                    FROM `tabUOM Conversion Detail` uom
                    WHERE
                        uom.parenttype='Item' and
                        uom.parent=item_name and
                        uom.uom='Bdl'
                    limit 1
                )    
                , 0)
            )
        """

class ShotBlastCosting(Document):
    def validate(self):
        self.total_cost = (self.additional_cost or 0) + (self.labour_cost or 0) + (self.total_operator_wages or 0)
        self.total_cost_per_sqft = (self.total_cost or 0) / (((self.total_sqft or 0) - (self.total_damage_sqft or 0)) or 1)
        self.fetch_warehouses()
        self.calculate_total_damage_cost()
    
    @frappe.whitelist()
    def calculate_total_damage_cost(self):
        total_cost=0
        for row in self.items:
            if row.material_manufacturing and row.damages_in_sqft:
                prod_date = frappe.get_value("Material Manufacturing", row.material_manufacturing, "from_time")
                row.damage_cost = row.damages_in_sqft * (get_paver_production_rate(item=row.item_name, date=prod_date) or 0)
                total_cost += row.damage_cost or 0
        self.total_damage_cost = total_cost

    def fetch_warehouses(self):
        if not self.warehouse:
            curing_t = frappe.db.get_single_value("USB Setting", "default_curing_target_warehouse")
            self.warehouse = curing_t

        if not self.source_warehouse:
            curing_s = frappe.db.get_single_value("USB Setting", "default_curing_target_warehouse_for_setting")
            self.source_warehouse = curing_s

        if not self.workstation:
            wrk = frappe.db.get_single_value("USB Setting", "default_shot_blast_workstation")
            self.workstation = wrk

    def before_submit(doc):
        material = frappe.get_all("Stock Entry",filters={"shot_blast":doc.get("name")},pluck="name")
        if len(material) == 0:
            frappe.throw("Process Incomplete. Create Stock Entry To Submit")
    def on_update(doc):
        if doc.docstatus<=1:
            sbc=frappe.db.sql(f"""
                select material_manufacturing, sum(bundle_taken + {uom_conv_query()}) as bundle_taken from `tabShot Blast Items` where parent in (select name from `tabShot Blast Costing` where docstatus!=2) group by material_manufacturing;
            """, as_dict=True)
            mm = [i['material_manufacturing'] for i in sbc]
            other_mms = frappe.get_all("Material Manufacturing", filters = {"is_shot_blasting": 1, "name": ["not in", mm]}, fields = ["name as material_manufacturing"])
            for mm in other_mms:
                mm["bundle_taken"] = 0

            for i in sbc + other_mms:
                Bdl=(frappe.db.get_value("Material Manufacturing", i['material_manufacturing'], 'no_of_bundle') or 0)
                frappe.db.set_value("Material Manufacturing",i['material_manufacturing'],'shot_blasted_bundle', Bdl-(i['bundle_taken'] or 0))
                if Bdl-(i['bundle_taken'] or 0) <= 0:
                    frappe.db.set_value("Material Manufacturing",i['material_manufacturing'],'status1', "Completed")
                else:
                    frappe.db.set_value("Material Manufacturing",i['material_manufacturing'],'status1', "Shot Blast")
       

    def on_trash(doc):
        sbc=frappe.db.sql(f"""
            select material_manufacturing, sum(bundle_taken + {uom_conv_query()}) as bundle_taken from `tabShot Blast Items` where parent in (select name from `tabShot Blast Costing` where docstatus!=2 and name!='{doc.name}') group by material_manufacturing;
        """, as_dict=True)
        # and name!= '{doc.name}'
        mm=frappe.db.sql(f"""
            select material_manufacturing, sum(bundle_taken + {uom_conv_query()}) as bundle_taken from `tabShot Blast Items` where parent in (select name from `tabShot Blast Costing` where docstatus!=2 and name='{doc.name}') group by material_manufacturing;
        """)
        for mm_doc in mm:
            mm1=frappe.db.sql(f"""
                select name from `tabShot Blast Items` where parent!='{doc.name}' and material_manufacturing='{mm_doc[0]}'
            """)
            if not mm1:
                sbc+=({'material_manufacturing': mm_doc[0], "bundle_taken": 0},)
        mm = [i['material_manufacturing'] for i in sbc]
        other_mms = frappe.get_all("Material Manufacturing", filters = {"is_shot_blasting": 1, "name": ["not in", mm]}, fields = ["name as material_manufacturing"])
        for mm in other_mms:
            mm["bundle_taken"] = 0

        for i in sbc + other_mms:
            Bdl=(frappe.db.get_value("Material Manufacturing", i['material_manufacturing'], 'no_of_bundle') or 0)
            frappe.db.set_value("Material Manufacturing",i['material_manufacturing'],'shot_blasted_bundle', Bdl-(i['bundle_taken'] or 0))
            if Bdl-(i['bundle_taken'] or 0) <= 0:
                frappe.db.set_value("Material Manufacturing",i['material_manufacturing'],'status1', "Completed")
            else:
                frappe.db.set_value("Material Manufacturing",i['material_manufacturing'],'status1', "Shot Blast")

    def on_cancel(doc):
        doc.on_trash()

@frappe.whitelist()
def make_stock_entry(doc):
    doc=json.loads(doc)

    valid = frappe.get_all("Stock Entry",filters={"shot_blast_costing":doc.get("name"),"docstatus":["!=",2]},pluck="name")
    if len(valid) >= 1:
           frappe.throw("Already Stock Entry("+valid[0]+") Created For Shot Blast Costing")

    if doc.get("total_cost") == 0:
        frappe.throw("Please Enter Total Expense Cost")
    if not doc.get("total_bundle") and not doc.get("total_pieces"):
        frappe.throw("Please Enter Total Bundle")
    valid = frappe.get_all("Stock Entry",filters={"shot_blast":doc.get("name"),"stock_entry_type":"Material Transfer","docstatus":["!=",2]},pluck="name")
    if len(valid) >= 1:
        frappe.throw("Already Stock Entry("+valid[0]+") Created")

    _datetime = datetime.datetime.strptime(doc.get("to_time"), '%Y-%m-%d %H:%M:%S')

    default_scrap_warehouse = frappe.db.get_singles_value("USB Setting", "scrap_warehouse")
    expenses_included_in_valuation = frappe.get_cached_value("Company", doc.get("company"), "expenses_included_in_valuation")
    
    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.company = doc.get("company")
    stock_entry.shot_blast = doc.get("name")
    stock_entry.set_posting_time = 1
    stock_entry.posting_date = _datetime.date()
    stock_entry.posting_time = _datetime.time()
    stock_entry.shot_blast_costing = doc.get("name")
    default_nos = frappe.db.get_singles_value("USB Setting", "default_manufacture_uom")
    default_bundle = frappe.db.get_singles_value("USB Setting", "default_rack_shift_uom")
    stock_entry.stock_entry_type = "Repack"
    for i in doc.get("items"):
        stock_entry.append('items', dict(
            s_warehouse = doc.get("source_warehouse"), 
            item_code = i["item_name"],
            qty = i["sqft"]-i["damages_in_sqft"], 
            uom = frappe.db.get_value("Item", i["item_name"], "stock_uom"),
            batch_no = i["batch"]
        ))
        stock_entry.append('items', dict(
            t_warehouse = doc.get("warehouse"), 
            item_code = i["item_name"],
            qty = i["sqft"]-i["damages_in_sqft"], 
            uom = frappe.db.get_value("Item", i["item_name"], "stock_uom"),
        ))

        check_batch_stock_avalability(
            i["batch"], 
            doc.get("source_warehouse"), 
            doc.get("warehouse"),
            _datetime.date(),
            _datetime.time(),
            i["sqft"]
        )
        
        if i["damages_in_nos"] > 0:
            stock_entry.append('items', dict(
                s_warehouse = doc.get("source_warehouse"),t_warehouse = default_scrap_warehouse, item_code = i["item_name"]	,qty = i["damages_in_nos"], uom = default_nos, is_process_loss = 1,batch_no = i["batch"]
                ))
    stock_entry.append('additional_costs', dict(
            expense_account	 = expenses_included_in_valuation, amount = doc.get("total_cost"),description = "In Shot Blast, Cost of Labour and Additional"
        ))
    stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
    stock_entry.save()
    stock_entry.submit()
    frappe.msgprint("New Stock Entry Created "+stock_entry.name)

@frappe.whitelist()
def uom_conversion(mm, batch=None, date=None, warehouse=None):
    res = {
        "bundle": 0,
        "stock": 0
    }
    if batch:
        stock_conditions=""
        if date:
            stock_conditions += f""" and timestamp(sle.posting_date, sle.posting_time) <= "{date}" """
        if warehouse:
            stock_conditions += f""" and sle.warehouse='{warehouse}' """

        batch_qty_query = f"""
                    select 
                        sum(sle.actual_qty)
                    from `tabStock Ledger Entry` sle
                    where 
                        sle.is_cancelled = 0 and 
                        sle.batch_no= '{batch}'
                        {stock_conditions}
            """
        batch_qty = frappe.db.sql(batch_qty_query)
        res['stock'] = batch_qty[0][0] if batch_qty and batch_qty[0] and batch_qty[0][0] else 0

    batch_qty = frappe.get_value('Material Manufacturing', mm, 'shot_blasted_bundle')
    res["bundle"] = batch_qty
    return res

@frappe.whitelist()
def batch_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
    searchfield = frappe.get_meta(doctype).get_search_fields()
    searchfield = "(" +"or ".join(field + " like %(txt)s" for field in searchfield) + ")"
    if filters and filters.get('material_manufacturing'):
        searchfield+=f""" and name='{frappe.get_value("Material Manufacturing", filters.get("material_manufacturing"), "batch_no_curing")}' """
    fields = ', '.join(get_fields(doctype))
    res = frappe.db.sql(
        f"""SELECT 
                {fields} 
            FROM 
                `tab{doctype}`
            WHERE
                ({searchfield})
            ORDER BY
                (case when locate(%(_txt)s, name) > 0 then locate(%(_txt)s, name) else 99999 end),
                idx desc,
                name
            LIMIT
                {page_len} offset {start}
        """,
        {"txt": "%%%s%%" % txt, "_txt": txt.replace("%", ""), "start": start, "page_len": page_len},
    )
    return res

def check_batch_stock_avalability(batch_no, warehouse, f_warehouse, date, time, needed_stock):
    qty = get_batch_qty(batch_no, warehouse, posting_date=date, posting_time=time) or 0
    if qty != 0:
        return
    
    current_qty = get_batch_qty(batch_no, f_warehouse, posting_date=frappe.utils.nowdate(), posting_time=frappe.utils.nowtime()) or 0
    if current_qty < needed_stock:
        return

    move_stock({
                "date": str(date),
                "time": str(time),
                "batch_no": batch_no,
                "from_warehouse": f_warehouse,
                "to_warehouse": warehouse,
            })


def move_stock(args):
    if not args:
        return

    date = args.get("date")  
    time = args.get("time")  
    batch_no = args.get("batch_no")  
    f_warehouse = args.get("from_warehouse")  
    warehouse = args.get("to_warehouse")  

    current_qty = get_batch_qty(batch_no, f_warehouse, posting_date=frappe.utils.nowdate(), posting_time=frappe.utils.nowtime()) or 0
    
    if current_qty<=0:
        return
    
    doc = frappe.new_doc("Stock Entry")
    doc.update({
        "stock_entry_type": "Material Transfer",
        "posting_date": date,
        "posting_time": time,
        "set_posting_time": 1,
        "items": [{
            "s_warehouse": f_warehouse,
            "t_warehouse": warehouse,
            "item_code": frappe.db.get_value("Batch", batch_no, "item"),
            "qty": current_qty,
            "batch_no": batch_no
        }]
    })
    doc.save()
    doc.submit()


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def material_manufacturing_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
    conditions = []

    if isinstance(filters, str):
        filters = json.loads(filters)

    #Get searchfields from meta and use in DocType Link field query
    meta = frappe.get_meta(doctype, cached=True)
    searchfields = meta.get_search_fields() + ['batch_no_curing']

    columns = ''
    extra_searchfields = ['`tabMaterial Manufacturing`.batch_no_curing'] + [f"`tabMaterial Manufacturing`.{field}" for field in searchfields]

    if extra_searchfields:
        columns = ", " + ", ".join(extra_searchfields)

    searchfields = searchfields + [field for field in [searchfield]
        if not field in searchfields]
    searchfields = " or ".join([field + " like %(txt)s" for field in searchfields])

    date = ""
    warehouse = ""
    if filters.get("date"):
        date=filters.get("date")
        filters.pop("date")
    if filters.get("warehouse"):
        warehouse=filters.get("warehouse")
        filters.pop("warehouse")

    stock_conditions=""
    if date:
        stock_conditions += f""" and timestamp(sle.posting_date, sle.posting_time) <= "{date}" """
    if warehouse:
        stock_conditions += f""" and sle.warehouse='{warehouse}' """

    batch_qty_query = f"""
        case when ifnull(`tabMaterial Manufacturing`.batch_no_curing, "")!=""
        then ifnull((
                select 
                    sum(sle.actual_qty)
                from `tabStock Ledger Entry` sle
                where 
                    sle.is_cancelled = 0 and 
                    sle.batch_no= `tabMaterial Manufacturing`.batch_no_curing
                    {stock_conditions}
            ), 0)
        else 0 end
        """
        
    return frappe.db.sql("""select
            `tab{doctype}`.name,
            CONCAT("Batch Qty: ", round({batch_qty_query}, 2)) as batch_qty
        {columns}
        from `tab{doctype}`
        where `tab{doctype}`.docstatus < 2
            and ifnull(`tabMaterial Manufacturing`.batch_no_curing, "")!=""
            and ({scond})
            {fcond} {mcond}
        order by
            from_time, 
            if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
            if(locate(%(_txt)s, item_to_manufacture), locate(%(_txt)s, item_to_manufacture), 99999),
            idx desc,
            name, item_to_manufacture
        limit %(start)s, %(page_len)s """.format(
            doctype=doctype,
            columns=columns,
            scond=searchfields,
            batch_qty_query=batch_qty_query,
            fcond=get_filters_cond(doctype, filters, conditions).replace('%', '%%'),
            mcond=get_match_cond(doctype).replace('%', '%%')),
            {
                "today": nowdate(),
                "txt": "%%%s%%" % txt,
                "_txt": txt.replace("%", ""),
                "start": start,
                "page_len": page_len
            }, as_dict=as_dict)

@frappe.whitelist()
def get_operators(workstation, division=1):
    division = int(division)
    op_table=[]
    op_list=[]
 
    op_cost= frappe.get_doc("Workstation",workstation)
    for j in op_cost.ts_operators_table:
        if(j.ts_operator_name not in op_list):
            op_list.append(j.ts_operator_name)
            op_table.append({"employee":j.ts_operator_name,"operator_name":j.ts_operator_full_name,"salary":j.ts_operator_wages, "division_salary":(j.ts_operator_wages/division)})
        else:
            for k in op_table:
                if k['employee'] == j.ts_operator_name:
                    k['salary'] = j.ts_operator_wages
                    k["division_salary"] = (j.ts_operator_wages/division)
    return(op_table)