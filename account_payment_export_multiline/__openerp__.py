# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Payment Order Export For Multiline',
    'version': '1.0',
    'author': 'Thamini S.à.R.L',
    'website': 'http://www.thamini.com',
    'category': 'Generic Modules/Accounting',
    'description':  """
     This module allows to export payment orders into VIR200 Multiline Format
     """,
    'depends': [
        'base_vat',
        'base_iban',
        'account_payment'
    ],
    'demo_xml': [],
    'init_xml': [],
    'update_xml': [
        'security/ir.model.access.csv',
        'wizard/export_wizard_view.xml',
        'payment_export_wizard.xml',
        'payment_export_view.xml',
        'payment_export_data.xml'
    ],
    'active': False,
    'installable': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
