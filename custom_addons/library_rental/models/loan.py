from odoo import fields, models


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
        selection=[
            ('active', 'Активна'),
            ('returned', 'Повернена'),
        ],
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
