import pytest
import datetime
from dateutil.relativedelta import relativedelta
from lbrc_flask.validators import (
    is_invalid_nhs_number,
    standardise_nhs_number,
    calculate_nhs_number_checksum,
    is_invalid_uhl_system_number,
    parse_date,
    is_invalid_dob,
    standardise_postcode,
    is_invalid_postcode,
)


@pytest.mark.parametrize(
    "nhs_number, expected",
    [
        (None, ''),
        ('', ''),
        ('  ', ''),
        ('1111111111', '1111111111'),
        ('111 111 1111', '1111111111'),
        ('111-111-1111', '1111111111'),
    ],
)
def test__standardise_nhs_number(client, nhs_number, expected):
    assert standardise_nhs_number(nhs_number) == expected


@pytest.mark.parametrize(
    "pre_nhs_number, expected",
    [
        ('111111111', '1'),
        ('222222222', '2'),
        ('333333333', '3'),
        ('444444444', '4'),
        ('555555555', '5'),
        ('666666666', '6'),
        ('777777777', '7'),
        ('888888888', '8'),
        ('999999999', '9'),
    ],
)
def test__calculate_nhs_number_checksum(client, pre_nhs_number, expected):
    assert calculate_nhs_number_checksum(pre_nhs_number) == expected


@pytest.mark.parametrize(
    "nhs_number, expected",
    [
        (None, False),
        ('', False),
        ('1111111111', False),
        ('ABCDEFGHIJ', True),
        ('1234321234', True),
        ('111111111', True),
        ('11111111111', True),
    ],
)
def test__is_invalid_nhs_number(client, nhs_number, expected):
    assert is_invalid_nhs_number(nhs_number) == expected


@pytest.mark.parametrize(
    "s_number, expected",
    [
        (None, False),
        ('', False),
        ('S1234567', False),
        ('S123456', True),
        ('S12345678', True),
        ('S123456A', True),
        ('R1234567', False),
        ('R123456', True),
        ('R12345678', True),
        ('R123456A', True),
        ('F1234567', False),
        ('F123456', True),
        ('F12345678', True),
        ('F123456A', True),
        ('G1234567', False),
        ('G123456', True),
        ('G12345678', True),
        ('G123456A', True),
        ('U1234567', False),
        ('U123456', True),
        ('U12345678', False),
        ('U1234567A', False),
        ('U123456A', True),
        ('LB1234567', False),
        ('LB123456', True),
        ('LB12345678', True),
        ('LB123456A', True),
        ('RTD1234567', False),
        ('RTD123456', False),
        ('RTD12345678', False),
        ('RTD1234-678', False),
        ('RTD123456A', True),
    ],
)
def test__is_invalid_uhl_system_number(client, s_number, expected):
    assert is_invalid_uhl_system_number(s_number) == expected


@pytest.mark.parametrize(
    "value, is_error, expected",
    [
        ('1944-12-19 00:00:00', False, '19441219'),
        ('1944-12-19', False, '19441219'),
        ('01/02/1923', False, '19230201'),
        ('31/01/1923', False, '19230131'),
        ('32/01/1923', True, None),
        ('29/02/1996', False, '19960229'),
        ('12/06/1948', False, '19480612'),
        ('1948-06-12 00:00:00', False, '19480612'),
        ('1948-06-12T00:00:00', False, '19480612'),
        ('1948-06-12 00:00:00.0', False, '19480612'),
        ('1948-06-12T00:00:00.00000000', False, '19480612'),
        ('1997-07-16T19:20:30+01:00', False, '19970716'),
        ('1997-07-16T19:20:30-01:00', False, '19970716'),
        ('1997-07-16T19:20:30Z', False, '19970716'),
        ('29/02/1997', True, None),
        ('29-02-1996', False, '19960229'),
        ('29 02 1996', False, '19960229'),
        ('29 Feb 1996', False, '19960229'),
        ('29 February 1996', False, '19960229'),
        (datetime.datetime(1996, 2, 29), False, '19960229'),
        (datetime.date(1996, 2, 29), False, '19960229'),
        ('19/12/1944', False, '19441219'),
        ('19440103', False, '19440103'),    ],
)
def test__parse_date(client, value, is_error, expected):
    if is_error:
        with pytest.raises(ValueError):
            parse_date(value)
    else:
        assert parse_date(value).strftime("%Y%m%d") == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, False),
        ('', False),
        (datetime.datetime.now(datetime.UTC) - relativedelta(years=130), False),
        (datetime.datetime.now(datetime.UTC) - relativedelta(years=130, days=1), True),
        (datetime.datetime.now(datetime.UTC), False),
        (datetime.datetime.now(datetime.UTC) + relativedelta(days=1), True),
    ],
)
def test__is_invalid_dob(client, value, expected):
    assert is_invalid_dob(value) == expected


@pytest.mark.parametrize(
    "postcode, expected",
    [
        (None, False),
        ('', False),
        (' ', True),
        ('LE101 8HG', True),
        ('10 8HG', True),
        ('LE10 887HG', True),
        ('LE10A 8HG', True),
        ('LE10 8HG and something else', True),
        ('W1J 7NT', False), # - 149 Piccadilly, London. House of the Duke of Wellington
        ('DE12 8HJ', False), # - 17 Burton Road Coton in the Elms, Derbyshire. The Black Horse Pub, possibly the furthest pub from the sea in the UK.
        ('SW1A 1AA', False), # - Buckingham Palace
        ('HD7 5UZ', False), # - covers 7 streets; the most in the UK
        ('CH5 3QW', False), # - the longest addresses in terms of numbers of elements
        ('SA63 4QJ', False), # - the Post Town is CLARBESTON ROAD
        ('W2 1JB', False), # - When all the premises get expanded you'll get the longest 'premise string' in the UK
        ('PL7 1RF', False), # - Devon and Cornwall Police vs Devon and Cornwall Constabulary
        ('GIR 0AA', False), # - special case Postcode for Girobank at Bootle
        ('JE3 1EP', False), # - You will find that 'towns and large villages' are classed as Localities; Jersey; the Isle of Man and Guernsey are the Post Towns.
        ('IM9 4AJ', False), # - has no street
        ('WC1A 1AA', False),
        ('M1 1AA', False),
        ('AB10 1JB', False), # - First postcode
        ('ZE3 9JZ', False), # - Last postcode
    ],
)
def test__is_invalid_postcode(client, postcode, expected):
    assert is_invalid_postcode(postcode) == expected


@pytest.mark.parametrize(
    "postcode, expected",
    [
        (None, ''),
        ('', ''),
        (' ', ''),
        ('SA63 4QJ', 'SA63 4QJ'),
        ('SA634QJ', 'SA63 4QJ'),
        ('WC1A 1AA', 'WC1A 1AA'),
        ('WC1A1AA', 'WC1A 1AA'),
        ('M1 1AA', 'M1 1AA'),
        ('M11AA', 'M1 1AA'),
    ],
)
def test__standardise_postcode(client, postcode, expected):
    assert standardise_postcode(postcode) == expected
