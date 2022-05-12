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
        if(len(child_docs)):
            for i in child_docs:
                child_name.append(i['work_order'])
            child_status.append(child_docs[0])
        else:
            break
    frappe.errprint(child_status)
    return child_status

