frappe.ui.form.on('TS Employee Attendance Tool',{
    department:function(frm, cdt, cdn){
        emp_detail(frm);
        get_data(frm, cdt, cdn)
    },
    designation:function(frm, cdt, cdn){
        emp_detail(frm);
        get_data(frm, cdt, cdn)
    },
    onload:function(frm){
        cur_frm.doc.date=frappe.datetime.now_datetime()
        emp_detail(frm);
    },
    on_submit: async function(){
        await frappe.call({
            method:"ganapathy_pavers.custom.py.employee_atten_tool.attenance",
            args:{
                "table_list":cur_frm.doc.employee_detail?cur_frm.doc.employee_detail:'',
                atten_date: cur_frm.doc.date?cur_frm.doc.date:'',
                checkout: cur_frm.doc.checkout_time?cur_frm.doc.checkout_time:'',
                company: cur_frm.doc.company?cur_frm.doc.company:'',
                ts_name:cur_frm.doc.name?cur_frm.doc.name:'',
            },
            
        })
    },
    update:function(frm,cdt,cdn){
        if (cur_frm.doc.employee){
            if (cur_frm.doc.updated_checkout){
                frappe.call({
                    method:"ganapathy_pavers.custom.py.employee_atten_tool.help_session",
                    args:{
                        emp: cur_frm.doc.employee,
                        upd_cout: cur_frm.doc.updated_checkout,
                        emp_tabl :cur_frm.doc.employee_detail
                    },
                    callback(r){
                        cur_frm.set_value("employee_detail", r.message)
                    }
                })
                
                    
            }
        } 
    },
    date:function(frm, cdt,cdn){
        for (var i =0; i < cur_frm.doc.employee_detail.length; i++){
           frappe.model.set_value(cur_frm.doc.employee_detail[i].doctype, cur_frm.doc.employee_detail[i].name, "check_in", cur_frm.doc.date)
    }},
    checkout_time:function(frm, cdt,cdn){
        for (var i =0; i < cur_frm.doc.employee_detail.length; i++){
           frappe.model.set_value(cur_frm.doc.employee_detail[i].doctype, cur_frm.doc.employee_detail[i].name, "check_out", cur_frm.doc.checkout_time)
    }}
})

function emp_detail(frm) {
    frm.set_query('employee','employee_detail',function() {
		return {
			filters: {
				'department': frm.doc.department,
                'designation': frm.doc.designation
			}
		}
	});
}

function get_data(frm, cdt, cdn){
    var advance=locals[cdt][cdn]
    var advance1=advance.designation
    frappe.call({
        method:"ganapathy_pavers.ganapathy_pavers.doctype.employee_advance_tool.employee_advance_tool.employee_finder_attendance",
        args:{
            designation: cur_frm.doc.designation,
            department: cur_frm.doc.department
        },
        callback(r){
            frm.clear_table("employee_detail");
            for(var i=0;i<r.message.length;i++){
                var child = cur_frm.add_child("employee_detail");
                frappe.model.set_value(child.doctype, child.name, "employee", r.message[i]["name"])
                frappe.model.set_value(child.doctype, child.name, "check_in", cur_frm.doc.date)
                frappe.model.set_value(child.doctype, child.name, "check_out", cur_frm.doc.checkout_time)
                frappe.model.set_value(child.doctype, child.name, "employee_name", r.message[i]["employee_name"])
                if (frm.doc.designation == "Labour Worker"){
                    frappe.model.set_value(child.doctype, child.name, "payment_method",'Deduct from Salary')
                }
                
            }
            cur_frm.refresh_field("employee_detail")
        }
    })
}