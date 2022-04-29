import frappe

@frappe.whitelist()
def get_link(doc):
    job_card = frappe.get_all("Job Card", filters={'work_order':doc},pluck = 'name')
    return "/app/job-card/"+job_card[0]


@frappe.whitelist()
def get_linked_jobcard(name):
    job_card = frappe.get_all("Job Card",filters={'work_order':name},pluck='total_completed_qty')
    if(len(job_card)):
        return job_card[0]