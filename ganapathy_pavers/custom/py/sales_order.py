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
    for row in (doc['items'] or []):
        if(row.get("work")!="Supply Only"):
            create=True
    if(doc.get('work')!="Supply Only" and create):
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
                'stock_uom': row['stock_uom']
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
        for item in paver:
            if(item.sales_order!=self.name):
                new_paver.append(item)
        for item in cw:
            if(item.sales_order!=self.name):
                new_cw.append(item)
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
            'completed': percent
        })
        doc.save()
        frappe.db.commit()
        

    

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


