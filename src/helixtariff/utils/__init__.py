from decimal import Decimal

def format_price(p):
    '''
    >>> format_price('5.01')
    '5.01'
    >>> format_price('11.1')
    '11.1'
    >>> format_price('11.12')
    '11.12'
    >>> format_price('11.00')
    '11'
    >>> format_price('111')
    '111'
    '''
    dec = Decimal(p)
    base = dec.quantize(Decimal("1"))
    res = dec if dec - base else base
    return '%s' % res
