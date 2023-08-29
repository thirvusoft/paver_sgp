#apps/erpnext/erpnext/accounts/report/supplier_ledger_summary/supplier_ledger_summary.py

#------------------------------------------------------------------------------------------------------------------------------------------
# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from erpnext.accounts.report.customer_ledger_summary.customer_ledger_summary import (
	PartyLedgerSummaryReport,
)


def execute(filters=None):
	args = {
		"party_type": "Supplier",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	columns, data = PartyLedgerSummaryReport(filters).run(args)
	return columns, sorted(data, key = lambda x: ((x.get("party") or "")[0] if len((x.get("party") or ""))>0 else "", (x.get("closing_balance") or 0)))