from odoo import fields, models
from odoo.exceptions import ValidationError


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
    due_date = fields.Date(string='Повернути до')
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

    def action_return(self):
        for rec in self:
            if rec.state == 'returned':
                raise ValidationError('Цю видачу вже було повернено.')
            rec.state = 'returned'
            if not rec.return_date:
                rec.return_date = fields.Date.context_today(rec)
        return True
