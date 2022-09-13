frappe.ui.form.on('Sales Invoice Item', {
    ts_qty: function(frm,cdt,cdn){
        bundle_calc(frm, cdt, cdn)
    },
    conversion_factor: function(frm,cdt,cdn){
        bundle_calc(frm, cdt, cdn)
    },
    pieces: function(frm,cdt,cdn){
        bundle_calc(frm, cdt, cdn)
    }
})


async function bundle_calc(frm, cdt, cdn){
    let row = locals[cdt][cdn]
    let uom=row.uom
    let conv1
    let conv2
    await frappe.db.get_doc('Item', row.item_code).then((doc) => {
        let bundle_conv=1
        let other_conv=1;
        let nos_conv=1
        for(let doc_row=0; doc_row<doc.uoms.length; doc_row++){
            if(doc.uoms[doc_row].uom==uom){
                other_conv=doc.uoms[doc_row].conversion_factor
            }
            if(doc.uoms[doc_row].uom=='bundle'){
                bundle_conv=doc.uoms[doc_row].conversion_factor
            }
            if(doc.uoms[doc_row].uom=='Nos'){
                nos_conv=doc.uoms[doc_row].conversion_factor
            }
        }
        conv1=bundle_conv/other_conv
        conv2=nos_conv/other_conv
    })

    frappe.model.set_value(cdt, cdn, 'qty', row.ts_qty*conv1 + row.pieces*conv2)
    let rate=row.rate
    frappe.model.set_value(cdt, cdn, 'rate', 0)
    frappe.model.set_value(cdt, cdn, 'rate', rate)
}



frappe.ui.form.on('Sales Invoice', {
    onload:async function(frm){
        if(cur_frm.is_new() ){
            for(let ind=0;ind<cur_frm.doc.items.length;ind++){
                let cdt=cur_frm.doc.items[ind].doctype
                let cdn=cur_frm.doc.items[ind].name
                let row=locals[cdt][cdn]
                let uom=row.uom
                let conv1
                let conv2
                if(row.item_code)
                {
                await frappe.db.get_doc('Item', row.item_code).then((doc) => {
                    let bundle_conv=1
                    let other_conv=1;
                    let nos_conv=1
                    for(let doc_row=0; doc_row<doc.uoms.length; doc_row++){
                        if(doc.uoms[doc_row].uom==uom){
                            other_conv=doc.uoms[doc_row].conversion_factor
                        }
                        if(doc.uoms[doc_row].uom=='bundle'){
                            bundle_conv=doc.uoms[doc_row].conversion_factor
                        }
                        if(doc.uoms[doc_row].uom=='Nos'){
                            nos_conv=doc.uoms[doc_row].conversion_factor
                        }
                    }
                    conv1=bundle_conv/other_conv
                    conv2=nos_conv/other_conv
                })
            
                
                    let total_qty=row.qty
                    await frappe.model.set_value(cdt, cdn, 'ts_qty', parseInt(row.qty/conv1))
                    await frappe.model.set_value(cdt, cdn, 'pieces', 0)
                    let bundle_qty=row.qty
                    let pieces_qty=total_qty-bundle_qty
                    await frappe.model.set_value(cdt, cdn, 'pieces', pieces_qty/conv2)
                    let rate=row.rate
                    frappe.model.set_value(cdt, cdn, 'rate', 0)
                    frappe.model.set_value(cdt, cdn, 'rate', rate)
                }
            }
            let items = cur_frm.doc.items || [];
            let len = items.length;
            while (len--)
            {
                if(items[len].qty == 0)
                {
                    await cur_frm.get_field("items").grid.grid_rows[len].remove();
                }
            }
            cur_frm.refresh();
            
            
            }
            
        },
         // Thirvu_dual_Accounting
         company:function(frm){
            if(frm.doc.company){
    
            frappe.call({
                method:"ganapathy_pavers.custom.py.sales_order.branch_list",
                args:{
                    company:frm.doc.company
                },
                callback: function(r){
                   
                frm.set_query('branch',function(frm){
                    return{
                        filters:{
                            'name':['in',r.message]
                        }
                    }
                
                })
                }
            
            })}},
        site_work: function(frm, cdt, cdn){
            cur_frm.set_value('project', cur_frm.doc.site_work)
        }
})

function amount(frm,cdt,cdn){
    let row=locals[cdt][cdn];
    console.log(row.rate)
    if(row.qty>=0 && row.rate>=0){
        frappe.model.set_value(cdt,cdn,'amount',Math.round(row.qty*row.rate));
    }
 }
 frappe.ui.form.on('Sales Invoice Print Items', {
     qty:function(frm,cdt,cdn){
         amount(frm,cdt,cdn);
        },
     rate:function(frm,cdt,cdn){
         amount(frm,cdt,cdn);
        },
    })

frappe.ui.form.on('Sales Invoice',{
    refresh:function(frm){
        if(cur_frm.doc.docstatus==0){
            cur_frm.fields_dict.site_work.$input.on("click", function() {
                if(!cur_frm.doc.customer){
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
                }
            }
        })
    },
})
