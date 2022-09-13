 // Thirvu_dual_Accounting
 frappe.ui.form.on("Purchase Invoice" ,{company:function(frm){
    if (frm.doc.company){
    frappe.call({
        method:"ganapathy_pavers.custom.py.sales_order.branch_list",
        args:{
            company:frm.doc.company
        },
        callback: function(r){
           
        frm.set_query('branch',function(frm){
            return{
                filters:{
                    'name':['in',r.message]
                }
            }
        
        })
        }
    })}},
})