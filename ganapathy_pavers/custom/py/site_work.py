import math
import frappe
import json
from frappe.utils.csvutils import getlink
from frappe.utils import nowdate
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from ganapathy_pavers.custom.py.sales_order import get_item_rate
from ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing import uom_conversion
from ganapathy_pavers import get_valuation_rate, get_buying_rate



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
    total_costing=additionalcost_total+item_details_total+job_worker_total+raw_material_total

    doc.total_expense_amount=total_costing

    item_cost=0
    rm_cost=0
    for item in doc.item_details:
        if(item.get('warehouse')):
            bin_=get_valuation_rate(item_code=item.item, warehouse=item.warehouse, posting_date=frappe.utils.get_date_str(doc.creation))
            item_cost+=(bin_ or 0)* (item.stock_qty or 0)

    for item in doc.item_details_compound_wall:
        if(item.get('warehouse')):
            bin_=get_valuation_rate(item_code=item.item, warehouse=item.warehouse, posting_date=frappe.utils.get_date_str(doc.creation))
            item_cost+=(bin_ or 0)* (item.stock_qty or 0)

    for item in doc.raw_material:
        warehouse=frappe.get_value("Sales Order Item", {"item_code":item.item, "parent":item.sales_order}, "warehouse")
        if not warehouse:
            warehouse=frappe.get_all("Sales Order Item", {"parent":item.sales_order, "warehouse":["is", "set"]}, pluck="warehouse")
            if warehouse:
                warehouse=warehouse[0]
        rate=get_buying_rate(item_code=item.item, warehouse=warehouse, posting_date=frappe.utils.get_date_str(doc.creation))
        rm_cost+=(rate or 0)*(item.stock_qty or 0)
    doc.actual_site_cost_calculation=(item_cost or 0)+(doc.total or 0)+(doc.total_job_worker_cost or 0)+ (rm_cost or 0) + (doc.transporting_cost or 0)
    doc.site_profit_amount=(doc.total_expense_amount or 0) - (doc.actual_site_cost_calculation or 0)
    return doc

@frappe.whitelist()
def add_total_amount(items):
    if items:
        return sum([i['amount'] for i in json.loads(items)])


def autoname(self, event):
    self.name= self.project_name

def create_status():
    print('Creating Property Setter for Site Work Status')
    doc=frappe.new_doc('Property Setter')
    doc.update({
        "doctype_or_field": "DocField",
        "doc_type":"Project",
        "field_name":"status",
        "property":"options",
        "value":"\nOpen\nCompleted\nCancelled\nStock Pending at Site\nRework"
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


                doc=frappe.new_doc('Payment Entry')
                doc.update({
                    'company': self.company,
                    'source_exchange_rate': 1,
                    'payment_type': 'Receive',
                    'posting_date': nowdate(),
                    'mode_of_payment': mode,
                    'party_type': 'Customer',
                    'party': row.customer if(self.is_multi_customer) else self.customer,
                    'paid_amount': amount,
                    'paid_to': get_bank_cash_account(mode, self.company).get('account'),
                    'project': self.name,
                    'site_work': self.name,
                    'received_amount': amount,
                    'target_exchange_rate': 1,
                    'paid_to_account_currency': frappe.db.get_value('Account',acc_paid_to,'account_currency')
                })
                doc.insert()
                doc.submit()
                create_jw_advance(row.job_worker, row.currency, amount, row.advance_account, row.mode_of_payment_for_advance, self.company, self.name, row.exchange_rate)
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
    delivered_item={}
    for row in self.delivery_detail:
        if(row.item not  in delivered_item):
            delivered_item[row.item]=0
        delivered_item[row.item]+=row.delivered_stock_qty+row.returned_stock_qty
    jw_items={}
    for row in self.job_worker:
        if(row.item and not row.other_work):
            if(row.item not  in jw_items):
                jw_items[row.item]=0
            item_doc=frappe.get_doc('Item', row.item)
            conv_factor=[conv.conversion_factor for conv in item_doc.uoms if(conv.uom=="SQF")]
            if(not conv_factor):
                frappe.throw('Please enter Square Feet Conversion for an item: '+ frappe.bold(getlink('Item', row.item)))
            jw_items[row.item]+=float(row.sqft_allocated or 0)*conv_factor[0]
    wrong_items=[]
    for item in jw_items:
        if((jw_items.get(item) or 0)>math.ceil(delivered_item.get(item) or 0)):
            wrong_items.append({"item_code": item, "entered":jw_items.get(item), "delivered": math.ceil(delivered_item.get(item) or 0)})
    if(wrong_items):
        message="<ul>"+''.join([f"""<li><a href="/app/item/{item.get('item_code', '')}"><b>{item.get("item_code", "")}</b></a><div style="display: flex; width: 100%;"><div style="width: 50%;">Delivered Qty: {item.get("delivered", 0)}</div><div style="width: 50%;">Entered Qty: {item.get("entered", 0)}</div></div></li>""" for item in wrong_items])+"</ul>"
        frappe.throw("Job Worker completed qty cannot be greater than Delivered Qty for the following items "+ message)

    if(self.type == "Compound Wall"):
        delivered_qty = 0
        for row in self.delivery_detail:
            if(row.item and frappe.get_value("Item", row.item, 'item_group') == "Compound Walls"):
                delivered_qty += uom_conversion(row.item, '', float(row.delivered_stock_qty), "SQF")

        completed_qty = 0
        for row in self.job_worker:
            if((not row.item) or row.item_group == "Compound Walls"):
                completed_qty += float(row.sqft_allocated or 0)

        if(completed_qty > math.ceil(delivered_qty)):
            frappe.throw("Job Worker completed qty cannot be greater than Delivered Qty.")

def create_jw_advance(emp_name, currency, adv_amt, adv_act, mop, company ,sw, exchange_rate):
    doc=frappe.new_doc('Employee Advance')
    doc.update({
        'employee': emp_name,
        'posting_date': frappe.utils.nowdate(),
        'repay_unclaimed_amount_from_salary': 1,
        'currency': currency,
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

def update_status(doc, events):
    frappe.db.set_value("Project", doc.name, "previous_state", doc.status)
    doc.reload()

def validate_status(self,event):
    if (self.previous_state == "Completed" and self.status != "Rework"):
        frappe.throw("Completed Site Work cannot be updated.")

def rework_count(self,event):
    a = frappe.get_value("Project", self.name, 'status')
    if (a =="Completed" and self.status =="Rework"):
        self.total_rework = self.total_rework + 1
    else:
        pass

def update_delivery_detail(self, event):
    item_details = self.item_details + self.item_details_compound_wall
    to_delivered_qty = {}
    for row in item_details:
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
                                        sum(child.pieces) as pieces
                                        from `tabDelivery Note` as doc
                                        left outer join `tabDelivery Note Item` as child
                                            on doc.name = child.parent
                                        where doc.docstatus = 1 and doc.site_work = '{sw}'  and doc.is_return = 0
                                        group by child.item_code
                                        """, as_dict=True)
            for data in total_delivered_qty:
                if frappe.get_value("Item", data.get('item_code'), "item_group") in ["Pavers", "Compound Walls"]:
                    old_value=frappe.db.sql(f"""
                        SELECT delivered_stock_qty, delivered_bundle, delivered_pieces
                        FROM `tabDelivery Status`
                        WHERE  parenttype="Project" and parent="{sw}" and item="{data.get('item_code')}"
                    """, as_dict=True)
                    if old_value and (old_value[0].get("delivered_stock_qty") != data.get("stock_qty") or old_value[0].get("delivered_bundle") != data.get("bundle") or old_value[0].get("delivered_pieces") != data.get("pieces")):
                        log_content+=f"""
                        Site Work: {sw}\n
                        {data.get("item_code")} Delivered Stock Qty old: {old_value[0].get("delivered_stock_qty")}   new: {data.get("stock_qty")}\n
                        {data.get("item_code")} Delivered Bundle old: {old_value[0].get("delivered_bundle")}   new: {data.get("bundle")}\n
                        {data.get("item_code")} Delivered Pieces old: {old_value[0].get("delivered_pieces")}   new: {data.get("pieces")}\n\n\n
                        """
                        frappe.db.sql(f"""
                            UPDATE `tabDelivery Status`
                            SET 
                                delivered_stock_qty = {data.get("stock_qty")}, 
                                delivered_bundle = {data.get("bundle")},
                                delivered_pieces = {data.get("pieces")},
                                pending_qty__to_deliver = qty_to_deliver-{data.get("stock_qty")}
                            WHERE parenttype="Project" and parent="{sw}" and item="{data.get('item_code')}"
                        """)
                elif frappe.get_value("Item", data.get('item_code'), "item_group")=="Raw Material":
                    old_value=frappe.db.sql(f"""
                        SELECT delivered_quantity
                        FROM `tabRaw Materials`
                        WHERE  parenttype="Project" and parent="{sw}" and item="{data.get('item_code')}"
                    """, as_dict=True)
                    if old_value and old_value[0].get("delivered_quantity") != data.get("qty"):
                        log_content+=f"""
                        Site Work: {sw}\n
                        {data.get("item_code")} Delivered Raw Material old: {old_value[0].get("delivered_quantity")}   new: {data.get("qty")}\n\n\n
                        """
                        frappe.db.sql(f"""
                            UPDATE `tabRaw Materials`
                            SET 
                                delivered_quantity = {data.get("qty")}
                            WHERE parenttype="Project" and parent="{sw}" and item="{data.get('item_code')}"
                        """)

            total_returned_qty = frappe.db.sql(f""" select
                                        child.item_code,
                                        sum(child.stock_qty) as stock_qty,
                                        sum(child.qty) as qty,
                                        sum(child.ts_qty) as bundle,
                                        sum(child.pieces) as pieces
                                        from `tabDelivery Note` as doc
                                        left outer join `tabDelivery Note Item` as child
                                            on doc.name = child.parent
                                        where doc.docstatus = 1 and doc.site_work = '{sw}'  and doc.is_return = 1
                                        group by child.item_code
                                        """, as_dict=True)
            for data in total_returned_qty:
                if frappe.get_value("Item", data.get('item_code'), "item_group") in ["Pavers", "Compound Walls"]:
                    old_value=frappe.db.sql(f"""
                        SELECT returned_stock_qty, returned_bundle, returned_pieces
                        FROM `tabDelivery Status`
                        WHERE  parenttype="Project" and parent="{sw}" and item="{data.get('item_code')}"
                    """, as_dict=True)
                    if old_value and (old_value[0].get("returned_stock_qty") != data.get("stock_qty") or old_value[0].get("returned_bundle") != data.get("bundle") or old_value[0].get("returned_pieces") != data.get("pieces")):
                        log_content+=f"""
                        Site Work: {sw}\n
                        {data.get("item_code")} Returned Stock Qty old: {old_value[0].get("returned_stock_qty")}   new: {data.get("stock_qty")}\n
                        {data.get("item_code")} Returned Bundle old: {old_value[0].get("returned_bundle")}   new: {data.get("bundle")}\n
                        {data.get("item_code")} Returned Pieces old: {old_value[0].get("returned_pieces")}   new: {data.get("pieces")}\n\n\n
                        """
                        frappe.db.sql(f"""
                            UPDATE `tabDelivery Status`
                            SET 
                                returned_stock_qty = {data.get("stock_qty")}, 
                                returned_bundle = {data.get("bundle")},
                                returned_pieces = {data.get("pieces")}
                            WHERE parenttype="Project" and parent="{sw}" and item="{data.get('item_code')}"
                        """)
                elif frappe.get_value("Item", data.get('item_code'), "item_group")=="Raw Material":
                    old_value=frappe.db.sql(f"""
                        SELECT returned_quantity
                        FROM `tabRaw Materials`
                        WHERE  parenttype="Project" and parent="{sw}" and item="{data.get('item_code')}"
                    """, as_dict=True)
                    if old_value and old_value[0].get("returned_quantity") != data.get("qty"):
                        log_content+=f"""
                        Site Work: {sw}\n
                        {data.get("item_code")} Returned Raw Material old: {old_value[0].get("returned_quantity")}   new: {data.get("qty")}\n\n\n
                        """
                        frappe.db.sql(f"""
                            UPDATE `tabRaw Materials`
                            SET 
                                returned_quantity = {data.get("qty")}
                            WHERE parenttype="Project" and parent="{sw}" and item="{data.get('item_code')}"
                        """)
    except BaseException as e:
        log_content+=f"""\n\n{e}\n\n{frappe.get_traceback()}\n\nSITE WORK: {sw}\n\n{old_value}"""
    if log_content:
        frappe.log_error(title=f"SITE WORK DELIVERY QTY MISMATCH  {frappe.utils.now()}", message=f"""{log_content}""")
    return total_delivered_qty