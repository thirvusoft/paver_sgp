import frappe

def execute():
    for doc in frappe.get_all("Project"):
        self=frappe.get_doc("Project", doc)
        jw_items={}
        total_layed_sqft=0
        total_layed_bundle=0
        for row in self.job_worker:
            if not row.other_work:
                total_layed_sqft+=(row.sqft_allocated or 0)
                total_layed_bundle+=(row.completed_bundle or 0)
            if(row.item and not row.other_work):
                if(row.item not  in jw_items):
                    jw_items[row.item]={'square_feet': 0, "bundle": 0}
                jw_items[row.item]['square_feet']+=(row.sqft_allocated or 0)
                jw_items[row.item]['bundle']+=(row.completed_bundle or 0)
        for row in self.delivery_detail:
            if row.item in jw_items:
                row.layed_sqft=jw_items[row.item]['square_feet']
                row.layed_bundle=jw_items[row.item]['bundle']
                row.save()
        self.total_layed_sqft=total_layed_sqft
        self.total_layed_bundle=total_layed_bundle
        self.db_update()