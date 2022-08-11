function setup_datatable(values) {
    this.$datatable_wrapper.empty();
    this.datatable = new DataTable(this.$datatable_wrapper[0], {
        columns: this.columns,
        data: this.get_data(values),
        getEditor: this.get_editing_object.bind(this),
        language: frappe.boot.lang,
        translations: frappe.utils.datatable.get_translations(),
        checkboxColumn: true,
        inlineFilters: true,
        showTotalRow: true,    ////// Customized by Thirvusoft
        cellHeight: 35,
        direction: frappe.utils.is_rtl() ? 'rtl' : 'ltr',
        events: {
            onRemoveColumn: (column) => {
                this.remove_column_from_datatable(column);
            },
            onSwitchColumn: (column1, column2) => {
                this.switch_column(column1, column2);
            },
            onCheckRow: () => {
                const checked_items = this.get_checked_items();
                this.toggle_actions_menu_button(checked_items.length > 0);
            }
        },
        hooks: {
            columnTotal: frappe.utils.report_column_total
        },
        headerDropdown: [{
            label: __('Add Column'),
            action: (datatabe_col) => {
                let columns_in_picker = [];
                const columns = this.get_columns_for_picker();

                columns_in_picker = columns[this.doctype]
                    .filter(df => !this.is_column_added(df))
                    .map(df => ({
                        label: __(df.label),
                        value: df.fieldname
                    }));

                delete columns[this.doctype];

                for (let cdt in columns) {
                    columns[cdt]
                        .filter(df => !this.is_column_added(df))
                        .map(df => ({
                            label: __(df.label) + ` (${cdt})`,
                            value: df.fieldname + ',' + cdt
                        }))
                        .forEach(df => columns_in_picker.push(df));
                }

                const d = new frappe.ui.Dialog({
                    title: __('Add Column'),
                    fields: [
                        {
                            label: __('Select Column'),
                            fieldname: 'column',
                            fieldtype: 'Autocomplete',
                            options: columns_in_picker
                        },
                        {
                            label: __('Insert Column Before {0}', [__(datatabe_col.docfield.label).bold()]),
                            fieldname: 'insert_before',
                            fieldtype: 'Check'
                        }
                    ],
                    primary_action: ({ column, insert_before }) => {
                        if (!columns_in_picker.map(col => col.value).includes(column)) {
                            frappe.show_alert({message: __('Invalid column'), indicator: 'orange'});
                            d.hide();
                            return;
                        }

                        let doctype = this.doctype;
                        if (column.includes(',')) {
                            [column, doctype] = column.split(',');
                        }


                        let index = datatabe_col.colIndex;
                        if (insert_before) {
                            index = index - 1;
                        }

                        this.add_column_to_datatable(column, doctype, index);
                        d.hide();
                    }
                });

                d.show();
            }
        }]
    });
}


// let items = [   
// //     {
// //     	label: __('Show Totals'),
// //     	action: () => {
// //     		this.add_totals_row = !this.add_totals_row;
// //     		this.save_view_user_settings({
// //     			add_totals_row: this.add_totals_row
// //     		});
// //     		this.datatable.refresh(this.get_data(this.data));
// //     	}
// //     },
//      Customized by Thirvusoft