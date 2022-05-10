frappe.ui.form.on('Timesheet', {
    before_submit: function(frm) {
            frappe.db.get_value('Workstation', {'name':cur_frm.doc.workstation}, '_assign', function(r) {
                cur_frm.assign_to.add();
                cur_frm.assign_to.assign_to.dialog.set_values({assign_to:r._assign});
                setTimeout(() => {
                    frm.assign_to.assign_to.dialog.primary_action();
                }, 100);
			});
            frappe.db.get_single_value('HR Settings', 'standard_working_hours').then(value => { 
                if((frm.doc.total_hours-value)>0){
                    frm.set_value('overtime_hours',(frm.doc.total_hours-value))
                }
                else{
                    frm.set_value('overtime_hours',(frm.doc.total_hours))
                }
                }
                )   
        },
});
var exists=[];
frappe.ui.form.on('Timesheet Detail',{
    total_production_pavers:function(frm,cdt,cdn){
        let row=locals[cdt][cdn]
        if(exists.includes(row.item)){
            var qty_table=frm.doc.item_produced_quantity
            for (let data in qty_table){
                if(row.item==qty_table[data].item){
                    let existing_quantity=0
                    for (let val in frm.doc.time_logs){
                        if(frm.doc.time_logs[val].item==row.item){
                            existing_quantity+=frm.doc.time_logs[val].total_production_pavers
                        }
                    }
                    frappe.model.set_value(qty_table[data].doctype,qty_table[data].name,'quantity_produced',existing_quantity)
                    cur_frm.refresh_field("item_produced_quantity")
                }
            }
        }
        else{
            exists.push(row.item)
            var child = cur_frm.add_child("item_produced_quantity");
            frappe.model.set_value(child.doctype, child.name, "item", row.item)     
            frappe.model.set_value(child.doctype, child.name, "quantity_produced",row.total_production_pavers)
            cur_frm.refresh_field("item_produced_quantity")
        }
    }

})
