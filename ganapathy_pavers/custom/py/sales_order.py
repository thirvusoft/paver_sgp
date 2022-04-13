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
    res=dict(
        project_name=doc['site_work'],
        type=doc['type'],
        customer=doc['customer'],
        sales_order=doc['name'],
        supervisor=doc['supervisor'],
        pavers=[{
                'item':row['item'],
                'required_area':row['required_area'],
                'area_per_bundle':row['area_per_bundle'],
                'number_of_bundle':row['number_of_bundle'],
                'allocated_paver_area':row['allocated_paver_area'],
                'rate':row['rate'],
                'amount':row['amount']
                } for row in doc['pavers']],
        raw_material=[{
                'item':row['item'],
                'qty':row['qty'],
                'uom':row['uom'],
                'rate':row['rate'],
                'amount':row['amount'],
                } for row in doc['raw_materials']],
    )
    return res
    
    

    
   