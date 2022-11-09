import frappe
import erpnext
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.stock.get_item_details import get_item_details

def dn_tax_validation(self, event=None):
    """
        For Delivery Note
    """
    for row in self.items:
        if row.unacc:
            row.item_tax_template=''
            row.item_tax_rate=''

def tax_validation(self, event=None):
    """
        For Sales Order and Sales Invoice
    """
    if self.branch and not frappe.get_value("Branch", self.branch, "is_accounting"):
        for row in self.items:
            row.unacc=1
            row.item_tax_template=None
    

def set_missing_item_details_tax(self, for_validate=False):
    """set missing item values except item_tax_rate"""
    force_item_fields = ("item_group", "brand", "stock_uom", "is_fixed_asset", #"item_tax_rate",
	"pricing_rules", "weight_per_unit", "weight_uom", "total_weight")
    from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

    if hasattr(self, "items"):
        parent_dict = {}
        for fieldname in self.meta.get_valid_columns():
            parent_dict[fieldname] = self.get(fieldname)

        if self.doctype in ["Quotation", "Sales Order", "Delivery Note", "Sales Invoice"]:
            document_type = "{} Item".format(self.doctype)
            parent_dict.update({"document_type": document_type})

        # party_name field used for customer in quotation
        if self.doctype == "Quotation" and self.quotation_to == "Customer" and parent_dict.get("party_name"):
            parent_dict.update({"customer": parent_dict.get("party_name")})

        self.pricing_rules = []
        for item in self.get("items"):
            if item.get("item_code"):
                args = parent_dict.copy()
                args.update(item.as_dict())

                args["doctype"] = self.doctype
                args["name"] = self.name
                args["child_docname"] = item.name
                args["ignore_pricing_rule"] = self.ignore_pricing_rule if hasattr(self, 'ignore_pricing_rule') else 0

                if not args.get("transaction_date"):
                    args["transaction_date"] = args.get("posting_date")

                if self.get("is_subcontracted"):
                    args["is_subcontracted"] = self.is_subcontracted

                ret = get_item_details(args, self, for_validate=True, overwrite_warehouse=False)

                for fieldname, value in ret.items():
                    if item.meta.get_field(fieldname) and value is not None:
                        if (item.get(fieldname) is None or fieldname in force_item_fields):
                            item.set(fieldname, value)

                        elif fieldname in ['cost_center', 'conversion_factor'] and not item.get(fieldname):
                            item.set(fieldname, value)

                        elif fieldname == "serial_no":
                            # Ensure that serial numbers are matched against Stock UOM
                            item_conversion_factor = item.get("conversion_factor") or 1.0
                            item_qty = abs(item.get("qty")) * item_conversion_factor

                            if item_qty != len(get_serial_nos(item.get('serial_no'))):
                                item.set(fieldname, value)

                        elif (
                            ret.get("pricing_rule_removed")
                            and value is not None
                            and fieldname
                            in [
                                "discount_percentage",
                                "discount_amount",
                                "rate",
                                "margin_rate_or_amount",
                                "margin_type",
                                "remove_free_item",
                            ]
                        ):
                            # reset pricing rule fields if pricing_rule_removed
                            item.set(fieldname, value)

                if self.doctype in ["Purchase Invoice", "Sales Invoice"] and item.meta.get_field('is_fixed_asset'):
                    item.set('is_fixed_asset', ret.get('is_fixed_asset', 0))

                # Double check for cost center
                # Items add via promotional scheme may not have cost center set
                if hasattr(item, 'cost_center') and not item.get('cost_center'):
                    item.set('cost_center', self.get('cost_center') or erpnext.get_default_cost_center(self.company))

                if ret.get("pricing_rules"):
                    self.apply_pricing_rule_on_items(item, ret)
                    self.set_pricing_rule_details(item, ret)

        if self.doctype == "Purchase Invoice":
            self.set_expense_account(for_validate)

AccountsController.set_missing_item_details = set_missing_item_details_tax