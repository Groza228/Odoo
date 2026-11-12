from odoo import api, fields, models
from odoo.exceptions import ValidationError


LOAN_PERIOD_DAYS = 14


class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Видача книги'

    copy_id = fields.Many2one(
        comodel_name='library.copy',
        string='Примірник',
        required=True,
        ondelete='restrict',
    )
    member_id = fields.Many2one(
        comodel_name='library.member',
        string='Читач',
        required=True,
        ondelete='restrict',
    )
    loan_date = fields.Date(string='Дата видачі', default=fields.Date.today, required=True)
    due_date = fields.Date(
        string='Повернути до',
        compute='_compute_due_date',
        store=True,
    )
    return_date = fields.Date(string='Дата повернення')
    state = fields.Selection(
        selection=[('active', 'Видано'), ('returned', 'Повернено')],
        string='Статус',
        default='active',
        required=True,
    )
    book_id = fields.Many2one(
        comodel_name='library.book',
        related='copy_id.book_id',
        string='Книга',
        store=True,
        readonly=True,
    )
    book_author = fields.Char(
        related='copy_id.book_id.author',
        string='Автор',
        readonly=True,
    )
    inventory_number = fields.Char(
        related='copy_id.inventory_number',
        string='Інвентарний номер',
        readonly=True,
    )
    member_name = fields.Char(
        related='member_id.name',
        string='Імʼя читача',
        readonly=True,
    )

    @api.depends('loan_date')
    def _compute_due_date(self):
        for rec in self:
            rec.due_date = (
                fields.Date.add(rec.loan_date, days=LOAN_PERIOD_DAYS)
                if rec.loan_date
                else False
            )

    def action_return(self):
        for rec in self:
            if rec.state == 'returned':
                raise ValidationError('Цю видачу вже було повернено.')
            rec.state = 'returned'
            if not rec.return_date:
                rec.return_date = fields.Date.context_today(rec)
        return True
