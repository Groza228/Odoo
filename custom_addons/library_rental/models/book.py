from odoo import fields, models


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Книга бібліотеки'

    name = fields.Char(string='Назва', required=True)
    author = fields.Char(string='Автор')
    isbn = fields.Char(string='ISBN')
    publish_year = fields.Integer(string='Рік видання')
    copy_ids = fields.One2many(
        comodel_name='library.copy',
        inverse_name='book_id',
        string='Примірники',
    )
