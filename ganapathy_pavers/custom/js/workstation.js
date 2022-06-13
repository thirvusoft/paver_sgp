frappe.ui.form.on("Workstation",{
    before_save:function(frm,cdt,cdn){
        var ts_data=locals[cdt][cdn]
        var ts_employee=[]
        for(var i=0;i<ts_data.ts_labor.length;i++){
            ts_employee.push(ts_data.ts_labor[i].ts_labour)
        }
        frappe.call({
            method:"ganapathy_pavers.custom.py.workstation.hour_salary_finder",
            args:{ts_employee},
            callback(ts_r){
                frm.set_value("hour_rate_labour",ts_r.message)
            }
        })
    }
})