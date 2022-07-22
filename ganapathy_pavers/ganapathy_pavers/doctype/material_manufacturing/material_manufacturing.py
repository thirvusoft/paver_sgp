# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class MaterialManufacturing(Document):
    def validate(doc):
        total_raw_material=[]
        total_cement = []
        total_ggbs2 = []
        for i in doc.raw_material_consumption:
            total_raw_material.append(i.total)
            total_cement.append(i.cm2_t)
            total_ggbs2.append(i.ggbs2_a)
        avg_raw_material = sum(total_raw_material)/len(total_raw_material)
        avg_cement = sum(total_cement)/len(total_cement)
        avg_ggbs2 = sum(total_ggbs2)/len(total_ggbs2)
        doc.total_no_of_raw_material = sum(total_raw_material)
        print(doc.total_no_of_raw_material,"-----------------")
        doc.total_no_of_cement = sum(total_cement)
        doc.total_no_of_ggbs2 = sum(total_ggbs2)
        doc.average_of_raw_material = avg_raw_material
        doc.average_of_cement = avg_cement
        doc.average_of__ggbs2 = avg_ggbs2
 
