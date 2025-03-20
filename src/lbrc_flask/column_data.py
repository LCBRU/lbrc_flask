from dataclasses import dataclass
from typing import Optional
import chardet
import csv
import xlrd
from openpyxl import load_workbook
from itertools import takewhile, zip_longest, compress, islice
from pathlib import Path
from functools import cached_property
from lbrc_flask.validators import is_integer, parse_date_or_none


class ColumnData():
    def __init__(self, filepath):
        self.filepath = filepath


class ExcelData(ColumnData):

    def get_column_names(self):
        wb = load_workbook(filename=self.filepath, read_only=True)
        ws = wb.active
        rows = ws.iter_rows(min_row=1, max_row=1)
        first_row = next(rows)

        return [c.value for c in takewhile(lambda x: x.value, first_row)]

    def iter_rows(self):
        wb = load_workbook(filename=self.filepath, read_only=True)
        ws = wb.active

        column_names = self.get_column_names()
        for r in ws.iter_rows(min_row=2, values_only=True):
            yield dict(zip(column_names, r))


class Excel97Data(ColumnData):

    def get_column_names(self):
        wb = xlrd.open_workbook(filename=self.filepath)
        ws = wb.sheet_by_index(0)
        first_row = ws.row(0)

        return [c.value for c in takewhile(lambda x: x.value, first_row)]

    def iter_rows(self):
        wb = xlrd.open_workbook(filename=self.filepath, formatting_info=True)
        ws = wb.sheet_by_index(0)

        column_names = self.get_column_names()
        rows = ws.get_rows()
        next(rows)
        for r in rows:
            yield dict(zip(column_names, [self._value_from_cell(c, wb.datemode) for c in r]))

    def _value_from_cell(self, cell, datemode):
        if cell.ctype == xlrd.book.XL_CELL_DATE:
            return xlrd.xldate.xldate_as_datetime(cell.value, datemode)
        else:
            return cell.value


class CsvData(ColumnData):

    def get_column_names(self):
        result = []

        with open(self.filepath, 'r', encoding=self._get_encoding()) as f:
            d_reader = csv.DictReader(f)

            result = d_reader.fieldnames

            for row in d_reader:
                for i in range(len(result), len(row)):
                    result.append(f'Column {i}')

        return result 

    def _get_encoding(self):
        rawdata = open(self.filepath, 'rb').read()
        result = chardet.detect(rawdata)
        return result['encoding']

    def iter_rows(self):
        column_names = self.get_column_names()

        with open(self.filepath, 'r', encoding=self._get_encoding()) as f:
            reader = csv.reader(f)

            for row in islice(reader, 1, None):
                yield dict(zip_longest(column_names, row, fillvalue=''))


class ColumnsDefinition():
    @property
    def column_definition(self):
        return []
    
    @property
    def column_names(self):
        return [d.name for d in self.column_definition]

    def definition_for_column_name(self, name):
        for d in self.column_definition:
            if d.name == name:
                return d


@dataclass
class ColumnDefinition:
    COLUMN_TYPE_STRING = 'str'
    COLUMN_TYPE_INTEGER = 'int'
    COLUMN_TYPE_DATE = 'date'

    name: str
    type: str
    allow_null: bool = False
    max_length: Optional[int] = None
    translated_name: Optional[str] = None

    def value(self, row: dict):
        return row.get(self.name, None)

    def stringed_value(self, row: dict):
        return str(self.value(row) or '').strip()

    def has_value(self, row: dict):
        return len(self.stringed_value(row)) > 0

    def get_translated_name(self):
        return self.translated_name or self.name


class Spreadsheet():
    def __init__(self, filepath: Path, header_rows: int = 1):
        self.filepath: Path = filepath
        self.header_rows: int = header_rows

    def worksheet(self):
        wb = load_workbook(filename=self.filepath, read_only=True)
        return wb.active

    @cached_property
    def column_names(self):
        rows = self.worksheet().values
        first_row = next(rows)

        result = [c.lower() for c in takewhile(lambda x: x, first_row)]

        return result

    def iter_rows(self):
        for r in self.worksheet().values:
            yield dict(zip(self.column_names, r))

    def iter_data(self):
        for r in islice(self.iter_rows(), self.header_rows, None):
            yield r


class SpreadsheetDefinition:
    def __init__(self, spreadsheet: Spreadsheet, column_definition: ColumnsDefinition):
        self.spreadsheet: Spreadsheet = spreadsheet
        self.column_definition: ColumnsDefinition = column_definition
    
    def validation_errors(self):
        errors = []

        errors.extend(self.column_validation_errors())
        errors.extend(self.data_validation_errors())

        return errors

    def column_validation_errors(self):
        missing_columns = set(self.column_definition.column_names) - set(self.spreadsheet.column_names)
        return map(lambda x: f"Missing column '{x}'", missing_columns)

    def iter_filtered_data(self):
        return compress(self.spreadsheet.iter_data(), self.rows_with_all_fields)
    
    def translated_data(self):
        for row in self.iter_filtered_data():
            result = {}

            for cd in self.column_definition.column_definition:
                result[cd.get_translated_name()] = cd.value(row)
            
            yield result

    def data_validation_errors(self):
        result = []

        for i, row in enumerate(self.iter_filtered_data(), 1):
            row_errors = self._field_errors_for_def(row)
            result.extend(map(lambda e: f"Row {i}: {e}", row_errors))

        return result
    
    @cached_property
    def rows_with_all_fields(self):
        result = []

        for row in self.spreadsheet.iter_data():
            result.append(all([d.has_value(row) or d.allow_null for d in self.column_definition.column_definition]))

        return result

    @cached_property
    def rows_with_any_fields(self):
        result = []

        for row in self.spreadsheet.iter_data():
            result.append(any([d.has_value(row) for d in self.column_definition.column_definition]))

        return result

    def _field_errors_for_def(self, row: dict):
        result = []
        for col_def in self.column_definition.column_definition:
            if col_def.name in row:
                result.extend(self._field_errors(row, col_def))
        
        return result
    
    def _field_errors(self, row, col_def):
        result = []

        value = row[col_def.name]

        if not col_def.allow_null:
            is_null = value is None or str(value).strip() == ''
            if is_null:
                result.append("Data is mising")

        match col_def.type:
            case ColumnDefinition.COLUMN_TYPE_STRING:
                result.extend(self._is_invalid_string(value, col_def))
            case ColumnDefinition.COLUMN_TYPE_INTEGER:
                result.extend(self._is_invalid_interger(value, col_def))
            case ColumnDefinition.COLUMN_TYPE_DATE:
                result.extend(self._is_invalid_date(value, col_def))
        
        return map(lambda e: f"{col_def.name}: {e}", result)

    def _is_invalid_string(self, value, col_def):
        if value is None:
            return []

        if max_length := col_def.max_length:
            if len(value) > max_length:
               return [f"Text is longer than {max_length} characters"]

        return []

    def _is_invalid_interger(self, value, col_def):
        if value is None:
            return []

        if not is_integer(value):
            return ["Invalid value"]
        
        return []

    def _is_invalid_date(self, value, col_def):
        if value is None:
            return []

        if parse_date_or_none(value) is None:
            return ["Invalid value"]
        
        return []
