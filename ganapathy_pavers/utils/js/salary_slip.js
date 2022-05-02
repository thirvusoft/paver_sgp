var salary_balance;
frappe.ui.form.on('Salary Slip',{
    employee:function(frm,cdt,cdn){
        if(frm.doc.designation=='Job Worker'){
            frappe.db.get_doc('Employee', frm.doc.employee).then((doc) => {
                salary_balance=doc.salary_balance
            });
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
                    cur_frm.set_value("total_unpaid_amount",(frm.doc.total_amount-frm.doc.total_paid_amount)+frm.doc.salary_balance);
                }
        })
        }
        var date = frm.doc.end_date;
        var arr = date.split('-');
        frm.set_value('days',arr[2])     
    },
    pay_the_balance:function(frm){
        if(frm.doc.pay_the_balance==1){
            frm.set_value('total_paid_amount',frm.doc.total_paid_amount+frm.doc.salary_balance)
            frm.set_value('total_amount',frm.doc.total_amount+frm.doc.salary_balance)
            frm.set_value('salary_balance',0)
        }
        else{
                frm.set_value('salary_balance',salary_balance)
                frm.set_value('total_paid_amount',frm.doc.total_paid_amount-frm.doc.salary_balance)
                frm.set_value('total_amount',frm.doc.total_amount-frm.doc.salary_balance)
        }

    },
    total_time_of_food_taken:function(frm){
        var emp = frm.doc.employee
        cur_frm.set_value('employee','')
        cur_frm.set_value('employee',emp)
    },
    total_paid_amount:function(frm){
        frm.set_value('total_unpaid_amount',(frm.doc.total_amount-frm.doc.total_paid_amount)+frm.doc.salary_balance) 
        let earnings = frm.doc.earnings
        var exit=0
        for (let data in earnings){
            if(earnings[data].salary_component=='Basic'){
                frappe.model.set_value(earnings[data].doctype,earnings[data].name,'amount',frm.doc.total_paid_amount)
                exit=1
            }
            cur_frm.refresh_field("earnings")
        }   
        if(exit==0){
            var child = cur_frm.add_child("earnings");
            frappe.model.set_value(child.doctype, child.name, "salary_component",'Basic') 
            setTimeout(() => {    
                frappe.model.set_value(child.doctype, child.name, "amount",frm.doc.total_paid_amount)
                cur_frm.refresh_field("earnings")            }, 100);
        }   
    }
})


frappe.ui.form.on('Site work Details',{
    paid_amount:function(frm,cdt,cdn){
        let row = locals[cdt][cdn];
        let amount_to_pay = 0
        let paid_data = frm.doc.site_work_details
        for (let value in paid_data){
            amount_to_pay+=paid_data[value].paid_amount
        }
        frappe.model.set_value(row.doctype,row.name, "balance_amount",row.amount - row.paid_amount)
        if(frm.doc.pay_the_balance){

            frm.set_value('total_paid_amount',salary_balance+amount_to_pay)
        }  
        else{
            frm.set_value('total_paid_amount',amount_to_pay)
        } 
        
}
})
