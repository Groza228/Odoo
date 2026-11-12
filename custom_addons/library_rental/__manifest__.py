{
    'name': 'Бібліотека',
    'version': '19.0.1.0.0',
    'category': 'Послуги',
    'depends': ['base'],
    'license': 'LGPL-3',
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'views/book_views.xml',
    ],
    'demo': [
        'demo/library_rental_demo.xml',
    ],
    'installable': True,
    'application': True,
}
