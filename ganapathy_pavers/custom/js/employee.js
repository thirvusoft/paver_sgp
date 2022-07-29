frappe.ui.form.on('Employee',{
    onload:function(frm){
        frm.set_query("designation",function(frm)
        {
            return{
                filters:{
                    "name":["in",["Labour Worker","Operator"]]
                }
            }
        })
        frm.set_query("department",function(frm)
        {
            return{
                filters:{
                    "name":["in",["Compount Wall - GP","Paver - GP"]]
                }
            }
        })
    },
})