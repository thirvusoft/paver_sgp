from codecs import ignore_errors
import site
import frappe
import json
from frappe.model.mapper import get_mapped_doc
from frappe.utils.csvutils import getlink

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
    create=False
    if(doc['type']=='Pavers'):
        for row in (doc['pavers'] or []):
            if(row["work"]!="Supply Only"):
                create=True
    if(doc['type']=='Compound Wall'):
        for row in (doc['compoun_walls'] or []):
            if(row["work"]!="Supply Only"):
                create=True
    if(doc['work']!="Supply Only" and create):
        supervisor=doc.get('supervisor_name') if('supervisor_name' in doc) else ''
        pavers=[]
        compoun_walls=[]
        if(doc['type']=='Pavers'):
            pavers=[{
                    'item':row['item'],
                    'required_area':row['required_area'],
                    'area_per_bundle':row['area_per_bundle'],
                    'number_of_bundle':row['number_of_bundle'],
                    'allocated_paver_area':row['allocated_paver_area'],
                    'rate':row['rate'],
                    'amount':row['amount'],
                    'work': row['work'],
                    'sales_order':doc['name'],
                    'warehouse':row['warehouse'] if(row.get('warehouse')) else doc.get('set_warehouse')
                    } for row in doc['pavers']]
        if(doc['type']=='Compound Wall'):
            compoun_walls=[{
                    'item':row['item'],
                    'compound_wall_type':row['compound_wall_type'],
                    'allocated_ft':row['allocated_ft'],
                    'rate':row['rate'],
                    'amount':row['amount'],
                    'work': row['work'],
                    'sales_order':doc['name'],
                    'warehouse':row['warehouse'] if(row.get('warehouse')) else doc.get('set_warehouse')
                    } for row in doc['compoun_walls']]
        raw_material=[{
                'item':row['item'],
                'qty':row['qty'],
                'uom':row['uom'],
                'rate':row['rate'],
                'amount':row['amount'],
                'sales_order':doc['name']
                } for row in doc['raw_materials']]
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
            'customer': doc['customer'] or '',
            'supervisor': doc.get('supervisor') if('supervisor' in doc) else '',
            'supervisor_name': supervisor,
            'item_details': (site_work.get('item_details') or []) +pavers,
            'item_details_compound_wall': (site_work.get('item_details_compound_wall') or []) +compoun_walls,
            'raw_material': (site_work.get('raw_material') or []) + raw_material,
            'total_required_area': total_area,
            'total_completed_area': completed_area,
            'completed': (completed_area/total_area)*100,
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


@frappe.whitelist()
def item_price(item):
    rate=frappe.get_last_doc('Item Price',filters={'item_code':item, 'selling':1})
    rate=rate.price_list_rate
    return rate

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
        raw_material=doc.get('raw_material')
        new_paver=[]
        new_rm=[]
        for item in paver:
            if(item.sales_order!=self.name):
                new_paver.append(item)
        for item in raw_material:
            if(item.sales_order!=self.name):
                new_rm.append(item)
                
                
        total_area=0
        completed_area=0
        for item in (new_paver or []):
            total_area+=(item.get('required_area') or 0)
        for item in (doc.get('job_worker') or []):
            completed_area+=(item.get('sqft_allocated') or 0)
        
        if(total_area):
            percent=(completed_area/total_area)*100
        else:
            percent=0
        doc.update({
            'item_details':new_paver,
            'raw_material':new_rm,
            'total_required_area': total_area,
            'total_completed_area': completed_area,
            'completed': percent
        })
        doc.save()
        frappe.db.commit()
        
@frappe.whitelist()        
def get_sqrfoot_uom(item):
    doc=frappe.get_doc('Item', item)
    if(not doc.sales_uom):
        frappe.throw('Please Enter Sales UOM for an Item: '+getlink('Item', item))
    for uom in doc.uoms:
        if(uom.uom==doc.sales_uom):
            return {'uom': doc.sales_uom, 'qty': uom.conversion_factor}
    return {'uom': doc.sales_uom, 'qty': 0}
    

@frappe.whitelist()
def get_item_rate(item='', selling=1):
    if(not item or item not in frappe.get_all('Item Price', {'selling': selling}, pluck='item_code')):
        return 0
    doc=frappe.get_last_doc('Item Price', {'item_code': item, 'selling': selling})
    return doc.price_list_rate or 0