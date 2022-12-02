var month, paver, cw, lego, fp;

frappe.ui.form.on("Journal Entry", {
    refresh: function (frm) {
        set_css();
        frm.set_query("account", "common_expenses", function () {
            return erpnext.journal_entry.account_query(cur_frm);
        });
        dashboard_data(cur_frm.doc.posting_date)
    },
    posting_date: function (frm) {
        dashboard_data(cur_frm.doc.posting_date)
    },
    onload_post_render: function (frm) {
        if (frm.is_new()) {
            frm.set_value("branch", "");
        }
    },
    split_expense: async function (frm) {
        if(cur_frm.doc.docstatus!=0) {
            return;
        }
        validate_common_accounts()
        frappe.dom.freeze('.......');
        cur_frm.fields_dict.accounts.grid.grid_rows.forEach(async row => {
            if(row.doc.from_common_entry) {
                row.doc.__checked=1;
            }
        });
        cur_frm.fields_dict.accounts.grid.delete_rows();
        refresh_field("accounts");

        await frappe.call({
            method: "ganapathy_pavers.custom.py.journal_entry.split_expenses",
            args: {
                common_exp: cur_frm.doc.common_expenses || [],
            },
            freeze: true,
            freeze_message: "Splitting Expenses",
            callback(r) {
                let res=r.message
                res.forEach(row => {
                    let child = cur_frm.add_child("accounts");
                    child.account = row.account;
                    child.debit_in_account_currency = row.debit;
                    child.from_common_entry = 1;
                    refresh_field("accounts");
                });
                
            }
        });
        frappe.dom.unfreeze();
    },
});

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
    debit: function (frm, cdt, cdn) {
        allocate_amount(frm, cdt, cdn);
    },
});

function validate_common_accounts() {
    cur_frm.doc.common_expenses.forEach(row => {
        if (row.paver && !row.paver_account) {
            frappe.throw({message: `<b>Paver Account</b> is mandatory at <b>Common Expenses</b> #row${row.idx}`, title: "Missing Fields", indicator: "res"});
        }
        if (row.compound_wall && !row.cw_account) {
            frappe.throw({message: `<b>Compound Wall Account</b> is mandatory at <b>Common Expenses</b> #row${row.idx}`, title: "Missing Fields", indicator: "res"});
        }
        if (row.lego_block && !row.lg_account) {
            frappe.throw({message: `<b>Lego Block Account</b> is mandatory at <b>Common Expenses</b> #row${row.idx}`, title: "Missing Fields", indicator: "res"});
        }
        if (row.fencing_post && !row.fp_account) {
            frappe.throw({message: `<b>Fencing Post Account</b> is mandatory at <b>Common Expenses</b> #row${row.idx}`, title: "Missing Fields", indicator: "res"});
        }
    });
}

function allocate_amount(frm, cdt, cdn) {
    let data = locals[cdt][cdn];
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
        frappe.model.set_value(cdt, cdn, 'paver_amount', data.debit * (paver/total_production));
    } else {
        frappe.model.set_value(cdt, cdn, 'paver_amount', 0);
    }

    if (data.compound_wall) {
        frappe.model.set_value(cdt, cdn, 'cw_amount', data.debit * (cw/total_production));
    } else {
        frappe.model.set_value(cdt, cdn, 'cw_amount', 0);
    }

    if (data.fencing_post) {
        frappe.model.set_value(cdt, cdn, 'fp_amount', data.debit * (fp/total_production));
    } else {
        frappe.model.set_value(cdt, cdn, 'fp_amount', 0);
    }

    if (data.lego_block) {
        frappe.model.set_value(cdt, cdn, 'lg_amount', data.debit * (lego/total_production));
    } else {
        frappe.model.set_value(cdt, cdn, 'lg_amount', 0);
    }
}

function get_accounts(frm, cdt, cdn) {
    let data = locals[cdt][cdn];
    if (!data.account) {
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

function dashboard_data(date) {
    if (!date) {
        cur_frm.dashboard.clear_comment();
        return;
    }
    frappe.call({
        method: "ganapathy_pavers.custom.py.journal_entry.get_production_details",
        args: {
            date: date
        },
        callback(r) {
            let res = r.message;
            month = res.month || "";
            paver = res.paver || 0;
            cw = res.cw || 0;
            lego = res.lego || 0;
            fp = res.fp || 0;
            let msg = `
                <div class="close-dialog">
                    <span></span>
                    <div class="production-heading">
                    PRODUCTION DETAILS OF ${month.toUpperCase()} MONTH
                </div>
                    <span class="close-x" onclick="cur_frm.dashboard.clear_comment(); return false;">x</span>
                </div>
                <div class="production-info">
                    <div class="production-info-data">
                        <div class="production-info-data-div">
                            Paver: ${parseInt(paver)}
                        </div>
                    </div>
                    <div class="production-info-data">
                        <div class="production-info-data-div">
                            Compound Wall: ${parseInt(cw)}
                        </div>
                    </div>
                    <div class="production-info-data">
                        <div class="production-info-data-div">
                            Lego Block: ${parseInt(lego)}
                        </div>
                    </div>
                    <div class="production-info-data">
                        <div class="production-info-data-div">
                            Fencing Post: ${parseInt(fp)}
                        </div>
                    </div>
                </div>
                <style>
                    .production-heading {
                        width: 100%;
                        font-size: 130%;
                        text-align: center;
                        font-weight: bold;
                        margin-bottom: 3mm;
                    }
                    .production-info {
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        width: 100%;
                        gap: 20px;
                        flex-wrap: nowrap;
                    }
                    .production-info div {
                        font-size: 110%;
                        padding: 10px;
                        display: flex;
                        flex-wrap: nowrap;
                        width: 25%;
                        background: rgb(91 86 86 / 50%);
                        border-radius: 10px;
                        color: rgb(0 0 0);
                    }
                    .production-info-data-div {
                        width: 100% !important;
                        align-items: center;
                        border-radius: 50px !important;
                        background: rgb(255 251 251 / 40%) !important;
                        font-weight: 700;
                        justify-content: center;
                        pointer-events: auto;
                    }
                    .production-info-data {
                        pointer-events: none;
                        transition: transform .2s;
                    }
                    .production-info-data:hover {
                        -webkit-transform: scale(1.5);
                        transform: scale(1.1);
                        cursor: pointer;
                    }
                    .close-dialog {
                        display: flex;
                        width: 100%;
                        align-items: right;
                        justify-content: space-between;
                        font-size: 125%;
                    }
                    .close-dialog :hover {
                        cursor: pointer;
                    }
                    .close-x {
                        background: rgb(0 0 0 / 29%) !important;
                        height: 25px;
                        width: 25px;
                        text-align: center !important;
                        border-radius: 50%;
                        display: inline-block;
                        color: black;
                        transition: transform .2s;
                    }
                    .close-x:hover {
                        -webkit-transform: scale(1.5);
                        transform: scale(1.2);
                        border-radius: 30%;
                        background: rgb(0 0 0 / 47%) !important;
                    }
                </style>
            `
            cur_frm.dashboard.clear_comment();
            cur_frm.dashboard.add_comment(msg, 'yellow', 1);
        }
    });
}