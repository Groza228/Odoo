from odoo import api, fields, models
from odoo.exceptions import ValidationError


LOAN_PERIOD_DAYS = 14
FINE_PER_DAY = 5.0


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
    fine_amount = fields.Float(
        string='Штраф (фінальний)',
        compute='_compute_fine_amount',
        store=True,
    )
    is_overdue = fields.Boolean(
        string='Прострочено',
        compute='_compute_is_overdue',
        search='_search_is_overdue',
    )
    days_late = fields.Integer(
        string='Днів прострочення',
        compute='_compute_days_late',
    )
    current_fine = fields.Float(
        string='Штраф (поточний)',
        compute='_compute_current_fine',
    )
    display_state = fields.Selection(
        selection=[
            ('active', 'Видано'),
            ('overdue', 'Прострочено'),
            ('returned', 'Повернено'),
        ],
        string='Етап',
        compute='_compute_display_state',
    )
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

    @api.depends('due_date', 'return_date')
    def _compute_fine_amount(self):
        for rec in self:
            rec.fine_amount = (
                (rec.return_date - rec.due_date).days * FINE_PER_DAY
                if rec.return_date
                and rec.due_date
                and rec.return_date > rec.due_date
                else 0.0
            )

    @api.depends('state', 'due_date')
    def _compute_is_overdue(self):
        for rec in self:
            today = fields.Date.context_today(rec)
            rec.is_overdue = bool(
                rec.state == 'active'
                and rec.due_date
                and rec.due_date < today
            )

    def _search_is_overdue(self, operator, value):
        if operator not in ('=', '!='):
            raise NotImplementedError(
                'Оператор пошуку прострочення має бути "=" або "!=".'
            )
        is_true = value in (True, 1, '1', 'True', 'true')
        should_match_overdue = is_true if operator == '=' else not is_true
        if should_match_overdue:
            return [
                ('state', '=', 'active'),
                ('due_date', '<', fields.Date.context_today(self)),
            ]
        return [
            '|',
            ('state', '!=', 'active'),
            '|',
            ('due_date', '=', False),
            ('due_date', '>=', fields.Date.context_today(self)),
        ]

    @api.depends('state', 'due_date', 'return_date')
    def _compute_days_late(self):
        for rec in self:
            if rec.state == 'returned':
                rec.days_late = (
                    max((rec.return_date - rec.due_date).days, 0)
                    if rec.return_date and rec.due_date
                    else 0
                )
            else:
                today = fields.Date.context_today(rec)
                rec.days_late = (
                    max((today - rec.due_date).days, 0)
                    if rec.due_date
                    else 0
                )

    @api.depends('state', 'due_date', 'return_date', 'fine_amount')
    def _compute_current_fine(self):
        for rec in self:
            rec.current_fine = (
                rec.fine_amount
                if rec.state == 'returned'
                else rec.days_late * FINE_PER_DAY
            )

    @api.depends('state', 'due_date')
    def _compute_display_state(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state == 'returned':
                rec.display_state = 'returned'
            elif rec.due_date and rec.due_date < today:
                rec.display_state = 'overdue'
            else:
                rec.display_state = 'active'

    def action_return(self):
        for rec in self:
            if rec.state == 'returned':
                raise ValidationError('Цю видачу вже було повернено.')
            rec.state = 'returned'
            if not rec.return_date:
                rec.return_date = fields.Date.context_today(rec)
        return True

    def action_restore(self):
        for rec in self:
            if rec.state != 'returned':
                raise ValidationError('Відновити можна лише повернену видачу.')
            conflict = self.search_count([
                ('copy_id', '=', rec.copy_id.id),
                ('state', '=', 'active'),
                ('id', '!=', rec.id),
            ])
            if conflict:
                raise ValidationError(
                    'Цей примірник уже має іншу активну видачу, '
                    'тому відновити цю видачу неможливо.'
                )
            rec.write({'state': 'active', 'return_date': False})
        return True
