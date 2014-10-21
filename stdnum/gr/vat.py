# vat.py - functions for handling Greek VAT numbers
# coding: utf-8
#
# Copyright (C) 2012, 2013 Arthur de Jong
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA

"""FPA, ΦΠΑ, ΑΦΜ (Αριθμός Φορολογικού Μητρώου, the Greek VAT number).

The FPA is a 9-digit number with a simple checksum.

>>> compact('GR 23456783')
'023456783'
>>> validate('EL 094259216 ')
'094259216'
>>> validate('EL 123456781')
Traceback (most recent call last):
    ...
InvalidChecksum: ...
"""

from stdnum.exceptions import *
from stdnum.util import clean

class CheckException(Exception):
    def __init__(self, code, descr):
        self.args = (code, descr)

    def __str__(self):
        return self.args[0] or ''

    def __unicode__(self):
        return self.args[1] or ''

    def __repr__(self):
        return u'<vat.CheckException %s >' % self.args[0]

def compact(number):
    """Convert the number to the minimal representation. This strips the
    number of any valid separators and removes surrounding whitespace."""
    number = clean(number, ' -./:').upper().strip()
    if number.startswith('EL') or number.startswith('GR'):
        number = number[2:]
    if len(number) == 8:
        number = '0' + number  # old format had 8 digits
    return number


def calc_check_digit(number):
    """Calculate the check digit. The number passed should not have the
    check digit included."""
    checksum = 0
    for n in number:
        checksum = checksum * 2 + int(n)
    return str(checksum * 2 % 11 % 10)


def validate(number):
    """Checks to see if the number provided is a valid VAT number. This
    checks the length, formatting and check digit."""
    number = compact(number)
    if not number.isdigit():
        raise InvalidFormat()
    if len(number) != 9:
        raise InvalidLength()
    if calc_check_digit(number[:-1]) != number[-1]:
        raise InvalidChecksum()
    return number


def is_valid(number):
    """Checks to see if the number provided is a valid VAT number. This
    checks the length, formatting and check digit."""
    try:
        return bool(validate(number))
    except ValidationError:
        return False

class VATchecker(object):
    GSIS_HOST = 'https://www1.gsis.gr'
    GSIS_WSDL = '/webtax2/wsgsis/RgWsPublic/RgWsPublicPort?wsdl'

    @classmethod
    def _getClient(cls, **options):
        """Establish a connection and get a `suds.Client`

            For internal purposes, only
        """
        from suds.client import Client
        try:
            from urllib import getproxies
        except ImportError:
            from urllib.request import getproxies
        return Client(cls.GSIS_HOST + cls.GSIS_WSDL, proxy=getproxies(), **options)

    def __init__(self, user_login, user_passwd):
        """ Initialize a checker object, with authenticated access
        """
        from suds.cache import ObjectCache
        from suds.wsse import Security, UsernameToken
        if not (user_login and user_passwd):
            raise RuntimeError("You must specify user AFM and token for authentication")
        security = Security()
        security.tokens.append(UsernameToken(user_login, user_passwd))
        self._client = self._getClient(wsse=security)

    @classmethod
    def getVersion(cls):
        client = cls._getClient()
        return unicode(client.service.rgWsPublicVersionInfo())

    def getAFMinfo(self, called_for, called_by):
        """Retrieve full VAT-number info

            @param called_for VAT number to look up in service
            @param called_by VAT number of the user requesting information. It will
                just be logged in the remote servers as a legal requirement

            @return ??
        """
        from suds import null
        from suds.sudsobject import asdict

        def _reset(obj):
            """ Resets all attributes of a suds.Object to null values

                The default pythonic `None` value would cause them to be
                skipped, not sent.
            """
            for k in obj.__keylist__:
                obj[k] = null()

        qry = self._client.factory.create('RgWsPublicInputRtUser')
        r2 = self._client.factory.create('RgWsPublicBasicRtUser')
        #out1 = client.factory.create('RgWsPublicFirmActRtUserArray')
        err = self._client.factory.create('GenWsErrorRtUser')

        qry.afmCalledBy = compact(called_by)
        qry.afmCalledFor= compact(called_for)

        _reset(r2)
        _reset(err)

        ret = self._client.service.rgWsPublicAfmMethod(qry,r2,'',0, err)

        if ret.pErrorRec_out and ret.pErrorRec_out.errorCode:
            raise CheckException(ret.pErrorRec_out.errorCode, ret.pErrorRec_out.errorDescr)
        else:
            return asdict(ret)

#eof
