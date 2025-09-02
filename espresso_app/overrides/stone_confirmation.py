import frappe
from frappe import _

def get_stone_confirmation_dashboard(data):
    return {
        "fieldname": "custom_stone_confirmation_id",
        "non_standard_fieldnames": {
            "Purchase Order": "custom_stone_confirmation_id"
        },
        "transactions": [
            {
                "label": _("Billing"),
                "items": ["Purchase Order"]
            }
        ],
    }
