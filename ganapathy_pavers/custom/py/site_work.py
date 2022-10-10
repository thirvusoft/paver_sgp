import frappe
import json
from frappe.utils.csvutils import getlink
from frappe.utils import nowdate
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from ganapathy_pavers.custom.py.sales_order import get_item_rate
from ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing import uom_conversion


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
            bin_=frappe.get_value('Bin', {'warehouse': item.warehouse, 'item_code': item.item}, 'valuation_rate')
            item_cost+=(bin_ or 0)* (item.stock_qty or 0)

    for item in doc.item_details_compound_wall:
        if(item.get('warehouse')):
            bin_=frappe.get_value('Bin', {'warehouse': item.warehouse, 'item_code': item.item}, 'valuation_rate')
            item_cost+=(bin_ or 0)* (item.stock_qty or 0)

    for item in doc.raw_material:
        doc1=frappe.get_all('Item Price', {'buying':1, 'item_code': item.item}, ["price_list_rate", "uom"])
        if(doc1):
            if(not doc1[0].uom):
                doc1[0].uom=frappe.get_value('Item', item.item, 'stock_uom')
            if(item.stock_uom and doc1[0].uom):
                item_doc=frappe.get_doc('Item', item.item)
                conv=0
                for row in item_doc.uoms:
                    if(row.uom==doc1[0].uom):
                        conv=row.conversion_factor
                if(not conv):
                    frappe.throw(f'Please enter {doc1[0].uom} conversion for an item: '+frappe.bold(getlink('Item', item.item)))
                rm_cost+=(doc1[0]['price_list_rate'] or 0)*(item.stock_qty or 0)/conv
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
        delivered_item[row.item]+=row.delivered_stock_qty

    jw_items={}
    for row in self.job_worker:
        if(row.item):
            if(row.item not  in jw_items):
                jw_items[row.item]=0
            item_doc=frappe.get_doc('Item', row.item)
            conv_factor=[conv.conversion_factor for conv in item_doc.uoms if(conv.uom=='Square Foot')]
            if(not conv_factor):
                frappe.throw('Please enter Square Feet Conversion for an item: '+ frappe.bold(getlink('Item', row.item)))
            jw_items[row.item]+=float(row.sqft_allocated or 0)*conv_factor[0]
    wrong_items=[]
    for item in jw_items:
        if((jw_items.get(item) or 0)>(delivered_item.get(item) or 0)):
            wrong_items.append(frappe.bold(item))
    if(wrong_items):
        frappe.throw("Job Worker completed qty cannot be greater than Delivered Qty for the following items "+', '.join(wrong_items))
    
    if(self.type == "Compound Wall"):
        delivered_qty = 0
        for row in self.delivery_detail:
            if(row.item and frappe.get_value("Item", row.item, 'item_group') == "Compound Walls"):
                delivered_qty += uom_conversion(row.item, '', float(row.delivered_stock_qty), 'Square Foot')
        
        completed_qty = 0
        for row in self.job_worker:
            if((not row.item) or row.item_group == "Compound Walls"):
                completed_qty += float(row.sqft_allocated or 0)

        if(completed_qty > delivered_qty):
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
    
