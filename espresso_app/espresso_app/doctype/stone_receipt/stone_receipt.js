frappe.ui.form.on('Stone Receipt', {
    refresh: function(frm) {
        if (!frm.doc.__islocal) {
            frappe.db.get_list('Stone Confirmation', {
                filters: { stone_receipt_id: frm.doc.name },
                fields: ['name']
            }).then(records => {
                let count = records.length;

                // Target dashboard link area
                let $link = frm.dashboard.transactions_area.find("[data-doctype='Stone Confirmation']");
                if ($link.length) {
                    // Agar 0 hai to sirf text, warna counter bhi
                    let label = count > 0
                        ? `${count} Stone Confirmation${count > 1 ? "s" : ""}`
                        : `Stone Confirmation`;

                    // UI same jaise Stone Request me tha
                    $link.html(`
                        <span class="custom-stone-link" 
                              style="background:#f5f5f5; padding:4px 8px; border-radius:6px; cursor:pointer; text-decoration:underline; display:inline-block;">
                            ${label}
                        </span>
                    `);

                    // Click action
                    $link.off("click").on("click", function() {
                        if (count === 1) {
                            frappe.set_route("Form", "Stone Confirmation", records[0].name);
                        } else if (count > 1) {
                            frappe.route_options = { stone_receipt_id: frm.doc.name };
                            frappe.set_route("List", "Stone Confirmation");
                        } else {
                            frappe.msgprint(__('No Stone Confirmation found'));
                        }
                    });
                }
            });
        }
    }
});
