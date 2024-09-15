# coding: utf-8

class PresentationTools:
    def __init__(self):
        pass

    @staticmethod
    def format_date(d):
        # type: (str) -> str
        """
        Formatea la fecha para su presentacion en ventas compras.
        :param d: La fecha a formatear.
        :type d: str
        :return: La fecha formateada.
        :rtype: str
        """
        if not isinstance(d, str):
            d = str(d)
        return d.replace("-", "")

    @staticmethod
    def format_amount(amount, dp=2):
        # type: (float, int) -> str
        """
        Formatea el numero con la cantidad de decimales que se le pase, o dos decimales por defecto.
        :param amount: El numero a formatear.
        :type amount: float
        :param dp: La precision decimal, a.k.a. la cantidad de decimales.
        :type dp: int
        :return: El numero formateado a string.
        :rtype: str
        """
        amount = str("{0:.{1}f}".format(amount, dp))
        amount = amount.replace(".", "").replace(",", "")
        return amount

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
