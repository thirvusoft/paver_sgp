$(document).ready(function () {
    let original = frappe.pages['dashboard-view'].on_page_load;
    frappe.pages['dashboard-view'].on_page_load = async function (...args) {
        await original.call(frappe.pages['dashboard-view'], ...args)

        let add_menu_item = cur_page.page.page.add_menu_item

        cur_page.page.page.add_menu_item = (...args) => {
            if (![__('Edit'), __('New'), __('Referesh All')].includes(args[0])) {
                return
            }
            add_menu_item.call(cur_page.page.page, ...args)
        }

        frappe.db.get_list('Dashboard', {
            filters: {
                module: 'Ganapathy Pavers'
            }
        }).then(dashboards => {
            dashboards.map(dashboard => {
                let name = dashboard.name;
                if (name != frappe.dashboard.dashboard_name) {
                    add_menu_item.call(cur_page.page.page, ...[name, () => frappe.set_route("dashboard-view", name), 1]);
                }
            });
        });
    }
})
