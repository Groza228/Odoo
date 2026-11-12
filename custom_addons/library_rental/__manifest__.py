{
    'name': 'Бібліотека',
    'version': '19.0.1.0.0',
    'category': 'Послуги',
    'depends': ['base', 'web'],
    'license': 'LGPL-3',
    'description': 'Облік видач книг: книги, примірники, читачі, видачі, штрафи, повернення та звіт історії видач.',
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'views/return_wizard_views.xml',
        'views/book_views.xml',
        'data/library_data.xml',
        'report/report_member_loan_history.xml',
    ],
    'demo': [
        'demo/library_rental_demo.xml',
    ],
    'installable': True,
    'application': True,
}
