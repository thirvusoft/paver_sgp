frappe.ui.form.on("Payment Entry",{
    site_work: function(frm){
        frm.set_query("site",function(){
            let party=frm.doc.party
            return {
                "filters": {
                    "customer":party
                }
            }
        })
        cur_frm.set_value('project', cur_frm.doc.site_work)
    }
})