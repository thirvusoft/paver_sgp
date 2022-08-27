frappe.ui.form.on("Workstation",{
    get_employees: function(frm){
        if(frm.doc.designation){
            frappe.db.get_list("Employee",{fields:['name'],filters:{'designation':frm.doc.designation}}).then((data)=>{
                data.forEach(function(i){
                    let child = cur_frm.add_child('ts_labor')
                    child.ts_labour = i['name']
                })
                cur_frm.refresh();
            })
        }
    },
    // validate:function(frm){
    //     for(var i=0;i<frm.doc.ts_operator_table.length;i++){
    //         if(frm.doc.ts_operator_table[i].ts_division_operator == 0){
    //             frappe.throw("Zero is not allowed kindly give above zero in division factors")}
    //     }
    // },
    refresh:function(frm){
            frm.set_query('ts_operator_name','ts_operators_table',function(frm){
                return {
                    filters:{
                        "designation":"Operator",
                    }
                }
            })
        frm.set_query('ts_machine_operator',function(frm){
            return {
                filters:{
                    "designation":"Operator",
                }
            }
        })
        frm.set_query('ts_panmix_operator',function(frm){
            return {
                filters:{
                    "designation":"Operator",
                }
            }
        })
    },

})
frappe.ui.form.on("Ts Operators",{
    ts_operator_name:function(frm,cdt,cdn){
        var row = locals[cdt][cdn]
        frappe.call({
            method:'ganapathy_pavers.custom.py.workstation.operator_salary',
            args:{
                'operator':row.ts_operator_name
            },
            callback: function(r){
                frappe.model.set_value(cdt,cdn,"ts_operator_salary",r.message)
            }
        })
    },

    ts_division_operator:function(frm,cdt,cdn){
        var row = locals[cdt][cdn]
        if(row.ts_division_operator == 0){
            frappe.model.set_value(cdt,cdn,"ts_operator_wages",row.ts_division_operator)
            frappe.throw("Zero is not allowed kindly give above zero in division factors")
        }
        else
            frappe.model.set_value(cdt,cdn,"ts_operator_wages",row.ts_operator_salary / row.ts_division_operator)
    },

})

frappe.ui.form.on("Workstation",{
    cost_per_hours:function(frm){
        cur_frm.set_value("cal_wages1",(frm.doc.cost_per_hours*frm.doc.no_of_labours)/frm.doc.division_factors1) 
        cur_frm.set_value("ts_wages1",frm.doc.cost_per_hours/frm.doc.division_factors1) 
    },
    no_of_labours:function(frm){
        cur_frm.set_value("cal_wages1",(frm.doc.cost_per_hours*frm.doc.no_of_labours)/frm.doc.division_factors1) 
        cur_frm.set_value("ts_wages1",frm.doc.cost_per_hours/frm.doc.division_factors1) 
    },
    division_factors1:function(frm){
        if(frm.doc.division_factors1==0){
            cur_frm.set_value("cal_wages1",frm.doc.division_factors1)
            cur_frm.set_value("ts_wages1",frm.doc.cost_per_hours/frm.doc.division_factors1) 
            frappe.throw("Zero is not allowed kindly give above zero in division factors")}
        else
            cur_frm.set_value("cal_wages1",(frm.doc.cost_per_hours*frm.doc.no_of_labours)/frm.doc.division_factors1)
            cur_frm.set_value("ts_wages1",frm.doc.cost_per_hours/frm.doc.division_factors1) 
    }
})