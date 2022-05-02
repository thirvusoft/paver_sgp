make_delivery_note(delivery_dates) {
    var me = this
    if(this.frm.doc.is_multi_customer){
    this.frm.call({
        method:"ganapathy_pavers.custom.py.sales_order.get_customer_list",
        args:{
            'sales_order':me.frm.doc.name
        },
        callback: function(r){
            var dialog = new frappe.ui.Dialog({
                title: __('Select a Customer for Delivery Note'),
                fields: [{
                    fieldtype: 'Select',
                    fieldname: 'customer',
                    label: __('Customer'),
                    options: r.message,
                    reqd:1
                }],
                primary_action: function() {
                    me.frm.call({
                        method: 'ganapathy_pavers.custom.py.sales_order.update_temporary_customer',
                        args: {
                            customer: dialog.fields_dict.customer.value,
                            sales_order: me.frm.doc.name
                        },
                        freeze: true,
                        callback: function(r) {
                            dialog.hide();
                            frappe.model.open_mapped_doc({
                                method: "erpnext.selling.doctype.sales_order.sales_order.make_delivery_note",
                                frm: me.frm,
                                args: {
                                    delivery_dates
                                }
                            })
                        }
                    });
                },
                primary_action_label: __('Create')
            });
            dialog.show();
        }
    })
}
else{
    frappe.model.open_mapped_doc({
        method: "erpnext.selling.doctype.sales_order.sales_order.make_delivery_note",
        frm: this.frm,
        args: {
            delivery_dates
        }
    })
}
},

 make_sales_invoice() {
    var me = this
    if(this.frm.doc.is_multi_customer){
    this.frm.call({
        method:"ganapathy_pavers.custom.py.sales_order.get_customer_list",
        args:{
            'sales_order':me.frm.doc.name
        },
        callback: function(r){
            var dialog = new frappe.ui.Dialog({
                title: __('Select a Customer for Sales Invoice'),
                fields: [{
                    fieldtype: 'Select',
                    fieldname: 'customer',
                    label: __('Customer'),
                    options: r.message,
                    reqd:1
                }],
                primary_action: function() {
                    me.frm.call({
                        method: 'ganapathy_pavers.custom.py.sales_order.update_temporary_customer',
                        args: {
                            customer: dialog.fields_dict.customer.value,
                            sales_order: me.frm.doc.name
                        },
                        freeze: true,
                        callback: function(r) {
                            dialog.hide();
                            frappe.model.open_mapped_doc({
                                method: "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice",
                                frm: me.frm
                            })
                        }
                    });
                },
                primary_action_label: __('Create')
            });
            dialog.show();
        }
    })
}
else{
    frappe.model.open_mapped_doc({
        method: "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice",
        frm: this.frm
    })
}
},