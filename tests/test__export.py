from lbrc_flask.column_data import CsvData, Excel97Data, ExcelData

def test__export__excel__matches(app, client, faker, tmp_path):
    p = tmp_path / 'test.xlsx'
    resp = client.get('/excel', follow_redirects=True)

    with open(p, 'wb') as f:
        f.write(resp.data)

    out = ExcelData(p)

    assert out.get_column_names() == ['Fred', 'Mary', 'Ed']

    d = list(out.iter_rows())
    assert len(d) == 1

    for x in out.iter_rows():
        assert x['Fred'] == 'soup'
        assert x['Mary'] == 'fish'
        assert x['Ed'] == '2000-01-02'
