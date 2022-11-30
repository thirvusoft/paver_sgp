frappe.ui.form.on("Journal Entry", {
    refresh: function (frm) {
        dashboard_data(cur_frm.doc.posting_date)
    },
    posting_date: function (frm) {
        dashboard_data(cur_frm.doc.posting_date)
    },
    onload_post_render: function (frm) {
        if (frm.is_new()) {
            frm.set_value("branch", "");
        }
    }
});

function dashboard_data(date) {
    if(!date) {
        cur_frm.dashboard.clear_comment()
        return
    }
    var month, paver, cw, lego, fp;
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
                <div class="production-heading">
                    PRODUCTION DETAILS OF ${month.toUpperCase()} MONTH
                </div>
                <div class="production-info">
                    <div><li>Paver: ${parseInt(paver)}</li></div>
                    <div><li>Compound Wall: ${parseInt(cw)}</li></div>
                    <div><li>Lego Block: ${parseInt(lego)}</li></div>
                    <div><li>Fencing Post: ${parseInt(fp)}</li></div>
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
                        width: 25%;
                        background: rgb(91 86 86 / 50%);
                        border-radius: 10px;
                        color: rgb(0 0 0);
                    }
                </style>
            `
            cur_frm.dashboard.clear_comment()
            cur_frm.dashboard.add_comment(msg, 'yellow', 1)
        }
    });
}