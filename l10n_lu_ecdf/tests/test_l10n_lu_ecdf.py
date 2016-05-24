# -*- coding: utf-8 -*-

from openerp.tests import common
from lxml import etree
from datetime import datetime
from openerp.addons.mis_builder.models.accounting_none import AccountingNone
import re as re
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class TestL10nLuEcdf(common.TransactionCase):

    def setUp(self):
        super(TestL10nLuEcdf, self).setUp()

        self.ecdf_report = self.env['ecdf.report']
        self.res_company = self.env['res.company']
        self.account_fiscalyear = self.env['account.fiscalyear']
        self.account_account = self.env['account.account']

        # Company instance
        self.company = self.env.ref('base.main_company')
        self.company.l10n_lu_matricule = '0000000000000'
        self.company.company_registry = 'L654321'
        self.company.vat = 'LU12345613'

        # 'Chart of account' instance
        self.chart_of_account = self.account_account.search([('parent_id',
                                                              '=',
                                                              False)])

        # Current fiscal year instance
        self.current_fiscal_year = self.account_fiscalyear.create({
            'company_id': self.company.id,
            'name': 'current_fiscalyear',
            'code': '123456',
            'date_start': datetime.strptime('01012015', "%d%m%Y").date(),
            'date_stop': datetime.strptime('31122015', "%d%m%Y").date()})

        self.current_fiscal_year.create_period()

        # Previous fiscal year instance
        self.previous_fiscal_year = self.account_fiscalyear.create({
            'company_id': self.company.id,
            'name': 'previous_fiscalyear',
            'code': '654321',
            'date_start': datetime.strptime('01012014', "%d%m%Y").date(),
            'date_stop': datetime.strptime('31122014', "%d%m%Y").date()})

        self.previous_fiscal_year.create_period()

        # eCDF report instance
        self.report = self.env['ecdf.report'].create({
            'language': 'FR',
            'target_move': 'posted',
            'with_pl': True,
            'with_bs': True,
            'with_ac': True,
            'reports_type': 'full',
            'current_fiscyear': self.current_fiscal_year.id,
            'prev_fiscyear': self.previous_fiscal_year.id,
            'remarks': "comment",
            'matricule': '1111111111111',
            'vat': 'LU12345678',
            'company_registry': 'L123456',
            'chart_account_id': self.chart_of_account.id})

    def test_check_matr(self):
        '''
        Matricule must be 11 or 13 characters long
        '''
        # Matricule too short (10)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.report.matricule = '1111111111'

        # Matricule's length not 11 nor 13 characters (12)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.report.matricule = '111111111112'

        # Matricule OK
        try:
            self.report.matricule = '11111111111'
        except ValidationError:
            self.fail()

        # No matricule
        try:
            self.report.matricule = None
        except ValidationError:
            self.fail()

    def test_check_rcs(self):
        '''
        RCS number must begin with an uppercase letter\
        followed by 2 to 6 digits. The first digit must not be 0
        '''
        # RCS doesn't begin with an upercase letter (lowercase letter instead)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.report.company_registry = 'l123456'

        # First digit is a zero
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.report.company_registry = 'L0234567'

        # RCS too short
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.report.company_registry = 'L1'

        # RCS dont begin with a letter
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.report.company_registry = '1123456'

        # RCS OK
        try:
            self.report.company_registry = 'L123456'
        except ValidationError:
            self.fail()

        # No RCS
        try:
            self.report.company_registry = None
        except ValidationError:
            self.fail()

    def test_check_vat(self):
        '''
        VAT number must begin with two uppercase letters followed by 8 digits.
        '''
        # VAT doesn't begin with two upercase letters (lowercase instead)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.report.vat = 'lu12345678'

        # VAT doesn't begin with two letters
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.report.vat = '0912345678'

        # VAT too short (missing digits)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.report.vat = 'LU1234567'

        # VAT OK
        try:
            self.report.vat = 'LU12345678'
        except ValidationError:
            self.fail()

        # No VAT
        try:
            self.report.vat = None
        except ValidationError:
            self.fail()

    def check_prev_fiscyear(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.report.previous_fiscal_year = self.current_fiscal_year

    def test_compute_file_name(self):
        '''
        File name must match the following pattern : 000000XyyyymmddThhmmssNN
        '''
        # Regular expression of the expected file name
        exp = r"""^\d{6}X\d{8}T\d{8}$"""
        rexp = re.compile(exp, re.X)

        self.report._compute_file_name()

        self.assertIsNotNone(rexp.match(self.report.file_name))

    def test_compute_full_file_name(self):
        '''
        Full file name must be the computed file name with ".xml" at the end
        '''
        self.report._compute_full_file_name()
        expected = self.report.file_name + '.xml'
        self.assertEqual(self.report.full_file_name, expected)

    def test_get_ecdf_file_version(self):
        report_file_version = self.report.get_ecdf_file_version()
        file_version = '1.1'

        self.assertEqual(report_file_version, file_version)

    def test_get_interface(self):
        report_interface = self.report.get_interface()
        interface = 'COPL3'

        self.assertEqual(report_interface, interface)

    def test_get_language(self):
        language = self.report.get_language()
        expected = 'FR'

        self.assertEqual(language, expected)

    # GETTERS AGENT

    def test_get_matr_agent(self):
        # With a matricule set to the agent
        report_matr = self.report.get_matr_agent()
        expected = '1111111111111'
        self.assertEqual(report_matr, expected)

        # With no matricule set to the agent
        self.report.matricule = False
        report_matr = self.report.get_matr_agent()
        # The excpected matricule is the company one
        expected = '0000000000000'
        self.assertEqual(report_matr, expected)

    def test_get_rcs_agent(self):
        # With a rcs number set to the agent
        report_rcs = self.report.get_rcs_agent()
        expected = 'L123456'
        self.assertEqual(report_rcs, expected)

        # With no rcs number set to the agent
        self.report.company_registry = False
        report_rcs = self.report.get_rcs_agent()
        # The expected rcs is the company one
        expected = 'L654321'
        self.assertEqual(report_rcs, expected)

    def test_get_vat_agent(self):
        # With a vat number set to the agent, without the two letters
        report_vat = self.report.get_vat_agent()
        expected = '12345678'
        self.assertEqual(report_vat, expected)

        # With no vat number set to the agent
        self.report.vat = False
        report_vat = self.report.get_vat_agent()
        # The expected vat is the company one, without the two letters
        expected = '12345613'
        self.assertEqual(report_vat, expected)

    # GETTERS DECLARER

    def test_get_matr_declarer(self):
        # With a matricule set to the company
        declarer_matr = self.report.get_matr_declarer()
        expected = '0000000000000'
        self.assertEqual(declarer_matr, expected)

        # With no matricule set to the company
        self.company.l10n_lu_matricule = False
        with self.assertRaises(ValueError), self.cr.savepoint():
            declarer_matr = self.report.get_matr_declarer()

    def test_get_rcs_declarer(self):
        # With a rcs number set to the company
        declarer_rcs = self.report.get_rcs_declarer()
        expected = 'L654321'
        self.assertEqual(declarer_rcs, expected)

        # With no rcs number set to the company
        self.company.company_registry = False
        declarer_rcs = self.report.get_rcs_declarer()
        expected = 'NE'
        self.assertEqual(declarer_rcs, expected)

    def test_get_vat_declarer(self):
        # With a vat number set to the company
        declarer_vat = self.report.get_vat_declarer()
        expected = '12345613'
        self.assertEqual(declarer_vat, expected)

        # With no vat number set to the company
        self.company.vat = False
        declarer_vat = self.report.get_vat_declarer()
        expected = 'NE'
        self.assertEqual(declarer_vat, expected)

    def test_append_num_field(self):
        '''
        Test of bordeline cases of the method append_num_field
        '''
        # Initial data : code not in KEEP_ZERO
        ecdf = '123'
        comment = "A comment"

        # Test with valid float value
        element = etree.Element('FormData')
        val = 5.5
        self.report._append_num_field(element, ecdf, val, False, comment)
        expected = '<FormData><!--A comment--><NumericField id="123">\
5,50</NumericField></FormData>'
        self.assertEqual(etree.tostring(element), expected)

        # Test with None value, code not in KEEP_ZERO
        element = etree.Element('FormData')
        val = None
        self.report._append_num_field(element, ecdf, val, False, comment)
        expected = '<FormData/>'
        self.assertEqual(etree.tostring(element), expected)

        # Test with AccountingNone value, code not in KEEP_ZERO
        element = etree.Element('FormData')
        val = AccountingNone
        self.report._append_num_field(element, ecdf, val, False, comment)
        expected = '<FormData/>'
        self.assertEqual(etree.tostring(element), expected)

        # Data : code in KEEP_ZERO
        ecdf = '639'

        # Test with None value, code in KEEP_ZERO
        element = etree.Element('FormData')
        val = None
        self.report._append_num_field(element, ecdf, val, False, comment)
        expected = '<FormData><!--A comment--><NumericField id="639">0,00\
</NumericField></FormData>'
        self.assertEqual(etree.tostring(element), expected)

        # Test with AccountingNone value, code in KEEP_ZERO
        element = etree.Element('FormData')
        val = AccountingNone
        self.report._append_num_field(element, ecdf, val, False, comment)
        expected = '<FormData><!--A comment--><NumericField id="639">0,00\
</NumericField></FormData>'
        self.assertEqual(etree.tostring(element), expected)

        # Test with None value, code not in KEEP_ZERO
        element = etree.Element('FormData')
        val = None
        self.report._append_num_field(element, ecdf, val, True, comment)
        expected = '<FormData><!--A comment--><NumericField id="639">0,00\
</NumericField></FormData>'
        self.assertEqual(etree.tostring(element), expected)

        # Test with AccountingNone value, code not in KEEP_ZERO
        element = etree.Element('FormData')
        val = AccountingNone
        self.report._append_num_field(element, ecdf, val, True, comment)
        expected = '<FormData><!--A comment--><NumericField id="639">0,00\
</NumericField></FormData>'
        self.assertEqual(etree.tostring(element), expected)

        # Test with valid float value
        element = etree.Element('FormData')
        val = 5.5
        self.report._append_num_field(element, ecdf, val, True, comment)
        expected = '<FormData><!--A comment--><NumericField id="639">0,00\
</NumericField></FormData>'
        self.assertEqual(etree.tostring(element), expected)

        # Test without comment
        element = etree.Element('FormData')
        val = 5.5
        self.report._append_num_field(element, ecdf, val, True)
        expected = '<FormData><NumericField id="639">0,00</NumericField>\
</FormData>'
        self.assertEqual(etree.tostring(element), expected)

    def test_append_fr_lines(self):
        '''
        Test of method 'append_fr_lines' with and without previous year
        '''
        data_current = {'content': [{
            'kpi_name': 'A. CHARGES',
            'kpi_technical_name': 'ecdf_642_641',
            'cols': [{'suffix': '\u20ac',
                      'prefix': False,
                      'period_id': None,
                      'drilldown': False,
                      'is_percentage': False,
                      'dp': 0,
                      'style': None,
                      'val': 123,
                      'val_r': '\u202f724\xa0747\xa0\u20ac',
                      'expr': 'ecdf_602_601 + ecdf_604_603'}]},
            {'kpi_name': 'empty',
             'kpi_technical_name': '',
             'cols': [{}]}]}

        data_previous = {'content': [{
            'kpi_name': 'A. CHARGES',
            'kpi_technical_name': 'ecdf_642_641',
            'cols': [{'suffix': '\u20ac',
                      'prefix': False,
                      'period_id': None,
                      'drilldown': False,
                      'is_percentage': False,
                      'dp': 0,
                      'style': None,
                      'val': 321,
                      'val_r': '\u202f724\xa0747\xa0\u20ac',
                      'expr': 'ecdf_602_601 + ecdf_604_603'}]},
            {'kpi_name': 'empty',
             'kpi_technical_name': '',
             'cols': [{}]}]}

        # Test with no previous year
        element = etree.Element('FormData')
        self.report._append_fr_lines(data_current, element)
        expected = '<FormData><!-- current - A. CHARGES -->\
<NumericField id="641">123,00</NumericField><!-- no previous year-->\
<NumericField id="642">0,00</NumericField></FormData>'
        self.assertEqual(etree.tostring(element), expected)

        # Test with previous year
        element = etree.Element('FormData')
        self.report._append_fr_lines(data_current, element, data_previous)
        expected = '<FormData><!-- current - A. CHARGES -->\
<NumericField id="641">123,00</NumericField><!-- previous - A. CHARGES -->\
<NumericField id="642">321,00</NumericField></FormData>'
        self.assertEqual(etree.tostring(element), expected)

    def test_print_xml(self):
        '''
        Main test : generation of all types of reports
        Chart of account, Profit and Loss, Balance Sheet
        '''
        # Type : full
        self.report.print_xml()

        # Type abbreviated
        self.report.reports_type = 'abbreviated'
        self.report.print_xml()

        # With no previous fiscal year, abbreaviated
        self.report.prev_fiscyear = False
        self.report.print_xml()

        # With no previous year, full
        self.report.reports_type = 'full'
        self.report.print_xml()
