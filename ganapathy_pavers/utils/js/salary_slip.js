var salary_balance,standard_hrs=0;
frappe.ui.form.on('Salary Slip',{
    employee:function(frm,cdt,cdn){
        frm.trigger("get_mess_amount");
        if(frm.doc.designation=='Job Worker' && frm.doc.start_date && frm.doc.end_date){
            frappe.db.get_doc('Employee', frm.doc.employee).then((doc) => {
                salary_balance=doc.billed_salary_balance
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
                    frm.set_value("unbilled_salary_balance", r.message['unbilled_salary_balance'])
                    frm.set_value("total_undeducted_advance", r.message['undeducted_advances'])
                    frm.set_value("last_salary_slip_date", r.message['last_salary_slip_date'])
                    frm.clear_table('site_work_details');
                    for (let data in r.message["site_work"]){
                        total_amount = total_amount+r.message["site_work"][data][1]
                        total_unpaid_amount=total_unpaid_amount+r.message["site_work"][data][1]
                        var child = cur_frm.add_child("site_work_details");
                        frappe.model.set_value(child.doctype, child.name, "site_work_name", r.message["site_work"][data][0])     
                        frappe.model.set_value(child.doctype, child.name, "amount",r.message["site_work"][data][1] )
                    }
                    cur_frm.refresh_field("site_work_details")
                    cur_frm.set_value("total_paid_amount",paid_amount);
                    cur_frm.set_value("total_amount",total_amount);
                    cur_frm.set_value("total_unpaid_amount",(frm.doc.total_amount-frm.doc.total_paid_amount)+frm.doc.salary_balance);
                }
        })
        }
        else if(frm.doc.designation=='Contractor'){
            frm.trigger('employee_count');    
        }
        var date = frm.doc.end_date;
        var arr = date.split('-');
        frm.set_value('days',arr[2]) 
    },
    total_unpaid_amount: function(frm) {
        let unpaid_amount = (frm.doc.total_amount-frm.doc.total_paid_amount)+frm.doc.salary_balance
        if (unpaid_amount < 0) {
            frm.set_value("excess_amount_to_create_advance", -1 * (unpaid_amount || 0));
            frm.set_value("total_unpaid_amount", 0);
        } else {
            frm.set_value("excess_amount_to_create_advance", 0)
        }
    },
    designation: function (frm) {
        frm.trigger("get_mess_amount");
    },
    company: function (frm) {
        frm.trigger("get_mess_amount");
    },
    get_mess_amount: async function(frm) {
        let mess = 0;
        if (frm.doc.designation && frm.doc.company) {
            if (!((await frappe.db.get_value("Designation", frm.doc.designation, "no_mess_amount"))?.message?.no_mess_amount)) {
                mess = (await frappe.db.get_value("Company", frm.doc.company, "mess_charge_per_month"))?.message?.mess_charge_per_month
            }
        }
        cur_frm.set_value("mess", mess)
    },
    unbilled_salary_balance: function(frm) {
        frm.set_value("salary_balance", (frm.doc.billed_salary_balance || 0) + (frm.doc.unbilled_salary_balance || 0));
    },
    billed_salary_balance: function(frm) {
        frm.trigger("unbilled_salary_balance");
    },
    calculate_amount_to_pay: function(frm) {
        frm.set_value("amount_to_pay", 
            (frm.doc.salary_balance || 0)
            +(frm.doc.total_amount || 0)
            -(frm.doc.total_deduction || 0)
        )
    },
    total_amount: function(frm) {
        frm.trigger("calculate_amount_to_pay");
    },
    employee_count:function(frm){
        frappe.db.get_list("Salary Slip", {
            filters: { 'status': 'Submitted','designation':'Labour Worker'},
            fields: ["name",'end_date','start_date','total_working_hours']
        }).then((data) => {
            let total_hours=0
            for(let val=0;val<=data.length;val++){
                if(data[val].start_date>=frm.doc.start_date && data[val].start_date<=frm.doc.end_date && data[val].end_date>=frm.doc.start_date && data[val].end_date<=frm.doc.end_date){
                    total_hours+=data[val].total_working_hours
                }
                let exit=0;
                let earnings = frm.doc.earnings
                for (let data in earnings){
                    if(earnings[data].salary_component=='Contractor Welfare'){
                        frappe.db.get_value("Company", {"name": frm.doc.company}, "contractor_welfare_commission", (r) => {
                            frappe.model.set_value(earnings[data].doctype,earnings[data].name,'amount',total_hours*r.contractor_welfare_commission)
                        });
                        exit=1
                    }
                    cur_frm.refresh_field("earnings")
                }   
                if(exit==0){
                    var child = cur_frm.add_child("earnings");
                    frappe.model.set_value(child.doctype, child.name, "salary_component",'Contractor Welfare') 
                    setTimeout(() => {    
                        frappe.db.get_value("Company", {"name": frm.doc.company}, "contractor_welfare_commission", (r) => {
                            frappe.model.set_value(child.doctype,child.name,'amount',total_hours*r.contractor_welfare_commission)
                        });
                        cur_frm.refresh_field("earnings")}, 100);
                }   
            }         
        });
    },
    start_date: function (frm) {
        cur_frm.trigger('employee')
       frm.trigger("__days_calc");
    },
    end_date: function (frm) {
        cur_frm.trigger('employee')
        frm.trigger("__days_calc");
    },
    __days_calc: function(frm) {
        if (frm.doc.start_date && frm.doc.end_date) {
            frm.set_value("days", moment(frm.doc.end_date).diff(frm.doc.start_date, "days")+1)
        } else {
            frm.set_value("days", 0)
        }
    },
    days: function (frm) {
        frm.trigger("__days_calc");
    },
    total_time_of_food_taken:function(frm){
        var emp = frm.doc.employee
        cur_frm.set_value('employee','')
        cur_frm.set_value('employee',emp)
    },
    paid_amount: function(frm) {
        frm.set_value('total_paid_amount', frm.doc.paid_amount+frm.doc.total_deduction)
    },
    validate: function(frm) {
        frm.trigger("paid_amount")
        frm.trigger("total_unpaid_amount")
    },
    total_deduction: function(frm) {
        frm.trigger("calculate_amount_to_pay");
        frm.trigger("paid_amount")
    },
    salary_balance: function(frm) {
        frm.set_value('total_unpaid_amount',(frm.doc.total_amount-frm.doc.total_paid_amount)+frm.doc.salary_balance) 
        frm.trigger("calculate_amount_to_pay");
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
    },
});

frappe.ui.form.on("Salary Detail", {
    deductions_add: function(frm, cdt, cdn) {
        frm.trigger("calculate_amount_to_pay");
        frm.trigger('paid_amount')
    },
    deductions_remove: function(frm, cdt, cdn) {
        frm.trigger("calculate_amount_to_pay");
        frm.trigger('paid_amount')
    },
    amount: function(frm, cdt, cdn) {
        frm.trigger("calculate_amount_to_pay");
        frm.trigger('paid_amount')
    },
})
