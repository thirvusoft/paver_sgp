frappe.ui.form.on('TS Emloyee Attendance Tool',{
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
    before_save: async function(){
        await frappe.call({
            method:"ganapathy_pavers.custom.py.employee_atten_tool.attenance",
            args:{
                "table_list":cur_frm.doc.employee_detail?cur_frm.doc.employee_detail:'',
                atten_date: cur_frm.doc.date?cur_frm.doc.date:'',
                checkout: cur_frm.doc.checkout_time?cur_frm.doc.checkout_time:'',
                company: cur_frm.doc.company?cur_frm.doc.company:''
            },
            callback(r){
                console.log("win")
            }
        })
    },
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
                frappe.model.set_value(child.doctype, child.name, "employee_name", r.message[i]["employee_name"])
                if (frm.doc.designation == "Labour Worker"){
                    frappe.model.set_value(child.doctype, child.name, "payment_method",'Deduct from Salary')
                }
            }
            cur_frm.refresh_field("employee_detail")
        }
    })
}