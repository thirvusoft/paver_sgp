frappe.ui.form.on("Payment Entry",{
    onload_post_render: function(frm) {
        if(frm.is_new()) {
            frm.set_value("branch", "")
        }
    },
    party: function(frm){
        if(frm.doc.party_type=="Customer" && frm.doc.party)
        cur_frm.set_query("site_work",function(){
            let party=frm.doc.party
            return {
                "filters": {
                    "customer":party
                }
            
        }

        })
        
    
    
    
        cur_frm.set_value('project', cur_frm.doc.site_work)
    },
    sales_taxes_and_charges_template: function(frm) {
        if(frm.doc.branch) {
            frappe.db.get_value("Branch", frm.doc.branch, "is_accounting").then( value => {
                if (!value.message.is_accounting) {
                    if(frm.doc.sales_taxes_and_charges_template)
                        frm.set_value("sales_taxes_and_charges_template", "")
                    if(frm.doc.taxes)
                        frm.clear_table("taxes")
                        refresh_field("taxes")
                }
            })
        }
    },
    branch: function (frm) {
        frm.trigger("sales_taxes_and_charges_template")
    },
    validate: function(frm) {
        frm.trigger("sales_taxes_and_charges_template")
    }
})