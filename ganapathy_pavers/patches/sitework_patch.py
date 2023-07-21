import frappe
import sys

from ganapathy_pavers.utils.py.site_work import batch_customization

def execute():
    batch_customization()


def other_work():
    for i in frappe.get_all("Project", pluck="name"):
        self=frappe.get_doc("Project", i)
        total_area=0
        total_bundle=0
        paver_table=self.item_details
        compound_wall=self.item_details_compound_wall
        if paver_table:
            for i in paver_table:
                total_area+=i.required_area or 0
                total_bundle += i.number_of_bundle or 0
        if compound_wall:
            for i in compound_wall:
                total_area+=i.allocated_ft or 0
        completed_area=0
        total_comp_bundle=0
        job_worker=self.job_worker
        if job_worker:
            for i in job_worker:
                if(i.other_work ==0):
                    completed_area+=i.sqft_allocated or 0
                    total_comp_bundle +=i.completed_bundle or 0
        self.total_required_area=total_area
        self.total_completed_area=completed_area
        self.total_required_bundle=total_bundle
        self.total_completed_bundle=total_comp_bundle
        self.completed=(completed_area/total_area)*100 if total_area else 0
        self.db_update()
    
def update_excess_remaining_qty():
    sites = frappe.get_all("Project")
    n = 0
    for i in sites:
        n+=1
        sys.stdout.write(f"\r{n}/{len(sites)} Updating Sites")
        sys.stdout.flush()
        doc=frappe.get_doc("Project", i.name)
        doc.excess_or_remaining_qty = (doc.get('measurement_sqft') or 0) - sum([(row.get('delivered_stock_qty') or 0)+(row.get('returned_stock_qty') or 0) for row in (doc.get('delivery_detail') or [])])
        doc.db_update()
    sys.stdout.write(f"\r\n")
    sys.stdout.flush()

# ganapathy_pavers.patches.sitework_patch.update_excess_remaining_qty
