from odoo import fields, models
from odoo.exceptions import ValidationError


def _copy_condition_selection(model):
    selection = model.env['library.copy']._fields['condition'].selection
    return selection(model.env['library.copy']) if callable(selection) else selection


class LibraryReturnWizard(models.TransientModel):
    _name = 'library.return.wizard'
    _description = 'Оформлення повернення книги'

    loan_id = fields.Many2one(
        comodel_name='library.loan',
        string='Видача',
        required=True,
        ondelete='cascade',
    )
    condition_on_return = fields.Selection(
        selection=_copy_condition_selection,
        string='Стан примірника після повернення',
        required=True,
    )
    notes = fields.Text(string='Примітка')

    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        if (
            self.env.context.get('active_model') == 'library.loan'
            and 'loan_id' in fields_list
            and not values.get('loan_id')
        ):
            values['loan_id'] = self.env.context.get('active_id')
        if (
            'condition_on_return' in fields_list
            and not values.get('condition_on_return')
            and values.get('loan_id')
        ):
            loan = self.env['library.loan'].browse(values['loan_id'])
            values['condition_on_return'] = loan.copy_id.condition
        return values

    def action_confirm(self):
        self.ensure_one()
        if self.loan_id.state == 'returned':
            raise ValidationError('Цю видачу вже було повернено.')
        self.loan_id.action_return()
        if self.notes:
            self.loan_id.write({'return_note': self.notes})
        self.loan_id.copy_id.write({
            'condition': self.condition_on_return,
        })
        return {'type': 'ir.actions.act_window_close'}
