var month, paver, cw, lego, fp;

frappe.ui.form.on("Journal Entry", {
    refresh: function (frm) {
         
        frm.add_custom_button('Monthly Cost', async function() {
           
            if (frm.doc.machine_3 || frm.doc.machine_12){
            await frappe.call({
                method:"ganapathy_pavers.ganapathy_pavers.doctype.expense_accounts.expense_accounts.monthly_cost",
   
                callback: async function(r){
                    console.log(r.message)
                   var  a=r.message
                    for(var i=0;i<(r.message).length;i++){
                        if(a[i]["monthly_cost"])
                     {

                        var row = frm.add_child("common_expenses");await cur_frm.fields_dict.common_expenses.refresh()
                        frappe.model.set_value(row.doctype, row.name, "account", a[i]["paver"][0] || "");
                        frappe.model.set_value(row.doctype, row.name, "debit", a[i]["monthly_cost"] || "");
                      if( a[i]["paver"][0])
                      {
                        frappe.model.set_value(row.doctype, row.name, "paver_account", a[i]["paver"][0] || "");
                        frappe.model.set_value(row.doctype, row.name, "paver", 1);
                      }
                      if( a[i]["cw"][0]){
                        frappe.model.set_value(row.doctype, row.name, "cw_account", a[i]["cw"][0] || "");
                        frappe.model.set_value(row.doctype, row.name, "compound_wall", 1);

                      }
                      if( a[i]["lg"][0])
                      {
                        frappe.model.set_value(row.doctype, row.name, "lg_account", a[i]["lg"][0] || "");
                        frappe.model.set_value(row.doctype, row.name, "lego_block", 1);
                      }
                      if( a[i]["fp"][0]){
                        frappe.model.set_value(row.doctype, row.name, "fp_account", a[i]["fp"][0] || "");
                        frappe.model.set_value(row.doctype, row.name, "fencing_post", 1);

                     }

                    }}

                    await cur_frm.fields_dict.common_expenses.refresh()
                }
            })}
            else{
                frappe.show_alert({ message: __('Please Select Machine'), indicator: 'red' });
            }

        })
   
  

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
        frappe.dom.freeze('.......');
        (cur_frm.fields_dict.accounts.grid.grid_rows || []).forEach(async row => {
            if (row.doc.from_common_entry) {
                row.doc.__checked = 1;
            }
        });
        await cur_frm.fields_dict.accounts.grid.delete_rows();
        await frm.fields_dict.accounts.refresh();
        await new Promise(r => setTimeout(r, 1000));
        await frappe.call({
            method: "ganapathy_pavers.custom.py.journal_entry.split_expenses",
            args: {
                common_exp: cur_frm.doc.common_expenses || [],
            },
            freeze: true,
            freeze_message: "Splitting Expenses",
            async callback (r) {
                let res = r.message || []
                res.forEach(async row => {
                    let child = cur_frm.add_child("accounts");
                    child.account = row.account;
                    child.debit_in_account_currency = row.debit;
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
            frm.set_value("machine_3", 0);
            trigger_allocate_amount(frm)
        }
        
    },
    machine_3: async function (frm) {
        await  dashboard_data(cur_frm.doc.posting_date, cur_frm)
        if (frm.doc.machine_3 == 1) {
            frm.set_value("machine_12", 0);
            trigger_allocate_amount(frm)
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
    frm.set_value("total_debit", total_debit)
    if (credit_acc_count === 1) {
        (frm.doc.accounts || []).forEach(async row => {
            if (!row.debit_in_account_currency) {
                await frappe.model.set_value(row.doctype, row.name, "credit_in_account_currency", total_debit);
                return
            }
        });
    } else {

    }

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
    debit: function (frm, cdt, cdn) {
        allocate_amount(frm, cdt, cdn);
    },
});

function validate_common_accounts() {
    (cur_frm.doc.common_expenses || []).forEach(row => {
        if (row.paver && !row.paver_account) {
            frappe.throw({ message: `<b>Paver Account</b> is mandatory at <b>Common Expenses</b> #row${row.idx}`, title: "Missing Fields", indicator: "res" });
        }
        if (row.compound_wall && !row.cw_account) {
            frappe.throw({ message: `<b>Compound Wall Account</b> is mandatory at <b>Common Expenses</b> #row${row.idx}`, title: "Missing Fields", indicator: "res" });
        }
        if (row.lego_block && !row.lg_account) {
            frappe.throw({ message: `<b>Lego Block Account</b> is mandatory at <b>Common Expenses</b> #row${row.idx}`, title: "Missing Fields", indicator: "res" });
        }
        if (row.fencing_post && !row.fp_account) {
            frappe.throw({ message: `<b>Fencing Post Account</b> is mandatory at <b>Common Expenses</b> #row${row.idx}`, title: "Missing Fields", indicator: "res" });
        }
    });
}

async function allocate_amount(frm, cdt, cdn) {
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

async function dashboard_data(date, frm) {
    if (!date || (!frm.doc.machine_12 && !frm.doc.machine_3)) {
        cur_frm.dashboard.clear_comment();
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
                            Paver: ${roundNumber(paver)}
                        </div>
                    </div>
                    <div class="production-info-data">
                        <div class="production-info-data-div">
                            Compound Wall: ${roundNumber(cw)}
                        </div>
                    </div>
                    <div class="production-info-data">
                        <div class="production-info-data-div">
                            Lego Block: ${roundNumber(lego)}
                        </div>
                    </div>
                    <div class="production-info-data">
                        <div class="production-info-data-div">
                            Fencing Post: ${roundNumber(fp)}
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