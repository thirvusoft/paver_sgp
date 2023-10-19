import frappe


def execute():
    update_vehicle_name()
    create_other_vehicle()

def update_vehicle_name():
    delivery_doc=frappe.get_all("Delivery Note",{"transporter":["!=","Own Transporter"]},pluck="name")
    for i in delivery_doc:
        delivery_note=frappe.get_doc("Delivery Note",i)
        a =delivery_note.vehicle_no
        if a:
            trimed_string=a.strip().split()
            camel_case=''.join(word.capitalize() for word in trimed_string)
            frappe.db.set_value("Delivery Note",i,"vehicle_no",camel_case,update_modified=False)


def create_other_vehicle():
    delivery_doc=frappe.get_all("Delivery Note",{"transporter":["!=","Own Transporter"]},pluck="vehicle_no",group_by="vehicle_no")
    for i in delivery_doc:
        
        if not frappe.db.exists("Other Vehicle",i) and i :
            doc = frappe.new_doc('Other Vehicle')
            doc.update({
                'vehicle': i
            })
            doc.flags.ignore_mandatory = True
            doc.save()