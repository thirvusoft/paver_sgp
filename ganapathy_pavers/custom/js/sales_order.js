function setquery(frm){
    frm.set_query('item','pavers',function(frm){
        return {
            filters:{
                'is_sales_item':1,
                'item_group':'Pavers',
                'has_variants':0
            }
        }
    })
}

var prop_name;
frappe.ui.form.on('Sales Order',{
    refresh:function(frm){
        if(cur_frm.doc.is_multi_customer){
            cur_frm.set_df_property('customer','reqd',0);
        }
        else{
            cur_frm.set_df_property('customer','reqd',1);
        }
        setquery(frm)
        
        if(cur_frm.is_new()==1){
            frm.clear_table('items')
        }
        cur_frm.set_df_property('items','reqd',0);
        cur_frm.set_df_property('items','hidden',1);
        frm.set_query('supervisor', function(frm){
            return {
                filters:{
                    'designation': 'Supervisor'
                }
            }
        });
        frm.set_query('item','raw_materials',function(frm){
            return {
                filters:{
                    'item_group':'Raw Material'
                }
            }
        })
        if(cur_frm.doc.docstatus==0){
            cur_frm.fields_dict.site_work.$input.on("click", function() {
                if(!cur_frm.doc.customer && cur_frm.doc.is_multi_customer==0){
                    frappe.throw('Please Select Customer')
                }
            });
        }
    },
    customer:function(frm){
        cur_frm.set_value('site_work','')
        frm.set_query('site_work',function(frm){
            return {
                filters:{
                    'customer': cur_frm.doc.customer,
                    'status': 'Open',
                    'is_multi_customer':cur_frm.doc.is_multi_customer
                }
            }
        })
    },
    site_work:function(frm){
        cur_frm.set_value('project',cur_frm.doc.site_work)
    },
    type:function(frm){
        setquery(frm)
    },
    before_save:async function(frm){
        if(cur_frm.doc.is_multi_customer){
            cur_frm.set_value('customer','');
            await frappe.call({
                "method":"ganapathy_pavers.custom.py.sales_order.create_property",
                "callback":function(r){
                    prop_name=r.message;
                }
            })
        }
        else{
            frm.clear_table("customers_name");
        }

        frm.clear_table("items");
        if(cur_frm.doc.type=='Pavers'){
            let rm= cur_frm.doc.pavers?cur_frm.doc.pavers:[]
            for(let row=0;row<rm.length;row++){
                var message;
                var new_row = frm.add_child("items");
                new_row.item_code=cur_frm.doc.pavers[row].item
                //new_row.ts_qty=cur_frm.doc.pavers[row].allocated_paver_area
                new_row.qty=cur_frm.doc.pavers[row].number_of_bundle
                new_row.area_per_bundle=cur_frm.doc.pavers[row].area_per_bundle
                new_row.rate=cur_frm.doc.pavers[row].rate
                new_row.amount=cur_frm.doc.pavers[row].amount
                await frappe.call({
                    method:'ganapathy_pavers.custom.py.sales_order.get_item_value',
                    args:{
                        'doctype':cur_frm.doc.pavers[row].item,
                    },
                    callback: function(r){
                        message=r.message;
                        new_row.item_name=message['item_name']
                        new_row.uom=message['uom']
                        new_row.description=message['description']
                        new_row.conversion_factor=message['uom_conversion']
                    }
                })
                new_row.warehouse=cur_frm.doc.set_warehouse
                new_row.delivery_date=cur_frm.doc.delivery_date
                new_row.work=cur_frm.doc.pavers[row].work
            }
        }
        let rm= cur_frm.doc.raw_materials?cur_frm.doc.raw_materials:[]
        for(let row=0;row<rm.length;row++){
            var message;
            var new_row = frm.add_child("items");
            new_row.item_code=cur_frm.doc.raw_materials[row].item
            new_row.qty=cur_frm.doc.raw_materials[row].qty
            new_row.uom=cur_frm.doc.raw_materials[row].uom
            new_row.rate=cur_frm.doc.raw_materials[row].rate
            new_row.amount=cur_frm.doc.raw_materials[row].amount
            await frappe.call({
                method:'ganapathy_pavers.custom.py.sales_order.get_item_value',
                args:{
                    'doctype':cur_frm.doc.raw_materials[row].item,
                },
                callback: function(r){
                    message=r.message;
                    new_row.item_name=message['item_name']
                    new_row.description=message['description']
                }
            })
            
            new_row.warehouse=cur_frm.doc.set_warehouse
            new_row.delivery_date=cur_frm.doc.delivery_date
            
        }
       
            
           
        refresh_field("items");
    },
    after_save:function(frm){
        if(cur_frm.doc.is_multi_customer){
            frappe.call({
                "method":"ganapathy_pavers.custom.py.sales_order.remove_property",
                "args":{
                    'prop_name':prop_name
                }
            })
        }
    },
    on_submit:function(frm){
        frappe.call({
            method:"ganapathy_pavers.custom.py.sales_order.create_site",
            args:{
                doc: cur_frm.doc
            },
            callback: function(r){
                if(r.message){ 
                        frappe.show_alert({message: __("Site Work Updated Successfully"),indicator: 'green'});
                      }
                else{
                    frappe.show_alert({message: __("Couldn't Update Site Work"),indicator: 'red'});
                    }
                }
        })
    },
    is_multi_customer: function(frm){
        cur_frm.set_value('site_work','')
        if(cur_frm.doc.is_multi_customer){
            cur_frm.set_df_property('customer','reqd',0);
            frm.set_query('site_work',function(frm){
                return {
                    filters:{
                        'status': 'Open',
                        'is_multi_customer':cur_frm.doc.is_multi_customer
                    }
                }
            })
        }
        else{
            cur_frm.set_df_property('customer','reqd',1);
            frm.set_query('site_work',function(frm){
                return {
                    filters:{
                        'customer': cur_frm.doc.customer,
                        'status': 'Open',
                        'is_multi_customer':cur_frm.doc.is_multi_customer
                    }
                }
            })
        }
    }
})







frappe.ui.form.on('TS Raw Materials',{
    item: function(frm,cdt,cdn){
        let row=locals[cdt][cdn]
        if(row.item){
            frappe.db.get_doc('Item',row.item).then((item)=>{
                frappe.model.set_value(cdt,cdn,'rate', item.standard_rate);
                frappe.model.set_value(cdt,cdn,'uom', item.stock_uom);
            })
        }
    },
    rate: function(frm,cdt,cdn){
        amount_rawmet(frm,cdt,cdn)
    },
    qty: function(frm,cdt,cdn){
        amount_rawmet(frm,cdt,cdn)
    }

})


function amount_rawmet(frm,cdt,cdn){
    let row=locals[cdt][cdn]
    frappe.model.set_value(cdt,cdn,'amount', (row.rate?row.rate:0)*(row.qty?row.qty:0))
}