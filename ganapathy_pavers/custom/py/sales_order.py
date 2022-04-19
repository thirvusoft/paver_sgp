from codecs import ignore_errors
import frappe
import json
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def get_item_value(doctype):
    res={
        'item_name':frappe.get_value('Item',doctype,'item_name'),
        'description':frappe.get_value('Item',doctype,'description'),
        'uom':frappe.get_value('Item',doctype,'sales_uom')
    }
    return res
    
@frappe.whitelist()
def create_site(doc):
    doc=json.loads(doc)
    supervisor=doc.get('supervisor_name') if('supervisor_name' in doc) else ''
    pavers=[{
            'item':row['item'],
            'required_area':row['required_area'],
            'area_per_bundle':row['area_per_bundle'],
            'number_of_bundle':row['number_of_bundle'],
            'allocated_paver_area':row['allocated_paver_area'],
            'rate':row['rate'],
            'amount':row['amount'],
            'work': doc['work'],
            'sales_order':doc['name']
            } for row in doc['pavers']]
    raw_material=[{
            'item':row['item'],
            'qty':row['qty'],
            'uom':row['uom'],
            'rate':row['rate'],
            'amount':row['amount'],
            'sales_order':doc['name']
            } for row in doc['raw_materials']]
    site_work=frappe.get_doc('Project',doc['site_work'])
    site_work.update({
        'supervisor_name': supervisor,
        'item_details': (site_work.get('item_details') or []) +pavers,
        'raw_material': (site_work.get('raw_material') or []) + raw_material
    })
    site_work.save()
    frappe.db.commit()
    return

    
