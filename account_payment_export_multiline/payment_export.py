##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from osv import osv,fields
import netsvc
import pooler


class account_pay(osv.osv):
    _name = "account.pay"
    _description = "Payment Export History"
    _columns = {
        'name': fields.binary('Export file', readonly=True),
        'note': fields.text('Creation log', readonly=True),

    }
account_pay()


class res_partner_bank(osv.osv):
    _inherit = "res.partner.bank"
    _columns = {
                'institution_code':fields.char('Institution code.', size=32),
    }
res_partner_bank()


class payment_order(osv.osv):
    _inherit = "payment.order"

    def get_wizard(self,mode):
        if mode=='pay':
            return self._module,'wizard_account_payment_create'
        return super(payment_order,self).get_wizard(mode)
payment_order()