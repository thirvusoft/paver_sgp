var month, paver, cw, lego, fp;

frappe.ui.form.on("Journal Entry", {
    refresh: async function (frm) {
        await frappe.model.with_doctype("TS Workstation")
        if (!frm.doc.docstatus) {
            frm.add_custom_button('Get Monthly Costing', async function () {
                if (frm.doc.machine_3 || frm.doc.machine_12) {

                    if (frm.doc.common_expenses?.length > 0) {
                        frm.scroll_to_field("common_expenses");
                        await frappe.confirm(
                            `Do you want to erase the existing data in <b>Common Expenses</b> table`,
                            async () => {
                                await frm.clear_table("common_expenses");
                                await frm.fields_dict.common_expenses?.refresh();
                                await get_common_expenses(frm);
                            },
                            () => { }
                        );
                    } else {
                        await get_common_expenses(frm);
                    }
                }
                else {
                    frappe.show_alert({ message: __('Please Select Machine'), indicator: 'red' });
                }
            });
            frm.add_custom_button('Get Vehicle Costing', async function () {
                let vehicle_acc_length = 0;
                (frm.doc.accounts || []).forEach(row => {
                    if (row.vehicle) {
                        vehicle_acc_length++;
                    }
                });
                if (vehicle_acc_length > 0) {
                    frm.scroll_to_field("accounts");
                    await frappe.confirm(
                        `Do you want to erase the existing data in <b>Accounting Entries</b> table`,
                        async () => {
                            frm.fields_dict.accounts.grid.grid_pagination.go_to_page(1);
                            for (let i = 0; i < cur_frm.fields_dict.accounts.grid.grid_rows.length; i++) {
                                frm.fields_dict.accounts.grid.grid_rows[0]?.remove();
                            }
                            await frm.fields_dict.accounts.refresh();
                            await get_vehicle_expenses(frm);
                        },
                        () => { }
                    );
                } else {
                    await get_vehicle_expenses(frm)
                }
            });
        }

        set_css();
        frm.set_query("account", "common_expenses", function () {
            return erpnext.journal_entry.account_query(cur_frm);
        });
        dashboard_data(cur_frm.doc.posting_date, cur_frm)
    },
    posting_date: function (frm) {
        dashboard_data(cur_frm.doc.posting_date, cur_frm)
    },
    onload_post_render: function (frm) {
        if (frm.is_new()) {
            frm.set_value("branch", "");
        }
    },
    split_expense: async function (frm) {
        if (cur_frm.doc.docstatus != 0 || (!frm.doc.machine_12 && !frm.doc.machine_3)) {
            return;
        }
        validate_common_accounts()
        frappe.dom.freeze(frappe.render_template("je_loading"));
        frm.fields_dict.accounts.grid.grid_pagination.go_to_page(1);
        for (let i = 0; i < cur_frm.fields_dict.accounts.grid.grid_rows.length; i++) {
            frm.fields_dict.accounts.grid.grid_rows[0]?.remove();
        }
        await frm.fields_dict.accounts.refresh();
        await frappe.call({
            method: "ganapathy_pavers.custom.py.journal_entry.split_expenses",
            args: {
                common_exp: cur_frm.doc.common_expenses || [],
            },
            freeze: true,
            freeze_message: "Splitting Expenses",
            async callback(r) {
                let res = r.message || []
                res.forEach(async row => {
                    let child = cur_frm.add_child("accounts");
                    child.account = row.account;
                    child.vehicle = row.vehicle;
                    child.debit_in_account_currency = row.debit;
                    child.debit = row.debit;
                    child.from_common_entry = 1;
                    await frm.fields_dict.accounts.refresh();
                });
                await calculate_debit(frm)
            }
        });
        frappe.dom.unfreeze();
    },
    machine_12: async function (frm) {
        await dashboard_data(cur_frm.doc.posting_date, cur_frm)
        if (frm.doc.machine_12 == 1) {
            await frm.set_value("machine_3", 0);
            await trigger_allocate_amount(frm)
        }

    },
    machine_3: async function (frm) {
        await dashboard_data(cur_frm.doc.posting_date, cur_frm)
        if (frm.doc.machine_3 == 1) {
            await frm.set_value("machine_12", 0);
            await trigger_allocate_amount(frm)
        }
    }
});

async function calculate_debit(frm) {
    let total_debit = 0, credit_acc_count = 0;
    (frm.doc.accounts || []).forEach(row => {
        total_debit += (row.debit_in_account_currency || 0);
        if (!row.debit_in_account_currency) {
            credit_acc_count += 1;
        }
    });
    if (credit_acc_count === 1) {
        (frm.doc.accounts || []).forEach(async row => {
            if (!row.debit_in_account_currency) {
                await frappe.model.set_value(row.doctype, row.name, "credit", total_debit);
                await frappe.model.set_value(row.doctype, row.name, "credit_in_account_currency", total_debit);
                return
            }
        });
    }
    frm.cscript.update_totals(frm.doc)
}

async function trigger_allocate_amount(frm) {
    (frm.doc.common_expenses || []).forEach(async row => {
        await allocate_amount(frm, row.doctype, row.name);
    });
    frm.trigger("split_expense");
}

frappe.ui.form.on("Common Expense JE", {
    paver: function (frm, cdt, cdn) {
        get_accounts(frm, cdt, cdn);
        allocate_amount(frm, cdt, cdn);
    },
    compound_wall: function (frm, cdt, cdn) {
        get_accounts(frm, cdt, cdn);
        allocate_amount(frm, cdt, cdn);
    },
    lego_block: function (frm, cdt, cdn) {
        get_accounts(frm, cdt, cdn);
        allocate_amount(frm, cdt, cdn);
    },
    fencing_post: function (frm, cdt, cdn) {
        get_accounts(frm, cdt, cdn);
        allocate_amount(frm, cdt, cdn);
    },
    account: function (frm, cdt, cdn) {
        get_accounts(frm, cdt, cdn);
        allocate_amount(frm, cdt, cdn);
    },
    vehicle: function (frm, cdt, cdn) {
        get_accounts(frm, cdt, cdn);
        allocate_amount(frm, cdt, cdn);
    },
    debit: function (frm, cdt, cdn) {
        allocate_amount(frm, cdt, cdn);
    },
});

function validate_common_accounts() {
    (cur_frm.doc.common_expenses || []).forEach(row => {
        if (row.paver && !row.paver_account) {
            frappe.throw({ message: `<b>Paver Account</b> is mandatory at <b>Common Expenses</b> #row ${row.idx}`, title: "Missing Fields", indicator: "red" });
        }
        if (row.compound_wall && !row.cw_account) {
            frappe.throw({ message: `<b>Compound Wall Account</b> is mandatory at <b>Common Expenses</b> #row ${row.idx}`, title: "Missing Fields", indicator: "red" });
        }
        if (row.lego_block && !row.lg_account) {
            frappe.throw({ message: `<b>Lego Block Account</b> is mandatory at <b>Common Expenses</b> #row ${row.idx}`, title: "Missing Fields", indicator: "red" });
        }
        if (row.fencing_post && !row.fp_account) {
            frappe.throw({ message: `<b>Fencing Post Account</b> is mandatory at <b>Common Expenses</b> #row ${row.idx}`, title: "Missing Fields", indicator: "red" });
        }
    });
}

async function get_common_expenses(frm) {
    await frappe.call({
        method: "ganapathy_pavers.ganapathy_pavers.doctype.expense_accounts.expense_accounts.monthly_cost",
        freeze: true,
        freeze_message: "Fetching Data...",
        callback: async function (r) {
            var a = r.message
            for (var idx = 0; idx < (r.message).length; idx++) {
                if (a[idx]["monthly_cost"]) {
                    var row = frm.add_child("common_expenses"); await cur_frm.fields_dict.common_expenses.refresh()
                    frappe.model.set_value(row.doctype, row.name, "account", a[idx]["account"] || a[idx]["paver"] || "");
                    frappe.model.set_value(row.doctype, row.name, "vehicle", a[idx]["vehicle"] || "");
                    frappe.model.set_value(row.doctype, row.name, "debit", a[idx]["monthly_cost"] || "");
                    if (a[idx]["paver"]) {
                        frappe.model.set_value(row.doctype, row.name, "paver_account", a[idx]["paver"] || "");
                        frappe.model.set_value(row.doctype, row.name, "paver", 1);
                    }
                    if (a[idx]["cw"]) {
                        frappe.model.set_value(row.doctype, row.name, "cw_account", a[idx]["cw"] || "");
                        frappe.model.set_value(row.doctype, row.name, "compound_wall", 1);
                    }
                    if (a[idx]["lg"]) {
                        frappe.model.set_value(row.doctype, row.name, "lg_account", a[idx]["lg"] || "");
                        frappe.model.set_value(row.doctype, row.name, "lego_block", 1);
                    }
                    if (a[idx]["fp"]) {
                        frappe.model.set_value(row.doctype, row.name, "fp_account", a[idx]["fp"] || "");
                        frappe.model.set_value(row.doctype, row.name, "fencing_post", 1);
                    }
                }
            }
            await cur_frm.fields_dict.common_expenses.refresh();
        }
    });
}

async function get_vehicle_expenses(frm) {
    await frappe.call({
        method: "ganapathy_pavers.custom.py.vehicle.get_vehicle_expenses",
        args: {
            date: frm.doc.posting_date
        },
        freeze: true,
        freeze_message: "Fetching Data...",
        callback: async function (r) {
            var a = r.message || []
            for (var idx = 0; idx < a.length; idx++) {
                if (a[idx]) {
                    if (a[idx]["amount"] && a[idx]["account"]) {
                        var row = frm.add_child("accounts");
                        await cur_frm.fields_dict.accounts.refresh();
                        frappe.model.set_value(row.doctype, row.name, "account", a[idx]["account"] || "");
                        frappe.model.set_value(row.doctype, row.name, "debit_in_account_currency", a[idx]["amount"] || "");
                        frappe.model.set_value(row.doctype, row.name, "debit", a[idx]["amount"] || "");
                        frappe.model.set_value(row.doctype, row.name, "vehicle", a[idx]["vehicle"] || "");
                    }
                }
            }
            await cur_frm.fields_dict.accounts.refresh();
        }
    });
}

async function allocate_amount(frm, cdt, cdn) {
    let data = locals[cdt][cdn];
    if (data.vehicle) {
        ['paver_amount', 'cw_amount', 'lg_amount', 'fp_amount',
            'paver', 'compound_wall', 'fencing_post', 'lego_block'].forEach(async field => {
                await frappe.model.set_value(cdt, cdn, field, 0);
            });
        return;
    }
    let total_production = 0;
    if (data.paver) {
        total_production += (paver || 0);
    }
    if (data.compound_wall) {
        total_production += (cw || 0);
    }
    if (data.lego_block) {
        total_production += (lego || 0);
    }
    if (data.fencing_post) {
        total_production += (fp || 0);
    }

    if (data.paver) {
        await frappe.model.set_value(cdt, cdn, 'paver_amount', data.debit * (paver / total_production));
    } else {
        await frappe.model.set_value(cdt, cdn, 'paver_amount', 0);
    }

    if (data.compound_wall) {
        await frappe.model.set_value(cdt, cdn, 'cw_amount', data.debit * (cw / total_production));
    } else {
        await frappe.model.set_value(cdt, cdn, 'cw_amount', 0);
    }

    if (data.fencing_post) {
        await frappe.model.set_value(cdt, cdn, 'fp_amount', data.debit * (fp / total_production));
    } else {
        await frappe.model.set_value(cdt, cdn, 'fp_amount', 0);
    }

    if (data.lego_block) {
        await frappe.model.set_value(cdt, cdn, 'lg_amount', data.debit * (lego / total_production));
    } else {
        await frappe.model.set_value(cdt, cdn, 'lg_amount', 0);
    }
}

function get_accounts(frm, cdt, cdn) {
    let data = locals[cdt][cdn];
    if (!data.account || data.vehicle) {
        frappe.model.set_value(cdt, cdn, "paver_account", "");
        frappe.model.set_value(cdt, cdn, "cw_account", "");
        frappe.model.set_value(cdt, cdn, "fp_account", "");
        frappe.model.set_value(cdt, cdn, "lg_account", "");
        return
    }
    frappe.call({
        method: "ganapathy_pavers.ganapathy_pavers.doctype.expense_accounts.expense_accounts.get_common_account",
        args: {
            account: data.account
        },
        callback(r) {
            let res = r.message;
            frappe.model.set_value(cdt, cdn, "paver_account", res["paver"] || "");
            frappe.model.set_value(cdt, cdn, "cw_account", res["cw"] || "");
            frappe.model.set_value(cdt, cdn, "fp_account", res["fp"] || "");
            frappe.model.set_value(cdt, cdn, "lg_account", res["lg"] || "");
        }
    });
}

function set_css(frm) {
    document.querySelectorAll("[data-fieldname='split_expense']")[1].style.paddingRight = "12px";
    document.querySelectorAll("[data-fieldname='split_expense']")[1].style.paddingLeft = "12px";
    document.querySelectorAll("[data-fieldname='split_expense']")[1].style.color = "white";
    document.querySelectorAll("[data-fieldname='split_expense']")[1].style.fontWeight = "bold";
    document.querySelectorAll("[data-fieldname='split_expense']")[1].style.backgroundColor = "#3399ff";
}

async function dashboard_data(date, frm) {
    if (!date || (!frm.doc.machine_12 && !frm.doc.machine_3)) {
        frm.dashboard.clear_comment();
        return;
    }
    let machines = [];
    if (frm.doc.machine_12) {
        machines = ["Machine1", "Machine2"]
    }
    if (frm.doc.machine_3) {
        machines = ["Machine3"]
    }
    await frappe.call({
        method: "ganapathy_pavers.custom.py.journal_entry.get_production_details",
        args: {
            date: date,
            machines: machines
        },
        callback(r) {
            let res = r.message;
            month = res.month || "";
            paver = res.paver || 0;
            cw = res.cw || 0;
            lego = res.lego || 0;
            fp = res.fp || 0;

            frm.dashboard.clear_comment();
            frm.dashboard.add_comment(frappe.render_template("je_production_dashboard", {
                month: month.toUpperCase(),
                paver: roundNumber(paver),
                cw: roundNumber(cw),
                lego: roundNumber(lego),
                fp: roundNumber(fp)
            }), 'yellow', 1);
        }
    });
}
