from odoo import fields, models


class LibraryCopy(models.Model):
    _name = 'library.copy'
    _description = 'Примірник книги'

    book_id = fields.Many2one(
        comodel_name='library.book',
        string='Книга',
        required=True,
        ondelete='restrict',
    )
    inventory_number = fields.Char(string='Інвентарний номер', required=True)
    condition = fields.Selection(
        selection=[
            ('new', 'Новий'),
            ('good', 'Добрий'),
            ('damaged', 'Пошкоджений'),
        ],
        default='good',
        required=True,
    )
