from odoo import fields, models


class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Читач бібліотеки'

    name = fields.Char(string='Імʼя', required=True)
    membership_number = fields.Char(string='Номер читацького квитка', required=True)
    user_id = fields.Many2one(
        'res.users',
        string='Користувач',
        ondelete='set null',
    )

    _membership_number_unique = models.Constraint(
        'UNIQUE(membership_number)',
        'Номер читацького квитка має бути унікальним.',
    )
    _user_id_unique = models.Constraint(
        'UNIQUE(user_id)',
        'Користувач може бути привʼязаний лише до одного читача.',
    )
