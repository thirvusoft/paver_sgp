frappe.listview_settings['TS Employee Attendance Tool'] = {
    onload: function (list_view) {
        list_view.page.add_actions_menu_item(__("Mark Attendance"), async function () {
            await frappe.call({
                method: "ganapathy_pavers.custom.py.employee_atten_tool.create_attendance",
                async: true,
                args: {
                    docnames: list_view.get_checked_items(true)
                }, callback(r) { 
                    if (r.message) {
                        frappe.show_alert({message: "Attendance Created Successfully", indicator: 'green'})
                    } else {
                        frappe.show_alert({message: "Can't Create Attendance", indicator: 'red'})
                    }
                }
            });
        });
    }
}