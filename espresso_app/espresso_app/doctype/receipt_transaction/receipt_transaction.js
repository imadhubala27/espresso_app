// frappe.ui.form.on('Receipt Transaction', {
//     refresh(frm) {
//         if (!frm.doc.__islocal) {
//             frappe.call({
//                 method: "espresso_app.overrides.stone_confirmation.get_purchase_invoice_count",
//                 args: {
//                     stone_confirmation_id: frm.doc.name
//                 },
//                 callback: function(r) {
//                     if (r.message > 0) {
//                         frm.dashboard.set_headline(
//                             __("Billing: {0} Purchase Invoice(s)", [r.message])
//                         );

//                         frm.dashboard.add_transactions({
//                             'Billing': [{
//                                 doctype: 'Purchase Invoice',
//                                 name: __("Purchase Invoice ({0})", [r.message]),
//                                 route_options: {
//                                     "items.custom_stone_confirmation_id": frm.doc.name
//                                 }
//                             }]
//                         });
//                     }
//                 }
//             });
//         }
//     }
// });
