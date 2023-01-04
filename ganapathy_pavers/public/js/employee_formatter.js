frappe.form.link_formatters['Employee'] = function(value, doc) {
    if(doc.employee_name && doc.employee_name !== value) {
        return value + ': ' + doc.employee_name;
    } else {
        return value;
    }
}