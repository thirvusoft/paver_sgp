import frappe
import json
from frappe.utils.csvutils import getlink
from ganapathy_pavers import uom_conversion

@frappe.whitelist()
def get_item_value(doctype):
    uom=frappe.get_doc('Item',doctype)
    conv=0
    if(uom.item_group=='Raw Material'):
        conv=1
    else:
        if(not uom.sales_uom):
                frappe.throw("Please Enter Sales Uom for an item:"+getlink('Item', doctype))
        for row in uom.uoms:
            if(row.uom==uom.sales_uom):
                conv=row.conversion_factor
        if(not conv):
            frappe.throw('Please enter UOM conversion for Square foot in item: '+getlink('Item', doctype))
    res={
        'item_name':frappe.get_value('Item',doctype,'item_name'),
        'description':frappe.get_value('Item',doctype,'description'),
        'uom':frappe.get_value('Item',doctype,'sales_uom'),
        'uom_conversion':conv
    }
    return res
    
@frappe.whitelist()
def create_site(doc):
    doc=json.loads(doc)
    if(doc.get('site_work')):
        create=False
        for row in (doc['items'] or []):
            if(row.get("work")!="Supply Only"):
                create=True
        if(create):
            supervisor=doc.get('supervisor_name') if('supervisor_name' in doc) else ''
            pavers=[]
            compoun_walls=[]
            pavers=[{
                    'item':row['item_code'],
                    'required_area':row['qty'],
                    'area_per_bundle':row['area_per_bundle'],
                    'number_of_bundle':row['ts_qty'],
                    'allocated_paver_area':row['qty'],
                    'uom': row['uom'],
                    'rate':row['rate'],
                    'amount':row['amount'],
                    'work': row.get('work'),
                    'sales_order':doc['name'],
                    'warehouse':row['warehouse'] if(row.get('warehouse')) else doc.get('set_warehouse'),
                    'stock_qty': row['stock_qty'],
                    'stock_uom': row['stock_uom']
                    } for row in doc['items'] if(row['item_group']=='Pavers')]
            compoun_walls=[{
                    'item':row['item_code'],
                    'compound_wall_type':row['compound_wall_type'],
                    'compound_wall_sub_type':row['compound_wall_sub_type'],
                    'allocated_ft':row['qty'],
                    'uom': row['uom'],
                    'rate':row['rate'],
                    'amount':row['amount'],
                    'work': row.get('work'),
                    'sales_order':doc['name'],
                    'warehouse':row['warehouse'] if(row.get('warehouse')) else doc.get('set_warehouse'),
                    'stock_qty': row['stock_qty'],
                    'stock_uom': row['stock_uom']
                    } for row in doc['items'] if(row['item_group']=='Compound Walls')]
            raw_material=[{
                    'item':row['item_code'],
                    'qty':row['qty'],
                    'uom':row['uom'],
                    'rate':row['rate'],
                    'amount':row['amount'],
                    'sales_order':doc['name'],
                    'stock_qty': row['stock_qty'],
                    'stock_uom': row['stock_uom'],
                    'customer_scope': row.get("customer_scope"),
                    'rate_inclusive': doc.get("rate_inclusive") if not row.get("customer_scope") else 0
                    } for row in doc['items'] if(row['item_group']=='Raw Material')]
            site_work=frappe.get_doc('Project',doc['site_work'])
            total_area=0
            completed_area=0
            
            for item in (site_work.get('item_details') or []):
                total_area+=item.required_area
            for item in pavers:
                total_area+=item['required_area']
            for item in (site_work.get('item_details_compound_wall') or []):
                total_area+=item.allocated_ft
            for item in compoun_walls:
                total_area+=item['allocated_ft']
            for item in (site_work.get('job_worker') or []):
                completed_area+=item.sqft_allocated
            
            site_work.update({
                'customer': (doc['customer'] or '') if(not doc.get('is_multi_customer')) else '',
                'type': doc.get('type'),
                'supervisor': doc.get('supervisor') if('supervisor' in doc) else '',
                'supervisor_name': supervisor,
                'item_details': (site_work.get('item_details') or []) +pavers,
                'item_details_compound_wall': (site_work.get('item_details_compound_wall') or []) +compoun_walls,
                'raw_material': (site_work.get('raw_material') or []) + raw_material,
                'total_required_area': total_area,
                'total_completed_area': completed_area,
                'completed': ((completed_area/total_area)*100) if(total_area) else 0,
                'distance':(site_work.get('distance') or 0)+(doc.get('distance') or 0)
            })
            if(doc['is_multi_customer']):
                sw_cust=[cus.customer for cus in (site_work.get('customer_name') or [] )]
                customer=[]
                for cust in doc['customers_name']:
                    if(cust['customer'] not in sw_cust):
                        customer.append({'customer':cust['customer']})
                site_work.update({
                    'customer_name': (site_work.get('customer_name') or [] ) + customer
                })
            site_work.save()
            frappe.db.commit()
            return 1


def update_site(doc, event):
    if(doc.get('site_work')):
        create=False
        for row in (doc.items or []):
            if(row.get("work")!="Supply Only"):
                create=True
        supervisor=doc.get('supervisor_name') or ''
        pavers=[]
        compoun_walls=[]
        raw_material=[]
        if(create):
            pavers=[{
                    'item':row.item_code,
                    'required_area':row.qty,
                    'area_per_bundle':row.area_per_bundle,
                    'number_of_bundle':row.ts_qty,
                    'allocated_paver_area':row.qty,
                    'uom': row.uom,
                    'rate':row.rate,
                    'amount':row.amount,
                    'work': row.get('work'),
                    'sales_order':doc.name,
                    'warehouse':row.warehouse if(row.get('warehouse')) else doc.get('set_warehouse'),
                    'stock_qty': row.stock_qty,
                    'stock_uom': row.stock_uom
                    } for row in doc.items if(row.item_group=='Pavers')]
            compoun_walls=[{
                    'item':row.item_code,
                    'compound_wall_type':row.compound_wall_type,
                    'compound_wall_sub_type':row.compound_wall_sub_type,
                    'allocated_ft':row.qty,
                    'uom': row.uom,
                    'rate':row.rate,
                    'amount':row.amount,
                    'work': row.get('work'),
                    'sales_order':doc.name,
                    'warehouse':row.warehouse if(row.get('warehouse')) else doc.get('set_warehouse'),
                    'stock_qty': row.stock_qty,
                    'stock_uom': row.stock_uom
                    } for row in doc.items if(row.item_group=='Compound Walls')]
            raw_material=[{
                    'item':row.item_code,
                    'qty':row.qty,
                    'uom':row.uom,
                    'rate':row.rate,
                    'amount':row.amount,
                    'sales_order':doc.name,
                    'stock_qty': row.stock_qty,
                    'stock_uom': row.stock_uom,
                    'customer_scope': row.get("customer_scope"),
                    'rate_inclusive': doc.get("rate_inclusive") if not row.get("customer_scope") else 0
                    } for row in doc.items if(row.item_group=='Raw Material')]
        site_work=frappe.get_doc('Project',doc.site_work)
        total_area=0
        completed_area=0
        
        sw_pavers=[]
        sw_cw=[]
        sw_rm=[]
        
        for item in (site_work.get('item_details') or []):
            if(item.get('sales_order') != doc.name):
                sw_pavers.append(item)
        for item in (site_work.get('item_details_compound_wall') or []):
            if(item.get('sales_order') != doc.name):
                sw_cw.append(item)
        for item in (site_work.get('raw_material') or []):
            if(item.get('sales_order') != doc.name):
                sw_rm.append(item)
        
        site_work.update({
            'item_details': sw_pavers,
            'item_details_compound_wall': sw_cw,
            'raw_material': sw_rm
        })

        for item in (site_work.get('item_details') or []):
            total_area+=item.required_area
        for item in pavers:
            total_area+=item['required_area']
        for item in (site_work.get('item_details_compound_wall') or []):
            total_area+=item.allocated_ft
        for item in compoun_walls:
            total_area+=item['allocated_ft']
        for item in (site_work.get('job_worker') or []):
            completed_area+=item.sqft_allocated
        
        site_work.update({
            'is_multi_customer': doc.get('is_multi_customer') or 0,
            'customer': (doc.customer or '') if(not doc.get('is_multi_customer')) else '',
            'supervisor': doc.get('supervisor') or '',
            'supervisor_name': supervisor,
            'item_details': (site_work.get('item_details') or []) +pavers,
            'item_details_compound_wall': (site_work.get('item_details_compound_wall') or []) +compoun_walls,
            'raw_material': (site_work.get('raw_material') or []) + raw_material,
            'total_required_area': total_area,
            'total_completed_area': completed_area,
            'completed': ((completed_area/total_area)*100) if(total_area) else 0,
            'distance':(site_work.get('distance') or 0)+(doc.get('distance') or 0)
        })
        if(doc.is_multi_customer):
            sw_cust=[cus.customer for cus in (site_work.get('customer_name') or [] )]
            customer=[]
            for cust in doc.customers_name:
                if(cust.customer not in sw_cust):
                    customer.append({'customer':cust.customer})
            site_work.update({
                'customer_name': (site_work.get('customer_name') or [] ) + customer
            })
        site_work.save()
        frappe.db.commit()
        return 1


@frappe.whitelist()
def item_price(item):
    if(item):
        rate=frappe.get_last_doc('Item Price',filters={'item_code':item, 'selling':1})
        rate=rate.price_list_rate
        return rate
    else:
        return 0

@frappe.whitelist()
def create_property():
    doc=frappe.new_doc('Property Setter')
    doc.update({
        "doctype_or_field": "DocField",
        "doc_type":"Sales Order",
        "field_name":"customer",
        "property":"reqd",
        "value":0
    })
    doc.save()
    frappe.db.commit()
    return doc.name
   
   
@frappe.whitelist()
def remove_property(prop_name):
    frappe.delete_doc('Property Setter',prop_name)
    frappe.db.commit()


@frappe.whitelist()
def update_temporary_customer(customer, sales_order):
    doc=frappe.get_doc('Sales Order',sales_order)
    frappe.db.set(doc, "customer", customer)

@frappe.whitelist()
def get_customer_list(sales_order):
    doc=frappe.get_doc('Sales Order', sales_order)
    customer=[cust.customer for cust in doc.customers_name]
    return '\n'.join(customer)
    
def remove_project_fields(self,event):
    project=self.site_work
    if(project):
        doc=frappe.get_doc('Project',project)
        paver=doc.get('item_details') or []
        cw=doc.get('item_details_compound_wall') or []
        raw_material=doc.get('raw_material')
        new_paver=[]
        new_cw=[]
        new_rm=[]
        delivery_detail=doc.delivery_detail
        for item in paver:
            if(item.sales_order!=self.name):
                new_paver.append(item)
            else:
                for row in delivery_detail:
                    if item.work!="Supply Only" and row.item == item.item:
                        row.qty_to_deliver -= item.stock_qty
                        row.pending_qty__to_deliver -= item.stock_qty
        for item in cw:
            if(item.sales_order!=self.name):
                new_cw.append(item)
            else:
                for row in delivery_detail:
                    if item.work!="Supply Only" and row.item == item.item:
                        row.qty_to_deliver -= item.stock_qty
                        row.pending_qty__to_deliver -= item.stock_qty
        for item in raw_material:
            if(item.sales_order!=self.name):
                new_rm.append(item)
                
                
        total_area=0
        completed_area=0
        for item in (new_paver or []):
            total_area+=(item.get('required_area') or 0)
        for item in (new_cw or []):
            total_area+=(item.get('allocated_ft') or 0)
        for item in (doc.get('job_worker') or []):
            completed_area+=(item.get('sqft_allocated') or 0)
        
        if(total_area):
            percent=(completed_area/total_area)*100
        else:
            percent=0
        doc.update({
            'item_details':new_paver,
            'item_details_compound_wall':new_cw,
            'raw_material':new_rm,
            'total_required_area': total_area,
            'total_completed_area': completed_area,
            'completed': percent,
            'delivery_detail': delivery_detail,
        })
        doc.save()
        

    

@frappe.whitelist()
def get_item_rate(item='', selling=1):
    if(not item or item not in frappe.get_all('Item Price', {'selling': selling}, pluck='item_code')):
        return 0
    doc=frappe.get_last_doc('Item Price', {'item_code': item, 'selling': selling})
    return doc.price_list_rate or 0


def item_table_pa_cw(self, event):
    types=self.type
    for i in self.items:
        if (types=="Pavers" and (i.item_group)=="Compound Walls"):
            frappe.throw(f"You can't select both {frappe.bold('Pavers')} and {frappe.bold('Compound Walls')}. Please remove the item: "+frappe.bold(i.item_code))
        elif (types=="Compound Wall" and (i.item_group)=="Pavers"):
            frappe.throw(f"You can't select both {frappe.bold('Pavers')} and {frappe.bold('Compound Walls')}. Please remove the item: "+frappe.bold(i.item_code))


@frappe.whitelist()
def update_branch(branch, name):
    frappe.db.set_value("Sales Order", name, 'branch', branch)

@frappe.whitelist()
def update_multicustomer(customers_name, sales_order):
	doc=frappe.new_doc('Property Setter')
	doc.update({
		"doctype_or_field": "DocField",
		"doc_type":"Sales Order",
		"field_name":"customers_name",
		"property":"allow_on_submit",
		"value":"1"
	})
	doc.save()
	doc1=frappe.new_doc('Property Setter')
	doc1.update({
		"doctype_or_field": "DocField",
		"doc_type":"Sales Order",
		"field_name":"customer",
		"property":"allow_on_submit",
		"value":"1"
	})
	doc1.save()
	doc2=frappe.new_doc('Property Setter')
	doc2.update({
		"doctype_or_field": "DocField",
		"doc_type":"Sales Order",
		"field_name":"is_multi_customer",
		"property":"allow_on_submit",
		"value":"1"
	})
	doc2.save()
	customers_name = [ {
		'customer': cus['customer'], 
		'doctype': 'TS Customer'
		} for cus in json.loads(customers_name)]
	self = frappe.get_doc('Sales Order', sales_order)
	self.is_multi_customer = 1
	if(frappe.db.exists('Customer', 'MultiCustomer')):
		self.update({
			'customer': 'MultiCustomer'
		})
	self.update({
		'customers_name' : customers_name
	})
	self.save('update')

	frappe.delete_doc('Property Setter', doc.name)
	frappe.delete_doc('Property Setter', doc1.name)
	frappe.delete_doc('Property Setter', doc2.name)

def check_branch(doc, event):
    if (doc.branch):
        value = frappe.db.get_value("Branch", doc.branch, "is_accounting")
        if (not value):
            for row in doc.items:
                frappe.db.set_value(row.doctype, row.name, 'unacc', 1)
                frappe.db.set_value(row.doctype, row.name, 'item_tax_template', '')
        else:
            for row in doc.items:
                frappe.db.set_value(row.doctype, row.name, 'unacc', 0)
        
def update_qty_and_required_unit(doc, event=None):
    doc.order_type = "Sales"
    for row in doc.items:
        if row.item_group in ['Pavers', 'Compound Walls']:
            row.db_set("ts_required_area_qty", uom_conversion(item = row.item_code, from_uom=row.uom, from_qty=row.qty, to_uom="SQF"))

def patch():
    for row in frappe.db.get_all("Sales Order Item", {"item_group": ["in", ["Pavers", "Compound Walls"]]}, ['name', 'item_code', 'qty', 'uom']):
        qty = uom_conversion(item = row.item_code, from_uom=row.uom, from_qty=row.qty, to_uom="SQF", throw_err=False)
        frappe.db.set_value("Sales Order Item", row.name, 'ts_required_area_qty', qty)

# from ganapathy_pavers.custom.py.sales_order import patch