# Copyright (c) 2025, espresso_app and contributors
# For license information, please see license.txt

# stone_receipt.py

import frappe
from frappe.model.document import Document
from frappe import _

class StoneReceipt(Document):
    def get_dashboard_data(self):
        return {
            'transactions': [
                {
                    'label': _('Stone Processing'),
                    'items': ['Stone Confirmation']
                }
            ],
            'non_standard_fieldnames': {
                'Stone Confirmation': 'stone_receipt_id'
            }
        }
