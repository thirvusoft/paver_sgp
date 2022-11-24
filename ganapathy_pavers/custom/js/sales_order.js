var prop_name;


frappe.ui.form.on('Sales Order', {
    onload: function (frm) {
        if (cur_frm.doc.docstatus == 1) {
            cur_frm.add_custom_button('Update Customer Details', function () {
                update_customer()
            })
        }
        frm.set_query('customer', 'customers_name', function () {
            return {
                filters: {
                    'customer_name': ['!=', 'MultiCustomer']
                }
            }
        })
        frm.set_query('customer', function () {
            return {
                filters: {
                    'customer_name': ['!=', 'MultiCustomer']
                }
            }
        })
        frappe.ui.form.ProjectQuickEntryForm = frappe.ui.form.QuickEntryForm.extend({
            render_dialog: async function () {
                this._super();
                if (this.dialog.fields.map(item => { return item.fieldname }).includes('naming_series')) {
                    this.dialog.set_df_property('naming_series', 'hidden', 1)
                }
                let calling_doc = frappe._from_link?.doc;
                this.doc.additional_cost = [{ 'description': 'Any Food Exp in Site' },
                { 'description': 'Other Labour Work' },
                { 'description': 'Site Advance' }]
                if (calling_doc.doctype == 'Sales Order') {
                    if (!calling_doc.is_multi_customer) {
                        this.dialog.get_field("customer").set_value(calling_doc.customer)
                    }
                    else {
                        this.dialog.get_field("is_multi_customer").set_value(1).then(() => {
                            this.dialog.refresh()
                        })
                        this.doc.customer_name = calling_doc.customers_name
                    }
                };
            }
        });
    },
    refresh: function (frm) {
        cur_frm.set_df_property("branch", "allow_on_submit", 0)
        if (cur_frm.doc.docstatus == 1 && !cur_frm.doc.branch) {
            cur_frm.add_custom_button("Update Branch", function () {
                let dialog = new frappe.ui.Dialog({
                    title: "Update Branch",
                    fields: [
                        {
                            fieldname: "branch",
                            label: "Branch",
                            fieldtype: "Link",
                            options: "Branch",
                            reqd: 1,
                        }
                    ],
                    primary_action: async function (data) {
                        if (cur_frm.is_dirty()) {
                            await cur_frm.save()
                        }
                        frappe.call({
                            method: "ganapathy_pavers.custom.py.sales_order.update_branch",
                            args: {
                                branch: data.branch,
                                name: cur_frm.doc.name,
                            },
                            callback: function (r) {
                                dialog.hide()
                                cur_frm.reload_doc()
                                frappe.show_alert({ message: "Branch updated successfully", indicator: 'green' })
                            }
                        })
                    }
                })
                dialog.show()
            }).addClass('btn ellipsis btn-primary').removeClass('btn-default')
        } else {
            cur_frm.remove_custom_button("Update Branch")
        }
        if (cur_frm.doc.is_multi_customer) {
            cur_frm.set_df_property('customer', 'reqd', 0);
        }
        else {
            cur_frm.set_df_property('customer', 'reqd', 1);
        }

        frm.set_query('supervisor', function (frm) {
            return {
                filters: {
                    'designation': 'Supervisor'
                }
            }
        });
        if (cur_frm.doc.docstatus == 0) {
            cur_frm.fields_dict.site_work.$input.on("click", async function () {
                await cur_frm.trigger('onload')

                if (!cur_frm.doc.customer && !cur_frm.doc.is_multi_customer) {
                    frappe.throw({ 'message': 'Please Select Customer' })
                }
            });
            cur_frm.fields_dict.customer.$input.on("click", async function () {
                await cur_frm.trigger('onload')
            })
        }

    },
    customer: function (frm) {
        if (cur_frm.doc.customer != 'MultiCustomer') {
            frm.set_query('site_work', function (frm) {
                return {
                    filters: {
                        'customer': cur_frm.doc.customer,
                        'status': 'Open',
                        'is_multi_customer': cur_frm.doc.is_multi_customer
                    }
                }
            })
        }
        else {
            frm.set_query('site_work', function (frm) {
                return {
                    filters: {
                        'status': 'Open',
                        'is_multi_customer': cur_frm.doc.is_multi_customer,
                        'customer': ''
                    }
                }
            })
        }
    },
    site_work: function (frm) {
        cur_frm.set_value('project', cur_frm.doc.site_work)
    },
    before_save: async function (frm) {
        if (cur_frm.doc.is_multi_customer) {
            frappe.db.exists('Customer', 'MultiCustomer').then((doc) => {
                if (doc == true) {
                    cur_frm.set_value('customer', 'MultiCustomer')
                }
                else {
                    frappe.throw({ 'message': "Can't find MultiCustomer" })
                }
            })
            cur_frm.set_df_property('customer', 'reqd', 0);
        }
        else {
            cur_frm.set_df_property('customer', 'reqd', 1);
        }
        if (cur_frm.doc.is_multi_customer) {
            await frappe.call({
                "method": "ganapathy_pavers.custom.py.sales_order.create_property",
                "callback": function (r) {
                    prop_name = r.message;
                }
            })
        }
        else {
            frm.clear_table("customers_name");
        }


        let tax = false;
        let taxes = cur_frm.doc.taxes ? cur_frm.doc.taxes : []
        for (let i = 0; i < taxes.length; i++) {
            if (!cur_frm.doc.taxes[i].tax_amount) {
                tax = true;
            }
        }

        if (taxes.length == 0) {
            tax = true;
        }

        if (tax) {
            let tax_category = frm.doc.tax_category
            await cur_frm.set_value('tax_category', '')
            await cur_frm.set_value('tax_category', tax_category)
        }


    },
    after_save: function (frm) {
        if (cur_frm.doc.is_multi_customer) {
            frappe.call({
                "method": "ganapathy_pavers.custom.py.sales_order.remove_property",
                "args": {
                    'prop_name': prop_name
                }
            })
        }
    },
    on_submit: function (frm) {
        if (cur_frm.doc.site_work) {
            frappe.call({
                method: "ganapathy_pavers.custom.py.sales_order.create_site",
                args: {
                    doc: cur_frm.doc
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.show_alert({ message: __("Site Work Updated Successfully"), indicator: 'green' });
                    }
                    else {
                        frappe.show_alert({ message: __("Couldn't Update Site Work"), indicator: 'red' });
                    }
                }
            })
        }
    },
    is_multi_customer: async function (frm) {
        cur_frm.set_value('site_work', '')

        if (cur_frm.doc.is_multi_customer) {
            frappe.db.exists('Customer', 'MultiCustomer').then((doc) => {
                if (doc == true) {
                    cur_frm.set_value('customer', 'MultiCustomer')
                }
                else {
                    frappe.throw({ 'message': "Can't find MultiCustomer" })
                }
            })
            frm.set_query('site_work', function (frm) {
                return {
                    filters: {
                        'status': 'Open',
                        'is_multi_customer': cur_frm.doc.is_multi_customer,
                        'customer': ''
                    }
                }
            })

        }
        else {
            frm.set_query('site_work', function (frm) {
                return {
                    filters: {
                        'customer': cur_frm.doc.customer,
                        'status': 'Open',
                        'is_multi_customer': cur_frm.doc.is_multi_customer
                    }
                }
            })
        }
    },

    length: function (frm) {
        cur_frm.set_value('post', Math.ceil(cur_frm.doc.length / 7))
        frm.trigger('height')
    },
    post: function (frm) {
        cur_frm.set_value('double_post', Math.ceil(cur_frm.doc.post / 15))
    },
    double_post: function (frm) {
        cur_frm.set_value('total_post', Math.ceil(cur_frm.doc.post + cur_frm.doc.double_post))
    },
    height: function (frm) {
        cur_frm.set_value('total_slab', Math.ceil(cur_frm.doc.post * (cur_frm.doc.height - 2)))
    },
    work: function (frm) {
        if (frm.doc.work == "Supply Only") {
            frm.set_value('site_work', '')
        }
        for (let row = 0; row < (frm.doc.items ? frm.doc.items.length : 0); row++) {
            frappe.model.set_value(frm.doc.items[row].doctype, frm.doc.items[row].name, 'work', frm.doc.work)
        }
    }
})

frappe.ui.form.on("Sales Order", {
    onload_post_render: function (frm) {
        if (frm.is_new()) {
            frm.set_value("branch", "")
        }
    },
    taxes_and_charges: function (frm) {
        if (frm.doc.branch) {
            frappe.db.get_value("Branch", frm.doc.branch, "is_accounting").then(value => {
                if (!value.message.is_accounting) {
                    if (frm.doc.taxes_and_charges)
                        frm.set_value("taxes_and_charges", "");
                    if (frm.doc.tax_category)
                        frm.set_value("tax_category", "");
                    if (frm.doc.taxes)
                        frm.clear_table("taxes");
                    refresh_field("taxes");
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
    tax_category: function (frm) {
        frm.trigger("taxes_and_charges")
    },
    branch: function (frm) {
        frm.trigger("taxes_and_charges")
    },
    validate: function (frm) {
        frm.trigger("taxes_and_charges")
    },
})

async function compoun_walls_calc(frm, cdt, cdtn) {
    let sales_uom, def_uom, ig, conv = 1, ts_uom;
    let row = locals[cdt][cdtn];
    if (row.item_code) {
        await frappe.db.get_doc('Item', row.item_code).then((doc) => {
            sales_uom = doc.sales_uom;
            def_uom = doc.stock_uom;
            ig = doc.item_group;
            ts_uom = (sales_uom ? sales_uom : def_uom);
            for (let i = 0; i < doc.uoms.length; i++) {
                if (doc.uoms[i].uom == ts_uom) {
                    conv = doc.uoms[i].conversion_factor
                }
            }
        })
        await frappe.model.set_value(cdt, cdtn, 'uom', ts_uom)
        if (conv) {
            await frappe.model.set_value(cdt, cdtn, 'conversion_factor', conv)
        }
        await frappe.model.set_value(cdt, cdtn, 'item_group', ig ? ig : '')
        if (ig != "Compound Walls") {
            return
        }
        let Post = 0, Slab = 0;
        for (let i = 0; i < frm.doc.items.length; i++) {
            if (cur_frm.doc.items[i].compound_wall_type == 'Slab' && cur_frm.doc.items[i].item_group == 'Compound Walls') {
                Slab += 1;
            }
            else if (cur_frm.doc.items[i].compound_wall_type == 'Post' && cur_frm.doc.items[i].item_group == 'Compound Walls') {
                Post += 1;
            }
        }
        if (row.compound_wall_type == 'Slab' && Slab == 1 && cur_frm.doc.total_slab) {
            frappe.model.set_value(cdt, cdtn, 'pieces', cur_frm.doc.total_slab);
        }
        else if (row.compound_wall_type == 'Post' && Post == 1 && cur_frm.doc.total_post) {
            frappe.model.set_value(cdt, cdtn, 'pieces', cur_frm.doc.total_post);
        }
        else {
            return
        }
        bundle_calc(frm, cdt, cdtn)
    }
}

frappe.ui.form.on('Sales Order Item', {
    item_code: function (frm, cdt, cdtn) {
        if (frm.doc.branch) {
            frappe.db.get_value("Branch", frm.doc.branch, "is_accounting").then(value => {
                if (!value.message.is_accounting) {
                    if (frm.doc.taxes_and_charges)
                        frm.set_value("taxes_and_charges", "");
                    if (frm.doc.tax_category)
                        frm.set_value("tax_category", "");
                    if (frm.doc.taxes)
                        frm.clear_table("taxes");
                    refresh_field("taxes");
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
        compoun_walls_calc(frm, cdt, cdtn)
    },
    ts_qty: function (frm, cdt, cdn) {
        bundle_calc(frm, cdt, cdn)
    },
    conversion_factor: function (frm, cdt, cdn) {
        bundle_calc(frm, cdt, cdn)
    },
    pieces: function (frm, cdt, cdn) {
        let data = locals[cdt][cdn]
        if (data.item_group == 'Raw Material') {
            frappe.model.set_value(cdt, cdn, 'qty', data.pieces)
        }
        bundle_calc(frm, cdt, cdn)
    },
    items_add: function (frm, cdt, cdn) {
        let data = locals[cdt][cdn]
        frappe.model.set_value(cdt, cdn, 'work', (data.idx > 1) ? cur_frm.doc.items[data.idx - 2].work : '')
    },
    ts_required_area_qty: async function (frm, cdt, cdn) {
        let row = locals[cdt][cdn]
        let conv1
        let conv2
        if (row.item_code && (row.item_group == 'Pavers' || row.item_group == 'Compound Walls')) {
            await frappe.db.get_doc('Item', row.item_code).then((doc) => {
                let bundle_conv = 1;
                let sqft_conv = 1;
                let nos_conv = 1;
                for (let doc_row = 0; doc_row < doc.uoms.length; doc_row++) {
                    if (doc.uoms[doc_row].uom == 'Bdl') {
                        bundle_conv = doc.uoms[doc_row].conversion_factor
                    }
                    if (doc.uoms[doc_row].uom == "SQF") {
                        sqft_conv = doc.uoms[doc_row].conversion_factor
                    }
                    if (doc.uoms[doc_row].uom == 'Nos') {
                        nos_conv = doc.uoms[doc_row].conversion_factor
                    }
                }
                conv1 = sqft_conv / bundle_conv
                conv2 = sqft_conv / nos_conv
            })

            await frappe.model.set_value(cdt, cdn, 'ts_qty', parseInt(row.ts_required_area_qty * conv1))
            let rem_ft = ((row.ts_required_area_qty * conv1) % 1) / conv1
            await frappe.model.set_value(cdt, cdn, 'pieces', Math.ceil(rem_ft * conv2))

        }
        else {
            await frappe.model.set_value(cdt, cdn, 'qty', row.ts_required_area_qty)
        }

    }

})


async function bundle_calc(frm, cdt, cdn) {
    let row = locals[cdt][cdn]
    let uom = row.uom
    let conv1
    let conv2
    if (row.item_code && (row.item_group == 'Pavers' || row.item_group == 'Compound Walls')) {
        await frappe.db.get_doc('Item', row.item_code).then((doc) => {
            let bundle_conv = 1
            let other_conv = 1;
            let nos_conv = 1
            for (let doc_row = 0; doc_row < doc.uoms.length; doc_row++) {
                if (doc.uoms[doc_row].uom == uom) {
                    other_conv = doc.uoms[doc_row].conversion_factor
                }
                if (doc.uoms[doc_row].uom == 'Bdl') {
                    bundle_conv = doc.uoms[doc_row].conversion_factor
                }
                if (doc.uoms[doc_row].uom == 'Nos') {
                    nos_conv = doc.uoms[doc_row].conversion_factor
                }
            }
            conv1 = bundle_conv / other_conv
            conv2 = nos_conv / other_conv
        })
        await frappe.model.set_value(cdt, cdn, 'qty', row.ts_qty * conv1 + row.pieces * conv2)
        let rate = row.rate
        frappe.model.set_value(cdt, cdn, 'rate', 0)
        frappe.model.set_value(cdt, cdn, 'rate', rate)
    }
}

function update_customer() {
    let dialog = new frappe.ui.Dialog({
        title: "Update MultiCustomer Details",
        fields: [
            {
                fieldname: 'customers_name',
                fieldtype: 'Table',
                label: 'Customers Name',
                data: cur_frm.doc.customers_name,
                reqd: 1,
                fields: [
                    {
                        fieldname: 'customer',
                        fieldtype: 'Link',
                        label: 'Customer',
                        options: 'Customer',
                        in_list_view: 1
                    }
                ]
            }
        ],
        primary_action: async function (data) {
            await frappe.call({
                method: "ganapathy_pavers.custom.py.sales_order.update_multicustomer",
                args: {
                    customers_name: data.customers_name,
                    sales_order: cur_frm.doc.name
                },
                freeze: true,
                freeze_message: "Updating",
                callback(r) {
                    cur_frm.reload_doc()
                    dialog.hide()
                }
            })
        }
    })
    dialog.show()
}