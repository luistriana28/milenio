from datetime import datetime, timedelta
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import ValidationError


class AdmonSummaryReportWizard(models.TransientModel):
    _name = 'admon.summary.report.wizard'

    date_start = fields.Date(string='Start Date', required=True,
        default=fields.Date.context_today)
    date_end = fields.Date(string='End Date', required=True,
        default=fields.Date.context_today)

    @api.onchange('date_start')
    def _onchange_date_start(self):
        if self.date_start and self.date_end and self.date_end < self.date_start:
            self.date_end = self.date_start

    @api.onchange('date_end')
    def _onchange_date_end(self):
        if self.date_end and self.date_end < self.date_start:
            self.date_start = self.date_end

    @api.multi
    def print_report(self):
        """
        data
        """
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'date_start': self.date_start, 
                'date_end': self.date_end,
            },
        }
        return self.env.ref(
            'milenio_admin_report.admon_summary_report').report_action(
            self, data=data)


class ReportAdmonSummaryReportView(models.AbstractModel):
    """
        Abstract Model specially for report template.
        _name = Use prefix `report.` along with `module_name.report_name`
    """
    _name = 'report.milenio_admin_report.admon_summary_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        start_date = fields.Date.to_string(
            fields.Date.from_string(date_start))
        end_date = fields.Date.to_string(
            fields.Date.from_string(date_end))

        docs = []
        total_invoiced = 0
        total_expense = 0
        taxes = 0
        services = 0
        bank_comission = 0
        sale_comission = 0
        maintenance = 0
        payroll = 0
        total_purchased = 0
        other_expense = 0
        credit_card = 0

        invoice_ids = self.env['account.invoice'].search([
            ('date_invoice', '>=', start_date),
            ('date_invoice', '<=', end_date),
            ('state', 'in', ['open', 'paid']), ('type', '=', 'out_invoice')])
        invoices = sum(inv.amount_total for inv in invoice_ids)
        total_invoiced += invoices

        purchase_ids = self.env['account.invoice'].search([
            ('date_invoice', '>=', start_date),
            ('date_invoice', '<=', end_date),
            ('state', 'in', ['open', 'paid']),
            ('type', '=', 'in_invoice')])
        purchases = sum(purc.amount_total for purc in purchase_ids)
        total_purchased += purchases

        for purc in purchase_ids:
            if purc.partner_id.category_id:
                for categ in purc.partner_id.category_id:
                    if categ.name == 'IMPUESTOS':
                        taxes += purc.amount_total
                    if categ.name == 'COMISION BANCO':
                        bank_comission += purc.amount_total
                    if categ.name == 'COMISION RENTA':
                        sale_comission += purc.amount_total
                    if categ.name == 'NOMINA':
                        payroll += purc.amount_total
                    if categ.name == 'SERVICIOS':
                        services += purc.amount_total
                    if categ.name == 'MANTENIMIENTO':
                        maintenance += purc.amount_total
                    if categ.name == 'TARJETAS CREDITO':
                        credit_card += purc.amount_total
            else:
                other_expense += purc.amount_total

        docs.append({
            'total_invoiced': total_invoiced,
            'taxes': taxes,
            'bank_comission': bank_comission,
            'sale_comission': sale_comission,
            'payroll': payroll,
            'services': services,
            'maintenance': maintenance,
            'credit_card': credit_card,
            'total_purchased': total_purchased,
            'utility': (total_invoiced - total_purchased),
            'other_expense': other_expense,
            'company': self.env.user.company_id
        })

        docargs = {
            'date_start': data['form']['date_start'],
            'date_end': data['form']['date_end'],
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
        }

        return docargs
