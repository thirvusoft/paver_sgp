frappe.ui.form.on('Salary Slip',{
    employee:function(frm,cdt,cdn){
        if(frm.doc.designation=='Job Worker'){
            frappe.call({
                method:"ganapathy_pavers.utils.py.salary_slip.site_work_details",
                args:{
                    employee:frm.doc.employee,
                    start_date:frm.doc.start_date,
                    end_date:frm.doc.end_date
                },
                callback:function(r){
                    let paid_amount = 0,total_unpaid_amount=0,total_amount=0;
                    frm.clear_table('site_work_details');
                    for (let data in r.message){
                        total_amount = total_amount+r.message[data][1]
                        total_unpaid_amount=total_unpaid_amount+r.message[data][1]
                        var child = cur_frm.add_child("site_work_details");
                        frappe.model.set_value(child.doctype, child.name, "site_work_name", r.message[data][0])     
                        frappe.model.set_value(child.doctype, child.name, "amount",r.message[data][1] )
                        frappe.model.set_value(child.doctype, child.name, "balance_amount",r.message[data][1] )   
                    }
                    cur_frm.refresh_field("site_work_details")
                    cur_frm.set_value("total_paid_amount",paid_amount);
                    cur_frm.set_value("total_amount",total_amount);
                    cur_frm.set_value("total_unpaid_amount",total_unpaid_amount);
                }
        })
        }     
    },
    total_paid_amount:function(frm){
        frm.set_value('total_unpaid_amount',frm.doc.total_amount-frm.doc.total_paid_amount) 
        let earnings = frm.doc.earnings
        for (let data in earnings){
            if(earnings[data].salary_component=='Basic'){
                frappe.model.set_value(earnings[data].doctype,earnings[data].name,'amount',frm.doc.total_paid_amount)
            }
            cur_frm.refresh_field("earnings")
        }      
    }
})
var set_totals = function(frm) {
	if (frm.doc.docstatus === 0 && frm.doc.doctype === "Salary Slip") {
		if (frm.doc.earnings || frm.doc.deductions) {
			frappe.call({
				method: "set_totals",
				doc: frm.doc,
				callback: function() {
					frm.refresh_fields();
				}
			});
		}
	}
};

frappe.ui.form.on('Site work Details',{
    paid_amount:function(frm,cdt,cdn){
        let row = locals[cdt][cdn];
        let amount_to_pay = 0
        let paid_data = frm.doc.site_work_details
        for (let value in paid_data){
            amount_to_pay+=paid_data[value].paid_amount
        }
        frappe.model.set_value(row.doctype,row.name, "balance_amount",row.amount - row.paid_amount )   
        frm.set_value('total_paid_amount',amount_to_pay)
        
}
})
