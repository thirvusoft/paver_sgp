frappe.ui.form.on("Vehicle Log" ,{
    validate:function(frm){
        if(cur_frm.doc.service_item_table)
        {for(let i=0; i<cur_frm.doc.service_item_table.length; i++){
            if(cur_frm.doc.service_item_table[i].expense_amount==0){
                frappe.throw({title:"Missing Value", message: "Enter value for expense"})
            }
        }}
    }
});