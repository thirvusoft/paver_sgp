import math
import frappe
import json
from frappe.utils.csvutils import getlink
from frappe.utils import nowdate
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from ganapathy_pavers.custom.py.sales_order import get_item_rate
from ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing import uom_conversion
from ganapathy_pavers import get_valuation_rate, get_buying_rate, uom_conversion
from ganapathy_pavers.utils.py.sitework_printformat import get_item_price_list_rate


@frappe.whitelist()
def item_details_fetching_pavers(item_code):
    if item_code:
        doc = frappe.get_doc("Item",item_code)
        item_price = get_item_rate(item_code)
        area_bundle= doc.bundle_per_sqr_ft
        return area_bundle,item_price

@frappe.whitelist()
def item_details_fetching_compoundwall(item_code):
    if item_code:
        doc = frappe.get_doc("Item",item_code)
        item_price = get_item_rate(item_code)
        area_bundle= doc.bundle_per_sqr_ft
        return area_bundle,item_price

def before_save(doc, action=None):
    additionalcost_total= 0
    item_details_total = 0
    job_worker_total = 0
    raw_material_total = 0
    sales_invoice_amount=0

    for i in doc.additional_cost:
        additionalcost_total = additionalcost_total+ (i.amount or 0)
    doc.total = additionalcost_total

    for i in doc.item_details:
        item_details_total = item_details_total+(i.amount or 0)
    for i in doc.item_details_compound_wall:
        item_details_total = item_details_total+(i.amount or 0)
    doc.total_amount=item_details_total

    for i in doc.job_worker:
        job_worker_total = job_worker_total+(i.amount or 0)
    doc.total_job_worker_cost=job_worker_total

    for i in doc.raw_material:
        raw_material_total = raw_material_total+(i.amount or 0)
    doc.total_amount_of_raw_material=raw_material_total

    sales_invoice_amount = sum(frappe.get_all("Sales Invoice", {"docstatus": 1, "site_work": doc.name}, pluck="total"))

    doc.total_expense_amount=sales_invoice_amount or 0

    item_cost=0
    rm_cost=0
    
    for item in doc.delivery_detail:
        date = item.creation
        bin_ = get_item_price_list_rate(item = item.item, date = date)
        item_cost+=(bin_ or 0)* (((item.delivered_stock_qty or 0) + (item.returned_stock_qty or 0)))

    rate=frappe.db.sql(f"""
                SELECT 
                    SUM(dni.stock_qty) *
                    ifnull((
                            SELECT sle.valuation_rate
                            FROM `tabStock Ledger Entry` sle
                            WHERE
                                sle.is_cancelled=0 and
                                sle.voucher_type = 'Purchase Invoice' and
                                sle.item_code = dni.item_code and
                                sle.posting_date  <= dn.posting_date and
                                sle.is_cancelled = 0
                            order by posting_date desc
                            limit 1
                        ), 0) as valuation_rate
                FROM `tabDelivery Note Item` dni
                LEFT OUTER JOIN `tabDelivery Note` dn
                ON dn.name=dni.parent AND dni.parenttype="Delivery Note"
                WHERE
                    dni.item_group='Raw Material'
                    AND dn.site_work='{doc.name}'
                    AND dn.docstatus=1
                GROUP BY dni.item_code, dni.uom
        """)
    rate = sum([r[0] for r in rate if r and r[0]])
    rm_cost+=rate

    doc.actual_site_cost_calculation=(item_cost or 0)+(doc.total or 0)+(doc.total_job_worker_cost or 0)+ (rm_cost or 0) + (doc.transporting_cost or 0)
    doc.site_profit_amount=(doc.total_expense_amount or 0) - (doc.actual_site_cost_calculation or 0)
    return doc

@frappe.whitelist()
def add_total_amount(items):
    if items:
        return sum([i['amount'] for i in json.loads(items)])


def autoname(self, event):
    self.project_name = (self.project_name or "").title()
    self.name= self.project_name


def create_status():
    print('Creating Property Setter for Site Work Status')
    doc=frappe.new_doc('Property Setter')
    doc.update({
        "doctype_or_field": "DocField",
        "doc_type":"Project",
        "field_name":"status",
        "property":"options",
        "value":"\nOpen\nCompleted\nTo Bill\nBilled\nCancelled\nStock Pending at Site\nRework"
    })
    doc.save()
    frappe.db.commit()



def validate(self,event):
    validate_jw_qty(self)
    if(self.name not in frappe.get_all('Project', pluck="name")):
        return
    amount=0
    total_amount=0
    add_cost=[]
    mode=''
    for row in self.additional_cost:
        if(row.description=="Site Advance"):
            child_name=row.name
            amount=row.amount or 0
            total_amount+=amount
            mode=row.mode_of_payment
            row.amount=0
            add_cost.append(row)
            if(amount):
                mode_of_payment = frappe.get_doc("Mode of Payment",mode).accounts
                for i in mode_of_payment:
                    if(i.company==self.company):
                        acc_paid_to=i.default_account
                        break
                try:
                    if(acc_paid_to):pass
                except:
                    frappe.throw(("Please set Company and Default account for ({0}) mode of payment").format(mode))

                employee_advance = create_jw_advance(row.job_worker, row.currency, amount, row.advance_account, row.mode_of_payment_for_advance, self.company, self.name, row.exchange_rate, row.date, row.branch)

                doc=frappe.new_doc('Payment Entry')
                doc.update({
                    'company': self.company,
                    'source_exchange_rate': 1,
                    'payment_type': 'Receive',
                    'posting_date': row.date or nowdate(),
                    'branch': row.branch,
                    'mode_of_payment': mode,
                    'party_type': 'Customer',
                    'party': row.customer if(self.is_multi_customer) else self.customer,
                    'paid_amount': amount,
                    'paid_to': get_bank_cash_account(mode, self.company).get('account'),
                    'project': self.name,
                    'site_work': self.name,
                    'received_amount': amount,
                    'target_exchange_rate': 1,
                    'paid_to_account_currency': frappe.db.get_value('Account',acc_paid_to,'account_currency'),
                    'employee_advance': employee_advance
                })
                doc.insert()
                doc.submit()
                
                if(row.name and event=='after_insert'):
                    frappe.db.set_value("Additional Costs", row.name, 'amount', 0)
        else:
            add_cost.append(row)
    if(event=='after_insert'):
        frappe.db.set_value("Project", self.name, 'total_advance_amount', (self.total_advance_amount or 0)+ (total_amount or 0))
    if(event=='validate'):
        self.update({
            'additional_cost': add_cost,
            'total_advance_amount': (self.total_advance_amount or 0)+ (total_amount or 0)
        })

def validate_jw_qty(self):
    if(self.type == "Pavers"):
        bundle_uom="Bdl"
        sqf_uom="SQF"
        delivered_item={}
        warning_delivered_item={}
        for row in self.delivery_detail:
            if(row.item not  in delivered_item):
                delivered_item[row.item]=0
                warning_delivered_item[row.item]=0
            bundle_qty=uom_conversion(item=row.item, from_qty=((row.delivered_stock_qty or 0)+(row.returned_stock_qty or 0)), to_uom=bundle_uom)
            delivered_item[row.item]+=round(bundle_qty)
            warning_delivered_item[row.item]+=round((row.delivered_stock_qty or 0)+(row.returned_stock_qty or 0))
        jw_items={}
        warning_jw_items={}
        for row in self.job_worker:
            if(row.item and not row.other_work):
                if(row.item not  in jw_items):
                    jw_items[row.item]=0
                    warning_jw_items[row.item]=0
                
                bundle_qty=uom_conversion(item=row.item, from_uom=sqf_uom, from_qty=row.sqft_allocated, to_uom=bundle_uom)
                jw_items[row.item]+=round(bundle_qty)
                warning_jw_items[row.item]+=round(row.sqft_allocated)
                
        wrong_items=[]
        warning_items=[]
        jw_qty = 0
        del_qty = 0
        for item in jw_items:
            jw_qty += (jw_items.get(item) or 0)
            del_qty += delivered_item.get(item) or 0
            if((jw_items.get(item) or 0)>math.ceil(delivered_item.get(item) or 0)):
                wrong_items.append({"item_code": item, "entered":jw_items.get(item), "delivered": (delivered_item.get(item) or 0)})
            elif((warning_jw_items.get(item) or 0)>(warning_delivered_item.get(item) or 0)):
                warning_items.append({"item_code": item, "entered":warning_jw_items.get(item), "delivered": (warning_delivered_item.get(item) or 0)})

        if(wrong_items):
            message="<ul>"+''.join([f"""<li><a href="/app/item/{item.get('item_code', '')}"><b>{item.get("item_code", "")}</b></a><div style="display: flex; width: 100%;"><div style="width: 50%;">Delivered Qty: {item.get("delivered", 0)}</div><div style="width: 50%;">Entered Qty: {item.get("entered", 0)}</div></div></li>""" for item in wrong_items])+"</ul>"
            frappe.throw("Job Worker completed qty cannot be greater than Delivered Qty for the following items "+ message)
        
        if(warning_items):
            message="<ul>"+''.join([f"""<li><a href="/app/item/{item.get('item_code', '')}"><b>{item.get("item_code", "")}</b></a><div style="display: flex; width: 100%;"><div style="width: 50%;">Delivered Qty: {item.get("delivered", 0)}</div><div style="width: 50%;">Entered Qty: {item.get("entered", 0)}</div></div></li>""" for item in warning_items])+"</ul>"
            # frappe.msgprint(title="Warning", msg="Job Worker completed qty is greater than Delivered Qty for the following items "+ message)

        if jw_qty > (del_qty - (self.returned_scrap_qty or 0)):
            frappe.throw(f"""Job Worker completed qty cannot be greater than Delivered Qty.
                <div>
                    <ul>
                        <li>Delivered Qty - <b>{del_qty}</b></li>
                        <li>Returned Scrap Qty - <b>{(self.returned_scrap_qty or 0)}</b></li>
                        <li>Job Worker Qty - <b>{jw_qty}</b></li> 
                    </ul>
                </div>
            """)

    if(self.type == "Compound Wall"):
        delivered_qty = 0
        for row in self.delivery_detail:
            if(row.item and frappe.get_value("Item", row.item, 'item_group') == "Compound Walls"):
                delivered_qty += uom_conversion(row.item, '', float(row.delivered_stock_qty), "SQF")

        completed_qty = 0
        for row in self.job_worker:
            if((not row.item) or row.item_group == "Compound Walls") and not row.other_work:
                completed_qty += float(row.sqft_allocated or 0)

        if(completed_qty > (math.ceil(delivered_qty) - (self.earth_foundation_sqft or 0) - (self.returned_scrap_qty or 0))):
            frappe.throw(f"""Job Worker completed qty cannot be greater than Delivered Qty.
                <div>
                    <ul>
                        <li>Delivered Qty - <b>{math.ceil(delivered_qty)}</b></li>
                        <li>Earth Foundation - <b>{(self.earth_foundation_sqft or 0)}</b></li>
                        <li>Returned Scrap Qty - <b>{(self.returned_scrap_qty or 0)}</b></li>
                        <li>Job Worker Qty - <b>{completed_qty}</b></li> 
                    </ul>
                </div>
            """)

def create_jw_advance(emp_name, currency, adv_amt, adv_act, mop, company ,sw, exchange_rate, date=None, branch=None):
    doc=frappe.new_doc('Employee Advance')
    doc.update({
        'employee': emp_name,
        'posting_date': date or frappe.utils.nowdate(),
        'repay_unclaimed_amount_from_salary': 1,
        'currency': currency,
        'branch': branch,
        'advance_amount': adv_amt,
        'advance_account': adv_act,
        'exchange_rate' : (exchange_rate or 1),
        'company': company,
        'mode_of_payment': mop,
        'purpose': f'Advance amount received from the site work {sw}',
        'project' : sw,
        'site_work': sw
    })
    doc.flags.ignore_permissions = True
    doc.flags.ignore_mandatory = True
    doc.save()
    doc.submit()
    return doc.name

def reduce_advance_amount(self, event=None):
    if self.project:
        doc=frappe.get_doc("Project", self.project)
        doc.update({
            "total_advance_amount": doc.total_advance_amount - self.advance_amount
        })
        doc.db_update()

@frappe.whitelist()
def update_completion_date(date, name):
    frappe.db.set_value("Project", name, "completion_date", date)

def update_status(doc, events):
    frappe.db.set_value("Project", doc.name, "previous_state", doc.status)
    doc.reload()

def validate_status(self,event):
    if (self.previous_state == "Billed" and self.status != "Rework"):
        frappe.throw("Billed Site Work cannot be updated.")

def rework_count(self,event):
    a = frappe.get_value("Project", self.name, 'status')
    if (a =="Billed" and self.status =="Rework"):
        self.total_rework = self.total_rework + 1
    else:
        pass

def update_delivery_detail(self, event):
    item_details = self.item_details + self.item_details_compound_wall
    to_delivered_qty = {}
    for row in item_details:
        if row.work!="Supply Only":
            if(row.item not in to_delivered_qty):
                to_delivered_qty[row.item] = 0
            to_delivered_qty[row.item] += row.stock_qty

    for items in to_delivered_qty:
        catch = 0
        for row in range(len(self.delivery_detail)):
            if(self.delivery_detail[row].item == items):
                self.delivery_detail[row].qty_to_deliver = to_delivered_qty[items]
                self.delivery_detail[row].pending_qty__to_deliver = (to_delivered_qty[items] or 0) - (self.delivery_detail[row].delivered_stock_qty or 0)
                catch = 1
        if(not catch):
            delivery_detail = [{'item': items, 'qty_to_deliver': to_delivered_qty[items], 'pending_qty__to_deliver': (to_delivered_qty[items] or 0)}]
            self.update({
                'delivery_detail': (self.delivery_detail or []) + delivery_detail
            })

def job_worker(self, event=None):
    for row in self.job_worker:
        if not row.other_work:
            row.description_for_other_work=""

@frappe.whitelist()
def update_delivered_qty(site_work=[]):
    old_value=""
    sw=""
    log_content=""
    try:
        if isinstance(site_work, str):
            site_work=json.loads(site_work)
        
        if not site_work:
            site_work=frappe.get_all("Project", pluck="name")

        for sw in site_work:
            total_delivered_qty = frappe.db.sql(f""" select
                                        child.item_code,
                                        sum(child.stock_qty) as stock_qty,
                                        sum(child.qty) as qty,
                                        sum(child.ts_qty) as bundle,
                                        sum(child.pieces) as pieces,
                                        child.against_sales_order as sales_order
                                        from `tabDelivery Note` as doc
                                        left outer join `tabDelivery Note Item` as child
                                            on doc.name = child.parent
                                        where 
                                            doc.docstatus = 1 
                                            and doc.site_work = '{sw}'  
                                            and doc.is_return = 0
                                             
                                        group by child.item_code, CASE WHEN child.item_group = "Raw Material" THEN child.against_sales_order
                                                      ELSE 0 END
                                        """, as_dict=True)

            total_delivered_qty += frappe.db.sql(f""" select
                                        child.item_code,
                                        sum(child.stock_qty) as stock_qty,
                                        sum(child.delivered_qty) as qty,
                                        0 as bundle,
                                        0 as pieces,
                                        doc.name as sales_order
                                        from `tabSales Order` as doc
                                        left outer join `tabSales Order Item` as child
                                            on doc.name = child.parent
                                        where 
                                            doc.docstatus = 1 
                                            and doc.site_work = '{sw}' 
                                            and child.delivered_by_supplier = 1
                                        group by child.item_code, CASE WHEN child.item_group = "Raw Material" THEN doc.name
                                                      ELSE 1 END
                                        """, as_dict=True)

            for data in total_delivered_qty:
                if frappe.get_value("Item", data.get('item_code'), "item_group")=="Raw Material":
                    old_value=frappe.db.sql(f"""
                        SELECT delivered_quantity, item
                        FROM `tabRaw Materials`
                        WHERE  parenttype="Project" and parent="{sw}" and item="{data.get('item_code')}" and IFNULL(sales_order, '') = "{data.get('sales_order', '') or ''}"
                    """, as_dict=True)
                    if old_value and old_value[0].get("delivered_quantity") != data.get("qty"):
                        log_content+=f"""
                        Site Work: {sw}\n
                        {data.get("item_code")} Delivered Raw Material old: {old_value[0].get("delivered_quantity")}   new: {data.get("qty")}   SALES ORDER {data.get('sales_order')}\n\n\n
                        """
                        frappe.db.sql(f"""
                            UPDATE `tabRaw Materials`
                            SET 
                                delivered_quantity = {data.get("qty")}
                            WHERE parenttype="Project" and parent="{sw}" and item="{data.get('item_code')}" and IFNULL(sales_order, '') = "{data.get('sales_order', '') or ''}"
                        """)
                    elif(not old_value):
                        log_content+=f"""
                        Site Work: {sw}\n
                        ---------NEW RECORD---------\n
                        {data.get("item_code")} Delivered Raw Material new: {data.get("qty")}   SALES ORDER {data.get('sales_order')}\n\n\n
                        """
                        new_row={
                            "parenttype": "Project",
                            "parent": sw,
                            "item": data.get('item_code'),
                            "delivered_quantity": data.get("qty"),
                            "sales_order": data.get('sales_order'),
                        }
                        sw_doc=frappe.get_doc("Project", sw)
                        sw_doc.update({
                            "raw_material": sw_doc.get("raw_material", [])+[new_row]
                        })
                        sw_doc.run_method=lambda *arg,**args:0
                        sw_doc.save()

            total_returned_qty = frappe.db.sql(f""" select
                                            child.item_code,
                                            sum(child.stock_qty) as stock_qty,
                                            sum(child.qty) as qty,
                                            sum(child.ts_qty) as bundle,
                                            sum(child.pieces) as pieces,
                                            child.against_sales_order as sales_order
                                        FROM `tabDelivery Note` as doc
                                        left outer join `tabDelivery Note Item` as child
                                            on doc.name = child.parent
                                        where 
                                            doc.docstatus = 1 
                                            and doc.site_work = '{sw}' 
                                            and doc.is_return = 1
                                       group by child.item_code, CASE WHEN child.item_group = "Raw Material" THEN child.against_sales_order
                                                      ELSE 0 END
                                        """, as_dict=True)
            for data in total_returned_qty:
                if frappe.get_value("Item", data.get('item_code'), "item_group")=="Raw Material":
                    old_value=frappe.db.sql(f"""
                        SELECT returned_quantity
                        FROM `tabRaw Materials`
                        WHERE  parenttype="Project" and parent="{sw}" and item="{data.get('item_code')}" and IFNULL(sales_order, '') = "{data.get('sales_order', '') or ''}"
                    """, as_dict=True)
                    if old_value and old_value[0].get("returned_quantity") != data.get("qty"):
                        log_content+=f"""
                        Site Work: {sw}\n
                        {data.get("item_code")} Returned Raw Material old: {old_value[0].get("returned_quantity")}   new: {data.get("qty")}   SALES ORDER {data.get('sales_order')}\n\n\n
                        """
                        frappe.db.sql(f"""
                            UPDATE `tabRaw Materials`
                            SET 
                                returned_quantity = {data.get("qty")}
                            WHERE parenttype="Project" and parent="{sw}" and item="{data.get('item_code')}" and IFNULL(sales_order, '') = "{data.get('sales_order', '') or ''}"
                        """)
                    elif(not old_value):
                        log_content+=f"""
                        Site Work: {sw}\n
                        ---------NEW RECORD---------\n
                        {data.get("item_code")} Returned Raw Material new: {data.get("qty")}   SALES ORDER {data.get('sales_order')}\n\n\n
                        """
                        new_row={
                            "parenttype": "Project",
                            "parent": sw,
                            "item": data.get('item_code'),
                            "returned_quantity": data.get("qty"),
                            "sales_order": data.get('sales_order'),
                        }
                        sw_doc=frappe.get_doc("Project", sw)
                        sw_doc.update({
                            "raw_material": sw_doc.get("raw_material", [])+[new_row]
                        })
                        sw_doc.run_method=lambda *arg,**args:0
                        sw_doc.save()
    except BaseException as e:
        log_content+=f"""\n\n{e}\n\n{frappe.get_traceback()}\n\nSITE WORK: {sw}\n\n{old_value}"""
    if log_content:
        frappe.log_error(title=f"SITE WORK DELIVERY QTY MISMATCH  {frappe.utils.now()}", message=f"""{log_content}""")
    # return total_delivered_qty

def job_worker_laying_details(self, event=None):
    jw_items={}
    total_layed_sqft=0
    total_layed_bundle=0
    for row in self.job_worker:
        if not row.other_work:
                total_layed_sqft+=(row.sqft_allocated or 0)
                total_layed_bundle+=(row.completed_bundle or 0)
        if(row.item and not row.other_work):
            if(row.item not  in jw_items):
                jw_items[row.item]={'square_feet': 0, "bundle": 0}
            jw_items[row.item]['square_feet']+=(row.sqft_allocated or 0)
            jw_items[row.item]['bundle']+=(row.completed_bundle or 0)
    for row in self.delivery_detail:
        if row.item in jw_items:
            row.layed_sqft=jw_items[row.item]['square_feet']
            row.layed_bundle=jw_items[row.item]['bundle']
    self.total_layed_sqft=total_layed_sqft
    self.total_layed_bundle=total_layed_bundle
    
def completed_and_required_area(self,event):
    total_area=0
    total_bundle=0
    paver_table=self.item_details
    compound_wall=self.item_details_compound_wall
    if paver_table:
        for i in paver_table:
            total_area+=i.required_area or 0
            total_bundle += i.number_of_bundle or 0
    if compound_wall:
        for i in compound_wall:
            total_area+=i.allocated_ft or 0
    completed_area=0
    total_comp_bundle=0
    job_worker=self.job_worker
    if job_worker:
        for i in job_worker:
            if(i.other_work ==0):
                completed_area+=i.sqft_allocated or 0
                total_comp_bundle +=i.completed_bundle or 0
    self.total_required_area=total_area
    self.total_completed_area=completed_area
    self.total_required_bundle=total_bundle
    self.total_completed_bundle=total_comp_bundle
    self.completed=(completed_area/total_area)*100 if total_area else 0
 

@frappe.whitelist()
def refill_delivery_detail(site_work, event=None):
    if isinstance(site_work, str):
        doc = frappe.get_doc("Project", json.loads(site_work)[0])
    else:
        doc=site_work
    sales_order = frappe.db.sql(f"""
        select
            soi.item_code as item,
            soi.item_group,
            sum(soi.qty) as qty_to_deliver,
            sum(case when soi.delivered_by_supplier = 1 then ifnull(soi.delivered_qty, 0) else 0 end) as delivered_stock_qty
        from `tabSales Order Item` soi
        inner join `tabSales Order` so
        on soi.parent=so.name and soi.parenttype='Sales Order'
        where
            so.docstatus=1 and
            so.site_work='{doc.name}' and
            ifnull((
                select group_concat(distinct _soi.work separator ', ')
                from `tabSales Order Item` _soi
                where _soi.parenttype='Sales Order' and _soi.parent=so.name
            ), "") not in ("Supply Only")
        group by soi.item_code
    """, as_dict=True)

    delivery_note = frappe.db.sql(f"""
        select
            dni.item_code as item,
            dni.item_group,
            sum(case when ifnull(dn.is_return, 0)=0 then dni.qty else 0 end) as delivered_stock_qty,
            sum(case when ifnull(dn.is_return, 0)=0 then dni.ts_qty else 0 end) as delivered_bundle,
            sum(case when ifnull(dn.is_return, 0)=0 then dni.pieces else 0 end) as delivered_pieces,
            sum(case when dn.is_return then dni.qty else 0 end) as returned_stock_qty,
            sum(case when dn.is_return then dni.ts_qty else 0 end) as returned_bundle,
            sum(case when dn.is_return then dni.pieces else 0 end) as returned_pieces
        from `tabDelivery Note Item` dni
        inner join `tabDelivery Note` dn
        on dni.parent=dn.name and dni.parenttype='Delivery Note'
        where
            dn.docstatus=1 and
            dn.site_work='{doc.name}'
        group by dni.item_code
    """, as_dict=True)
    
    delivery_detail=[]
    for dn_row in delivery_note:
        new = True
        for so_row in sales_order:
            if so_row.item == dn_row.item:
                new = False
                dn_row["delivered_stock_qty"] = (dn_row.get("delivered_stock_qty") or 0) + (so_row.get("delivered_stock_qty") or 0)
                so_row.update(dn_row)
                so_row["pending_qty__to_deliver"] = (dn_row.get("qty_to_deliver") or 0) - ((dn_row.get("delivered_stock_qty") or 0) + (dn_row.get("returned_stock_qty") or 0))
                if so_row.get("item_group") !="Raw Material":
                    delivery_detail.append(so_row)
        if new and dn_row.get("item_group") !="Raw Material":
            delivery_detail.append(dn_row)
    
    doc.update({"delivery_detail": delivery_detail})
    if isinstance(site_work, str):
        doc.save()
