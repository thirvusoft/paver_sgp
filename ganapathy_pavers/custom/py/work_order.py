import frappe

@frappe.whitelist()
def get_link(doc):
    job_card = frappe.get_all("Job Card", filters={'work_order':doc},pluck = 'name')
    return "/app/job-card/"+job_card[-1]


@frappe.whitelist()
def get_linked_jobcard(name):
    job_card = frappe.get_all("Job Card",filters={'work_order':name},pluck='total_completed_qty')
    if(len(job_card)):
        return job_card[0]

@frappe.whitelist()
def get_child_work_order_status(parent):
    child_status = []
    child = ""
    child_name=[parent]
    while(True):
        child_docs=frappe.db.sql(f''' 
            SELECT name AS work_order, status
            FROM `tabWork Order`
            WHERE parent_work_order = "{child_name[-1]}"
        ''', as_dict=1)
        frappe.errprint(child_docs)
        if(len(child_docs)):
            for i in child_docs:
                child_name.append(i['work_order'])
            child_status.append(child_docs[0])
        else:
            break
    return child_status

def change_status(wo, action=None):
    jc_completed_qty = sum(frappe.get_all("Job Card", filters={'work_order':wo}, pluck='total_completed_qty'))
    from frappe.utils import flt
    work_order = frappe.get_doc("Work Order", wo)
    status = work_order.status
    if work_order.docstatus==0:
        status = 'Draft'
    elif work_order.docstatus==1:
        if status != 'Stopped':
            stock_entries = True
            status = "Not Started"
            if stock_entries:
                status = "In Process"
                # produced_qty = stock_entries.get("Manufacture")
                if flt(jc_completed_qty) >= flt(work_order.qty):
                    status = "Completed"
    else:
        status = 'Cancelled'
    work_order.status = status
    work_order.save('Update')



def before_submit(doc,action):
    from frappe.utils import get_link_to_form
    if(doc.parent_work_order):
        parent=doc.parent_work_order
        if(frappe.db.get_value("Work Order",parent,'status') in ['Draft','Not Started','Cancelled']):
            frappe.throw(f"Work Order "+frappe.bold(get_link_to_form("Work Order",parent))+" is not Completed. Complete that workorder to submit this workorder.")
