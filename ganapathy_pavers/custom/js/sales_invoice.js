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
            if(doc.uoms[doc_row].uom=='Bdl'){
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

frappe.ui.form.on("Sales Invoice Item", {
    item_code: function(frm, cdt, cdn) {
        if(frm.doc.branch) {
            frappe.db.get_value("Branch", frm.doc.branch, "is_accounting").then( value => {
                if (!value.message.is_accounting) {
                    if(frm.doc.taxes_and_charges)
                        frm.set_value("taxes_and_charges", "")
                    if(frm.doc.tax_category)
                        frm.set_value("tax_category", "")
                    if(frm.doc.taxes)
                        frm.clear_table("taxes")
                    if(cur_frm.fields_dict["taxes"] && cur_frm.fields_dict["taxes"].refresh) {
                        cur_frm.fields_dict["taxes"].refresh()
                    }
                    (cur_frm.doc.items || []).forEach(row => {
                        frappe.model.set_value(row.doctype, row.name, 'unacc', 1);
                        frappe.model.set_value(row.doctype, row.name, 'item_tax_template', '');
                    })
                    refresh_field("items");
                } else {
                    (cur_frm.doc.items || []).forEach(row => {
                        frappe.model.set_value(row.doctype, row.name, 'unacc', 0);
                    })
                }
            })
        }
    }
})


frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        if (!cur_frm.doc.ewaybill && cur_frm.doc.einvoice_status == "Generated") {
            let bttn=cur_frm.add_custom_button("Get E-Way Bill No", async function() {
                await frappe.call({
                    method: "ganapathy_pavers.custom.py.sales_invoice.get_einvoice_no",
                    args: {
                        name: cur_frm.doc.name || "",
                        irn: cur_frm.doc.irn || "",
                    },
                    callback: function(r) {
                        if(!r.message) {
                            frappe.show_alert({message: "Couldn't get E-way Bill No", indicator: 'red'})
                        } else {
                            cur_frm.set_value("ewaybill", r.message)
                            cur_frm.save('Update')
                        }
                    }
                })
            });
            bttn.removeClass("btn-default")
            bttn.addClass("btn-success")
        }
    },
    onload_post_render: function(frm) {
        if(frm.is_new() && !frm.doc.customer) {
            frm.set_value("branch", "")
        }
    },
    taxes_and_charges: function(frm) {
        if(frm.doc.branch) {
            frappe.db.get_value("Branch", frm.doc.branch, "is_accounting").then( value => {
                if (!value.message.is_accounting) {
                    if(frm.doc.taxes_and_charges)
                        frm.set_value("taxes_and_charges", "")
                    if(frm.doc.tax_category)
                        frm.set_value("tax_category", "")
                    if(frm.doc.taxes)
                        frm.clear_table("taxes")
                    if(cur_frm.fields_dict["taxes"] && cur_frm.fields_dict["taxes"].refresh) {
                        cur_frm.fields_dict["taxes"].refresh()
                    }
                    (cur_frm.doc.items || []).forEach(row => {
                        frappe.model.set_value(row.doctype, row.name, 'unacc', 1);
                        frappe.model.set_value(row.doctype, row.name, 'item_tax_template', '');
                    })
                    refresh_field("items");
                } else {
                    (cur_frm.doc.items || []).forEach(row => {
                        frappe.model.set_value(row.doctype, row.name, 'unacc', 0);
                    })
                }
            })
        }
    },
    tax_category: function(frm) {
        frm.trigger("taxes_and_charges")
    },
    branch: function (frm) {
        frm.trigger("taxes_and_charges")
        frm.trigger("proforma_invoice")
    },
    validate: function(frm) {
        frm.trigger("taxes_and_charges")
    },
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
                        if(doc.uoms[doc_row].uom=='Bdl'){
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
            cur_frm.refresh_field("items");
            
            
            }
            
        },
        site_work: function(frm, cdt, cdn){
            cur_frm.set_value('project', cur_frm.doc.site_work)
        },
        proforma_invoice: async function(frm) {
            if (frm.doc.proforma_invoice && frm.doc.branch) {
                await frappe.db.get_value("Branch", frm.doc.branch, "proforma_abbr").then(res => {
                    if (res?.message?.proforma_abbr) {
                        frm.set_value("abbr_sales", res?.message?.proforma_abbr)
                    } else {
                        frappe.throw({message: `Please enter <b>Proforma Invoice</b> abbreviation in branch <b><a href="/app/branch/${frm.doc.branch}">${frm.doc.branch}</a></b>`})
                    }
                })
            } else {
                frm.set_value("abbr_sales", "")
            }
        },
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
});

frappe.ui.form.on("Sales Invoice Item", {
    item_code: function (frm, cdt, cdn) {
        (cur_frm.doc.items || []).forEach(row => {
            if (row.unacc && row.item_tax_template) {
                frappe.model.set_value(row.doctype, row.name, 'item_tax_template', '');
            }
        });
        refresh_field("items");
    }
});
