// Cutomization code   apps/frappe/frappe/public/js/frappe/views/reports/report_view.js

async prepare_data(r) {
    let data = r.message || {};
    
    data = frappe.utils.dict(data.keys, data.values);
    if(data && typeof(data) == 'object'){
        await frappe.call({
            method: "ganapathy_pavers.custom.py.reportview.reportview",
            args: { data: data},
            callback: function(r){
                if(r.message){
                    data = r.message
                }
            }
        })
    }

    if (this.start === 0) {
        this.data = data;
    } else {
        this.data = this.data.concat(data);
    }
}

// Cutomization code


// Original code

prepare_data(r) {
    let data = r.message || {};
    data = frappe.utils.dict(data.keys, data.values);
    if (this.start === 0) {
        this.data = data;
    } else {
        this.data = this.data.concat(data);
    }
}

// Original code