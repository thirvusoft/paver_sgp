frappe.provide("ganapathy_pavers");

ganapathy_pavers.apply_paver_report_filters = async function (from_date, to_date, machine, field_class) {
    let production_item_name = [], filters = { docstatus: ["<", 2] }
    if (from_date) {
        filters["from_time"] = [">=", from_date]
    }
    if (to_date) {
        filters["from_time"] = ["<=", to_date]
    }
    if (from_date && to_date) {
        filters["from_time"] = ["BETWEEN", [from_date, to_date]]
    }
    if (machine && typeof(type)=="object") {
        filters["work_station"] = ["in", machine]
    }
    if (machine && typeof(type)=="string") {
        filters["work_station"] = machine
    }
    await frappe.db.get_list("Material Manufacturing", {
        filters: filters,
        fields: ["item_to_manufacture"],
        limit: 0
    }).then(production_items => {
        (production_items || []).forEach(data => {
            if (!production_item_name.includes(data.item_to_manufacture))
                production_item_name.push(data.item_to_manufacture)
        })
        field_class.get_query = function () {
            return {
                filters: {
                    name: [
                        "in",
                        production_item_name
                    ]
                }
            }
        }
    })

}

ganapathy_pavers.apply_cwall_report_filters = async function (from_date, to_date, field_class, type) {
    let production_item_name = [], filters = { docstatus: ["<", 2] }
    if (from_date) {
        filters["molding_date"] = [">=", from_date]
    }
    if (to_date) {
        filters["molding_date"] = ["<=", to_date]
    }
    if (from_date && to_date) {
        filters["molding_date"] = ["BETWEEN", [from_date, to_date]]
    }
    if (type && typeof(type)=="object") {
        filters["type"] = ["in", type]
    }
    if (type && typeof(type)=="string") {
        filters["type"] = type
    }
    await frappe.db.get_list("CW Manufacturing", {
        filters: filters,
        fields: ["`tabCW Items`.item"],
        limit: 0
    }).then(production_items => {
        (production_items || []).forEach(data => {
            if (!production_item_name.includes(data.item))
                production_item_name.push(data.item)
        })
        field_class.get_query = function () {
            return {
                filters: {
                    name: [
                        "in",
                        production_item_name
                    ]
                }
            }
        }
    })

}


ganapathy_pavers.apply_sbc_report_filters = async function (from_date, to_date, field_class) {
    let production_item_name = [], filters = { docstatus: ["<", 2] }
    if (from_date) {
        filters["to_time"] = [">=", from_date]
    }
    if (to_date) {
        filters["to_time"] = ["<=", to_date]
    }
    if (from_date && to_date) {
        filters["to_time"] = ["BETWEEN", [from_date, to_date]]
    }
   
    await frappe.db.get_list("Shot Blast Costing", {
        filters: filters,
        fields: ["`tabShot Blast Items`.item_name"],
        limit: 0
    }).then(production_items => {
        (production_items || []).forEach(data => {
            if (!production_item_name.includes(data.item_name))
                production_item_name.push(data.item_name)
        })
        field_class.get_query = function () {
            return {
                filters: {
                    name: [
                        "in",
                        production_item_name
                    ]
                }
            }
        }
    })

}

