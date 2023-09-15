// apps/frappe/frappe/public/js/frappe/views/reports/query_report.js

get_filters_html_for_print() {
    const applied_filters = this.get_filter_values();
    return "<div style='display: flex; justify-content: space-between; flex-wrap: wrap;'>"+Object.keys(applied_filters)
        .map(fieldname => {
            if (frappe.query_report.get_filter(fieldname).df.print_hide) {
                return '';
            }
            const label = frappe.query_report.get_filter(fieldname).df.label;
            const value = applied_filters[fieldname];
            return `<h6><i>${__(label)}</i>: <b>${value}</b></h6>`;
        })
        .join('')+"</div>";
}