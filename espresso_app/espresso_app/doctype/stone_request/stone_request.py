# Copyright (c) 2025, espresso_app and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class StoneRequest(Document):
    def get_dashboard_data(self):
        return {
            'transactions': [
                {
                    'label': _('Stone Management'),
                    'items': ['Stone Receipt']
                }
            ],
            'non_standard_fieldnames': {
                'Stone Receipt': 'sr_id'
            }
        }
