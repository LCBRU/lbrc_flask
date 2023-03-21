# -*- coding: utf-8 -*-

import pytest
import datetime
from lbrc_flask.data_conversions import (
    convert_dob,
    convert_nhs_number,
    convert_uhl_system_number,
    convert_gender,
    convert_name,
    convert_postcode,
    SEX_MALE,
    SEX_FEMALE,
)


@pytest.mark.parametrize(
    "value, is_error, expected",
    [
        (None, False, ''),
        ('', False, ''),
        (' ', False, ''),
        ('1111111111', False, '1111111111'),
        ('111 111 1111', False, '1111111111'),
        ('111-111-1111', False, '1111111111'),
        ('ABCDEFGHIJ', True, ''),
        ('1234321234', True, ''),
        ('111111111', True, ''),
        ('11111111111', True, ''),
    ],
)
def test__convert_nhs__parsing(client, value, is_error, expected):
    error, actual = convert_nhs_number(value)

    assert (error is None) != is_error
    assert actual == expected


@pytest.mark.parametrize(
    "value, is_error, expected",
    [
        (None, False, ''),
        ('', False, ''),
        (' ', False, ''),
        ('S1234567', False, 'S1234567'),
        ('S123456', True, ''),
        ('S12345678', True, ''),
        ('S123456A', True, ''),
        ('R1234567', False, 'R1234567'),
        ('R123456', True, ''),
        ('R12345678', True, ''),
        ('R123456A', True, ''),
        ('F1234567', False, 'F1234567'),
        ('F123456', True, ''),
        ('F12345678', True, ''),
        ('F123456A', True, ''),
        ('G1234567', False, 'G1234567'),
        ('G123456', True, ''),
        ('G12345678', True, ''),
        ('G123456A', True, ''),
        ('U1234567', False, 'U1234567'),
        ('U123456', True, ''),
        ('U12345678', False, 'U12345678'),
        ('U1234567A', False, 'U1234567A'),
        ('U123456A', True, ''),
        ('LB1234567', False, 'LB1234567'),
        ('LB123456', True, ''),
        ('LB12345678', True, ''),
        ('LB123456A', True, ''),
        ('RTD1234567', False, 'RTD1234567'),
        ('RTD123456', False, 'RTD123456'),
        ('RTD12345678', False, 'RTD12345678'),
        ('RTD1234-678', False, 'RTD1234-678'),
        ('RTD123456A', True, ''),
    ],
)
def test__convert_uhl_system_number(client, value, is_error, expected):
    error, actual = convert_uhl_system_number(value)

    assert (error is None) != is_error
    assert actual == expected


@pytest.mark.parametrize(
    "value, is_error, expected",
    [
        (None, False, ''),
        ('', False, ''),
        (' ', False, ''),
        ('f', False, SEX_FEMALE),
        ('female', False, SEX_FEMALE),
        ('femaled', True, ''),
        ('efemale', True, ''),
        ('male', False, SEX_MALE),
        ('m', False, SEX_MALE),
        ('emale', True, ''),
        ('maleness', True, ''),
        ('suttin else', True, ''),
    ],
)
def test__convert_gender(client, value, is_error, expected):
    error, actual = convert_gender(value)

    assert (error is None) != is_error
    assert actual == expected


@pytest.mark.parametrize(
    "value, is_error, expected",
    [
        (None, False, ''),
        ('', False, ''),
        (' ', False, ''),
        ('f', True, ''),
        ('fe', False, 'fe'),
        ('suttin else', False, 'suttin else'),
    ],
)
def test__convert_name(client, value, is_error, expected):
    error, actual = convert_name(value)

    assert (error is None) != is_error
    assert actual == expected


@pytest.mark.parametrize(
    "value, is_error, expected",
    [
        ('1944-12-19 00:00:00', False, '19441219'),
        ('1944-12-19', False, '19441219'),
        ('01/02/1923', False, '19230201'),
        ('31/01/1923', False, '19230131'),
        ('32/01/1923', True, ''),
        ('29/02/1996', False, '19960229'),
        ('12/06/1948', False, '19480612'),
        ('1948-06-12 00:00:00', False, '19480612'),
        ('1948-06-12T00:00:00', False, '19480612'),
        ('1948-06-12 00:00:00.0', False, '19480612'),
        ('1948-06-12T00:00:00.00000000', False, '19480612'),
        ('1997-07-16T19:20:30+01:00', False, '19970716'),
        ('1997-07-16T19:20:30-01:00', False, '19970716'),
        ('1997-07-16T19:20:30Z', False, '19970716'),
        ('29/02/1997', True, ''),
        ('29-02-1996', False, '19960229'),
        ('29 02 1996', False, '19960229'),
        ('29 Feb 1996', False, '19960229'),
        ('29 February 1996', False, '19960229'),
        (datetime.datetime(1996, 2, 29), False, '19960229'),
        ('19/12/1944', False, '19441219'),
        ('19440103', False, '19440103'),
        ('10000103', True, ''),
        (None, False, ''),
    ],
)
def test__convert_dob__parsing(client, value, is_error, expected):
    error, actual = convert_dob(value)

    assert (error is None) != is_error
    assert actual == expected


@pytest.mark.parametrize(
    "value, is_error, expected",
    [
        (None, False, ''),
        ('', False, ''),
        (' ', False, ''),
        ('SA63 4QJ', False, 'SA63 4QJ'),
        ('SA634QJ', False, 'SA63 4QJ'),
        ('WC1A 1AA', False, 'WC1A 1AA'),
        ('WC1A1AA', False, 'WC1A 1AA'),
        ('M1 1AA', False, 'M1 1AA'),
        ('M11AA', False, 'M1 1AA'),
        ('AB10 1JB', False, 'AB10 1JB'),
        ('ZE3 9JZ', False, 'ZE3 9JZ'),
        ('LE101 8HG', True, ''),
        ('10 8HG', True, ''),
        ('LE10 887HG', True, ''),
        ('LE10A 8HG', True, ''),
        ('LE10 8HG and something else', True, ''),
    ],
)
def test__convert_postcode(client, value, is_error, expected):
    error, actual = convert_postcode(value)

    assert (error is None) != is_error
    assert actual == expected
