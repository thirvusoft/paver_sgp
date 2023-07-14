class calculate_taxes_and_totals(object):
    def calculate_taxes(self):
        doc_items = [i for i in (self.doc.get('items') or []) if not i.get('unacc')] # Customized by Thirvusoft
        rounding_adjustment_computed = self.doc.get('is_consolidated') and self.doc.get('rounding_adjustment')
        if not rounding_adjustment_computed:
            self.doc.rounding_adjustment = 0

        # maintain actual tax rate based on idx
        actual_tax_dict = dict([[tax.idx, flt(tax.tax_amount, tax.precision("tax_amount"))]
            for tax in self.doc.get("taxes") if tax.charge_type == "Actual"])

        for n, item in enumerate(doc_items): # Customized by Thirvusoft
            item_tax_map = self._load_item_tax_rate(item.item_tax_rate)
            for i, tax in enumerate(self.doc.get("taxes")):
                # tax_amount represents the amount of tax for the current step
                current_tax_amount = self.get_current_tax_amount(item, tax, item_tax_map)

                # Adjust divisional loss to the last item
                if tax.charge_type == "Actual":
                    actual_tax_dict[tax.idx] -= current_tax_amount
                    if n == len(doc_items) - 1: # Customized by Thirvusoft
                        current_tax_amount += actual_tax_dict[tax.idx]

                # accumulate tax amount into tax.tax_amount
                if tax.charge_type != "Actual" and \
                    not (self.discount_amount_applied and self.doc.apply_discount_on=="Grand Total"):
                        tax.tax_amount += current_tax_amount

                # store tax_amount for current item as it will be used for
                # charge type = 'On Previous Row Amount'
                tax.tax_amount_for_current_item = current_tax_amount

                # set tax after discount
                tax.tax_amount_after_discount_amount += current_tax_amount

                current_tax_amount = self.get_tax_amount_if_for_valuation_or_deduction(current_tax_amount, tax)

                # note: grand_total_for_current_item contains the contribution of
                # item's amount, previously applied tax and the current tax on that item
                if i==0:
                    tax.grand_total_for_current_item = flt(item.net_amount + current_tax_amount)
                else:
                    tax.grand_total_for_current_item = \
                        flt(self.doc.get("taxes")[i-1].grand_total_for_current_item + current_tax_amount)

                # set precision in the last item iteration
                if n == len(doc_items) - 1: # Customized by Thirvusoft
                    self.round_off_totals(tax)
                    self._set_in_company_currency(tax,
                        ["tax_amount", "tax_amount_after_discount_amount"])

                    self.round_off_base_values(tax)
                    self.set_cumulative_total(i, tax)

                    self._set_in_company_currency(tax, ["total"])

                    # adjust Discount Amount loss in last tax iteration
                    if i == (len(self.doc.get("taxes")) - 1) and self.discount_amount_applied \
                        and self.doc.discount_amount \
                        and self.doc.apply_discount_on == "Grand Total" \
                        and not rounding_adjustment_computed:
                            self.doc.rounding_adjustment = flt(self.doc.grand_total
                                - flt(self.doc.discount_amount) - tax.total,
                                self.doc.precision("rounding_adjustment"))