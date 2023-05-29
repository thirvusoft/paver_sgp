var change_value=1, delete_value=1;
frappe.ui.form.on('TS Employee Attendance Tool',{
    onload: async function(frm){
        frappe.realtime.on('ts_clear_dialogs', async function(){
            while(cur_dialog){
                if(cur_dialog.title == "Confirm" && cur_frm.doctype == 'TS Employee Attendance Tool'){
                    await cur_dialog.hide()
                }
                else{
                    break
                }
            }
        })
        frappe.realtime.on('ts_update_settings', async function(){
            await frappe.db.get_single_value('Attendance Tool Settings', 'change_confirm').then( async value => {
                change_value = value;
            })
            await frappe.db.get_single_value('Attendance Tool Settings', 'delete_confirm').then( async value => {
                delete_value = value;
            })
        })
        await frappe.db.get_single_value('Attendance Tool Settings', 'change_confirm').then( async value => {
            change_value = value;
        })
        await frappe.db.get_single_value('Attendance Tool Settings', 'delete_confirm').then( async value => {
            delete_value = value;
        })
        if(cur_frm.is_new()){
            frappe.db.exists('Location', 'Unit1').then(res => {
                if(res){
                    cur_frm.set_value('location', 'Unit1')
                }
            })
            frappe.db.exists('Designation', 'Labour Worker').then(res => {
                if(res){
                    cur_frm.set_value('designation', 'Labour Worker')
                }
            })
        }
        frm.set_query('machine', function(frm){
            return {
                filters: {
                    'location': cur_frm.doc.location
                }
            }
        })
        frm.set_query('machine', 'employee_detail', function(frm, cdt, cdn){
            return {
                filters: {
                    'location': locals[cdt][cdn].location
                }
            }
        })
        frm.set_query('employee', 'employee_detail', function(frm, cdt, cdn){
            return {
                filters: {
                    'status': 'Active'
                }
            }
        });
        frm.add_custom_button("Get Employees", () => get_data(frm));
    },
    onload_post_render: async function(frm){
        if (cur_frm.is_new()) {
            return
        } 
        let table = (cur_frm.doc.employee_detail?cur_frm.doc.employee_detail:[])
        for(let row=0; row<table.length; row++){
            if(table[row].employee){
                let docfield = cur_frm.fields_dict.employee_detail.grid.grid_rows[row].docfields?cur_frm.fields_dict.employee_detail.grid.grid_rows[row].docfields:[]
                let employee_idx;
                for(let df=0; df<docfield.length; df++){
                    if(docfield[df].fieldname=="employee"){
                        employee_idx=df
                        break
                    }
                }
                if(employee_idx>=0){
                    await frappe.call({
                        method: "ganapathy_pavers.custom.py.employee_atten_tool.row_delete",
                        args: {
                            "employee":table[row].employee,
                            "name":cur_frm.doc.name
                        }, 
                        callback: async function(r){
                            if(r.message){
                                cur_frm.fields_dict.employee_detail.grid.grid_rows[row].docfields[employee_idx].read_only=1
                                await cur_frm.fields_dict.employee_detail.grid.refresh()
                            }
                        }
                    })
                }
            }
        }
    },
    
    after_save: async function(){
        cur_frm.reload_doc()
    },
    hours_to_reduce: function(frm) {
        (frm.doc.employee_detail || []).forEach(row => {
            frappe.model.set_value(row.doctype, row.name, "hours_to_reduce", frm.doc.hours_to_reduce);
        })
    },
    update:function(frm,cdt,cdn){
        if (cur_frm.doc.employee && cur_frm.doc.updated_checkout){
                frappe.call({
                    method:"ganapathy_pavers.custom.py.employee_atten_tool.help_section",
                    args:{
                        emp: cur_frm.doc.employee,
                        emp_tabl : cur_frm.doc.employee_detail?cur_frm.doc.employee_detail:[]
                    },
                    callback(r){
                        if(r.message){
                            frappe.confirm(__("Are you sure to change the employee checkin time?"), function () {
                                cur_frm.doc.employee_detail[r.message.idx -1].check_out = cur_frm.doc.updated_checkout
                                cur_frm.refresh_field('employee_detail')
                            })
                        }
                    }
                })
            } 
    },
   
    update_checkin:function(frm, cdt,cdn){
        if (cur_frm.is_new()){
            for (var i =0; i < cur_frm.doc.employee_detail.length; i++){
                let data = locals[cur_frm.doc.employee_detail[i].doctype][cur_frm.doc.employee_detail[i].name]
                if(cur_frm.doc.update_empty_fields && data.check_in){
                    continue
                } 
                frappe.model.set_value(cur_frm.doc.employee_detail[i].doctype, cur_frm.doc.employee_detail[i].name, "check_in", cur_frm.doc.date)
            }
        }
        else{
            frappe.confirm(__("Are you sure to change all employee checkin time?"), function () {
                for (var i =0; i < cur_frm.doc.employee_detail.length; i++){
                    let data = locals[cur_frm.doc.employee_detail[i].doctype][cur_frm.doc.employee_detail[i].name]
                    if(cur_frm.doc.update_empty_fields && data.check_in){
                        continue
                    }
                    cur_frm.doc.employee_detail[cur_frm.doc.employee_detail[i].idx -1].check_in = cur_frm.doc.date
                    cur_frm.refresh_field('employee_detail')
    
                //    frappe.model.set_value(cur_frm.doc.employee_detail[i].doctype, cur_frm.doc.employee_detail[i].name, "check_in", cur_frm.doc.date)
                }
            })
        }
        
    },
    update_checkout:function(frm, cdt,cdn){
        if(cur_frm.is_new()){
            for (var i =0; i < cur_frm.doc.employee_detail.length; i++){
                let data = locals[cur_frm.doc.employee_detail[i].doctype][cur_frm.doc.employee_detail[i].name]
                if(cur_frm.doc.update_empty_fields && data.check_out){
                    continue
                }
               frappe.model.set_value(cur_frm.doc.employee_detail[i].doctype, cur_frm.doc.employee_detail[i].name, "check_out", cur_frm.doc.checkout_time)
        }
    }
        else{
            frappe.confirm(__("Are you sure to change all employee checkout time?"), function () {
                for (var i =0; i < cur_frm.doc.employee_detail.length; i++){
                    let data = locals[cur_frm.doc.employee_detail[i].doctype][cur_frm.doc.employee_detail[i].name]
                    if(cur_frm.doc.update_empty_fields && data.check_in){
                        continue
                    }
                    cur_frm.doc.employee_detail[cur_frm.doc.employee_detail[i].idx -1].check_out = cur_frm.doc.checkout_time
                    cur_frm.refresh_field('employee_detail')
    
                //    frappe.model.set_value(cur_frm.doc.employee_detail[i].doctype, cur_frm.doc.employee_detail[i].name, "check_in", cur_frm.doc.date)
                }
            })
        }
        
},
    update_selected_checkins:async function(frm, cdt, cdn){
        if(cur_frm.doc.checkin){
            let employees = cur_frm.fields_dict.employee_detail.grid.get_selected_children()
            employees = employees?employees:[]
            let row = 0
            if (employees.length){
                await frappe.confirm(__("Are you sure to change the employee checkin time?"), function () {
                    for(row = 0; row<employees.length; row++){
                        cur_frm.doc.employee_detail[employees[row].idx -1].check_in = cur_frm.doc.checkin
                        // frappe.model.set_value(employees[row].doctype, employees[row].name, 'check_in', cur_frm.doc.checkin)
                    }
                    cur_frm.refresh_field('employee_detail')
                    frappe.show_alert({message: `Updated ${row} Checkins`})
                })

            }
        }
    },
    update_selected_checkouts:async function(frm, cdt, cdn){
        if(cur_frm.doc.checkout){
            let employees = cur_frm.fields_dict.employee_detail.grid.get_selected_children()
            employees = employees?employees:[]
            let row = 0
            if (employees.length){
                await frappe.confirm(__("Are you sure to change the employee checkout time?"), function () {
                    for(row = 0; row<employees.length; row++){
                        cur_frm.doc.employee_detail[employees[row].idx -1].check_out = cur_frm.doc.checkout
                        // frappe.model.set_value(employees[row].doctype, employees[row].name, 'check_out', cur_frm.doc.checkout)

                    }
                    cur_frm.refresh_field('employee_detail')
                    frappe.show_alert({message: `Updated ${row} Checkouts`})
                })

            }
        }
    }
})


function get_data(frm, cdt, cdn){
    frappe.call({
        method:"ganapathy_pavers.custom.py.employee_atten_tool.employee_finder_attendance",
        args:{
            designation: cur_frm.doc.designation,
            location: cur_frm.doc.location,
            machine: cur_frm.doc.machine,
            branch: cur_frm.doc.branch,
            company: cur_frm.doc.company
        },
        callback(r){
            frm.clear_table("employee_detail");
            for(var i=0;i<r.message.length;i++){
                var child = cur_frm.add_child("employee_detail");
                frappe.model.set_value(child.doctype, child.name, "employee", r.message[i]["name"])
                frappe.model.set_value(child.doctype, child.name, "hours_to_reduce", frm.doc.hours_to_reduce)
                frappe.model.set_value(child.doctype, child.name, "check_in", cur_frm.doc.date)
                frappe.model.set_value(child.doctype, child.name, "check_out", cur_frm.doc.checkout_time)
                frappe.model.set_value(child.doctype, child.name, "employee_name", r.message[i]["employee_name"])
                frappe.model.set_value(child.doctype, child.name, "location", r.message[i]["location"])
                frappe.model.set_value(child.doctype, child.name, "machine", r.message[i]["machine"])
                if (frm.doc.designation == "Labour Worker"){
                    frappe.model.set_value(child.doctype, child.name, "payment_method",'Deduct from Salary')
                }
                
            }
            cur_frm.refresh_field("employee_detail")
        }
    })
}

var validate=true;
async function change_checkin(frm,cdt,cdn, logtype){
    let row=locals[cdt][cdn];
    if(!row.check_in || !row.employee)return
    await frappe.call({
        method:"ganapathy_pavers.custom.py.employee_atten_tool.change_check_in",
        args:{
            employee: row.employee,
            logtype: logtype,
            name: cur_frm.doc.name,
            check_in: row.check_in,
            check_out: row.check_out
        },
        async:false,
        async callback(r){
            if (validate && !frm.is_new() && r.message){
                // validate=false
                if(change_value){
                    await frappe.confirm(
                        `Are you sure to change the employee check${logtype.toLocaleLowerCase()} time?`,
                        function(){
                            validate=true
                        },
                        function(){
                            validate=true
                            frappe.call({
                                method:"ganapathy_pavers.custom.py.employee_atten_tool.get_check_in",
                                args:{
                                    employee: row.employee,
                                    name: cur_frm.doc.name,
                                    logtype: logtype
                                },
                                callback(r){
                                    frappe.model.set_value(cdt, cdn, `check_${logtype.toLocaleLowerCase()}`, r.message)
                                }
                            })  
                        }
                    )
                }
                    
            }
        }
        
    })
}

async function not_permitted(frm, cdt, cdn){
    let row = locals[cdt][cdn]
    let emp_name=row.employee, employee_name=row.employee_name, checkin=row.check_in, checkout=row.check_out, location=row.location, machine=row.machine;
    let idx= row.idx
    if(row.employee && !cur_frm.is_new()){
        await frappe.call({
                method: "ganapathy_pavers.custom.py.employee_atten_tool.row_delete",
                args: {
                    employee: row.employee,
                    name: cur_frm.doc.name
                }, 
                callback: async function (r) {
                    if(r.message) {
                        if(delete_value){
                            frappe.confirm(`Checkin log is created for this employee: ${row.employee}\nAre you want to delete the checikn?`, 
                            function(){

                            }, 
                            async function(){
                                let new_row=cur_frm.fields_dict.employee_detail.grid.add_new_row(idx)
                                new_row.employee=emp_name
                                new_row.employee_name=employee_name
                                new_row.check_in=checkin
                                new_row.check_out=checkout
                                new_row.location=location
                                new_row.machine=machine
                            })
                        }
                    }
                }
        })
    }
}

frappe.ui.form.on('TS Employee Details', {
    check_in:function(frm,cdt,cdn){
        if (cur_frm.is_new()) {
            return
        } 
        change_checkin(frm,cdt,cdn, 'IN');
    },
    check_out:function(frm,cdt,cdn){
        if (cur_frm.is_new()) {
            return
        } 
        change_checkin(frm,cdt,cdn, 'OUT');
    },
    employee:function(frm,cdt,cdn){
        duplicate_entry(frm, cdt, cdn)
        let data=locals[cdt][cdn]
        if(data.employee){
            frappe.db.get_doc('Employee', data.employee).then((doc) => {
                frappe.model.set_value(cdt, cdn, 'location', doc.location)
                frappe.model.set_value(cdt, cdn, 'machine', doc.machine)
            })
        }
        else{
            frappe.model.set_value(cdt, cdn, 'location', '')
        }
    },
    before_employee_detail_remove: async function(frm, cdt, cdn) {
        if (cur_frm.is_new()) {
            return
        } 
        not_permitted(frm, cdt, cdn);
    },
    employee_detail_add: async function(frm, cdt, cdn){
        frappe.model.set_value(cdt, cdn, frm.doc.hours_to_reduce)
        duplicate_entry(frm, cdt, cdn)
        cur_frm.trigger('onload_post_render')
    }
})

function duplicate_entry(frm, cdt, cdn){
    let table = cur_frm.doc.employee_detail?cur_frm.doc.employee_detail:[]
        let employee_list=[]
        for(let row=0; row<table.length; row++){
            if(table[row].employee && employee_list.includes(table[row].employee)){
                frappe.msgprint(__(`Duplicate employee for an employee: ${table[row].employee}`))
                frappe.model.set_value(cdt, cdn, 'employee', '')
            }
            else if(table[row].employee){
                employee_list.push(table[row].employee)
            }
        }
}