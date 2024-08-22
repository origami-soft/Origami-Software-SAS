# -*- encoding: utf-8 -*-
##############################################################################
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

from odoo.exceptions import ValidationError


class PostPaymentNonDraftCheckError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class InvalidCheckCurrencyError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class CheckInOtherPaymentError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class NonNumericCheckError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class InvalidCheckAmountError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class InvalidCheckDatesError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class NotEqualCheckDatesError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class DeleteNonDraftCheckError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class PostReceiptNonDraftCheckError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class PostPaymentNonWalletCheckError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class PostPaymentNotToOrderCheckError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class CancelReceiptNonWalletCheckError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class CancelPaymentNonHandedCheckError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class InvalidCheckCancelStateError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class InvalidCheckNextStateError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class WrongChecksInOutboundPaymentError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class WrongChecksInInboundPaymentError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)


class InvalidSentRateError(ValidationError):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
