from lbrc_flask.column_data import CsvData, Excel97Data, ExcelData


def test__export__excel__matches(app, client, faker, tmp_path):
    p = tmp_path / 'test.xlsx'
    resp = client.get('/excel', follow_redirects=True)

    with open(p, 'wb') as f:
        f.write(resp.data)

    out = ExcelData(p)

    assert out.get_column_names() == ['fred', 'mary', 'ed']

    d = list(out.iter_rows())
    assert len(d) == 1

    for x in out.iter_rows():
        assert x['fred'] == 'soup'
        assert x['mary'] == 'fish'
        assert x['ed'] == '2000-01-02'


def test__export__csv__matches(app, client, faker, tmp_path):
    p = tmp_path / 'test.csv'
    resp = client.get('/csv', follow_redirects=True)

    with open(p, 'wb') as f:
        f.write(resp.data)

    out = CsvData(p)

    assert out.get_column_names() == ['fred', 'mary', 'ed']

    d = list(out.iter_rows())
    assert len(d) == 1

    for x in out.iter_rows():
        assert x['fred'] == 'soup'
        assert x['mary'] == 'fish'
        assert x['ed'] == '2000-01-02'


def test__export__pdf__matches(app, client, faker, tmp_path):
    p = tmp_path / 'test.pdf'
    resp = client.get('/pdf', follow_redirects=True)

    with open(p, 'wb') as f:
        f.write(resp.data)
