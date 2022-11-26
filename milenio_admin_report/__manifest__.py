# Copyright 2022, Luis Triana
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Milenio Admon Report',
    'summary': 'Module summary',
    'version': '12.0.1.0.0',
    'category': 'Uncategorized',
    'website': 'https://odoo-community.org/',
    'author': 'Luis Triana, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'base',
        'account'
    ],
    'data': [
        'data/data.xml',
        'report/admon_summary.xml',
        'wizard/admon_order_summary_wizard.xml',
    ]
}
