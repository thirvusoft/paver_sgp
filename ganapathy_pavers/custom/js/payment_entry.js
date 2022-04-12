frappe.ui.form.on("Payment Entry",{
    site: function(frm){
        frm.set_query("site",function(){
            let party=frm.doc.party
            return {
                "filters": {
                    "customer":party
                }
            }
        })
    }
})