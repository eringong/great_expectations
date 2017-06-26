import json
import hashlib
import datetime
import numpy as np

from nose.tools import *
import great_expectations as ge

def test_expect_column_values_to_be_in_set():
    """
    Cases Tested:

    """

    D = ge.dataset.PandasDataSet({
        'x' : [1,2,4],
        'y' : [1,2,5],
        'z' : ['hello', 'jello', 'mello'],
    })

    tests = [
        {'input':('x', [1,2,4]), 'output':{'success':True, 'exception_list':[]}},
        {'input':('x', [4,2]), 'output':{'success':False, 'exception_list':[1]}},
        {'input':('y', []), 'output':{'success':False, 'exception_list':[1,2,5]}},
        {'input':('z', ['hello','jello','mello']), 'output': {'success':True, 'exception_list':[]}},
        {'input':('z', ['hello']), 'output': {'success':False, 'exception_list':['jello','mello']}}
    ]

    for t in tests:
        out = D.expect_column_values_to_be_in_set(*t['input'])
        assert out==t['output']
        # assert out['result']==t['output']['exception_list']
    #assert D.expect_column_values_to_be_in_set('x',[1,2,4])=={'success':True, [])
    #assert D.expect_column_values_to_be_in_set('x',[4,2])=={'success':False, [1])
    #assert D.expect_column_values_to_be_in_set('y',[])=={'success':False, [1,2,5])
    #assert D.expect_column_values_to_be_in_set('z',['hello', 'jello', 'mello'])=={'success':True, [])
    #assert D.expect_column_values_to_be_in_set('z',['hello'])=={'success':False, ['jello', 'mello'])

    #D2 = ge.dataset.PandasDataSet({
    #    'x' : [1,1,2,None],
    #    'y' : [None,None,None,None],
    #})

    #assert D2.expect_column_values_to_be_in_set('x',[1,2])=={'success':True, [])
    #assert D2.expect_column_values_to_be_in_set('x',[1])=={'success':False, [2])
    #assert D2.expect_column_values_to_be_in_set('x',[2])=={'success':False, [1, 1])
    #assert D2.expect_column_values_to_be_in_set('x',[2], suppress_exceptions=True)=={'success':False, 'exception_list':None)
    #assert D2.expect_column_values_to_be_in_set('x',[1], mostly=.66)=={'success':True, [2])
    #assert D2.expect_column_values_to_be_in_set('x',[1], mostly=.33)=={'success':True, [2])

    #assert D2.expect_column_values_to_be_in_set('x',[2], mostly=.66)
    #assert D2.expect_column_values_to_be_in_set('x',[2], mostly=.9)=={'success':False, [1,1])

    #assert D2.expect_column_values_to_be_in_set('y',[2])=={'success':True, [])
    #assert D2.expect_column_values_to_be_in_set('y',[])=={'success':True, [])
    #assert D2.expect_column_values_to_be_in_set('y',[2], mostly=.5)=={'success':True, [])
    #assert D2.expect_column_values_to_be_in_set('y',[], mostly=.5)=={'success':True, [])

    #print json.dumps(
    #    D2.ge_config,
    #    indent=2
    #)

    # assert 0

def test_expect_column_values_to_be_unique():
    """
    Cases Tested:
        Different data types are not equal
        Different values are not equal
        None and np.nan values trigger True
    """

    D = ge.dataset.PandasDataSet({
        'a' : ['2', '2'],
        'b' : [1, '2'],
        'c' : [1, 1],
        'd' : [1, '1'],
        'n' : [None, np.nan]
    })

    #Column string values are equal - 2 and 2
    assert D.expect_column_values_to_be_unique('a') == {'success':False, 'exception_list':['2']}
    #Column values are not equal - 1 and '2'
    assert D.expect_column_values_to_be_unique('b') == {'success':True, 'exception_list':[]}
    #Column int values are equal - 1 and '2'
    assert D.expect_column_values_to_be_unique('c') == {'success':False, 'exception_list':[1]}

    #!!! Different data types are never equal
    #Column int value and string value are equal - 1 and '1'
    assert D.expect_column_values_to_be_unique('d') == {'success':True, 'exception_list':[]}

    #np.nan and None pass
    assert D.expect_column_values_to_be_unique('n') == {'success':True, 'exception_list':[]}

    # Test suppress_exceptions
    assert D.expect_column_values_to_be_unique('n',suppress_exceptions = True) == {'success':True, 'exception_list':[]}
    assert D.expect_column_values_to_be_unique('a',suppress_exceptions = True) == {'success':False, 'exception_list':None}

    df = ge.dataset.PandasDataSet({
        'a' : ['2', '2', '2', '2'],
        'b' : [1, '2', '2', '3'],
        'n' : [None, None, np.nan, None],
    })

    #Column string values are equal - 2 and 2
    assert df.expect_column_values_to_be_unique('a') == {'success':False, 'exception_list':['2','2','2']}

    # Test mostly
    # !!! Really important to remember that this is mostly for NOT-NULL values.
    # !!! Tricky because you have to keep that in your mind if your column has many nulls
    assert df.expect_column_values_to_be_unique('b', mostly=.25)=={'success':True, 'exception_list':['2']}
    assert df.expect_column_values_to_be_unique('b', mostly=.75)=={'success':False, 'exception_list':['2']}
    assert df.expect_column_values_to_be_unique('a', mostly=1)=={'success':False, 'exception_list':['2','2','2']}
    assert df.expect_column_values_to_be_unique('n', mostly=.2)=={'success':True, 'exception_list':[]}

    # Test suppress_exceptions once more
    assert df.expect_column_values_to_be_unique('a',suppress_exceptions = True) == {'success':False, 'exception_list':None}


def test_expect_column_values_to_not_be_null():
    """
    Cases Tested:
        F: Column with one None value and other non None value
        F: Column with one np.nan value and other non np.nan value
        F: Column with one np.nan value and None value
        T: Column with non None or np.nan
    """

    D = ge.dataset.PandasDataSet({
        'x' : [2, None],
        'y' : [2, np.nan],
        'n' : [None, np.nan],
        'z' : [2, 5],
    })

    D2 = ge.dataset.PandasDataSet({
        'a' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'b' : [1, 2, 3, 4, 5, 6, 7, 8, 9, None],
    })

    assert_equal(
        D.expect_column_values_to_not_be_null('x'),
        {'success':False, 'exception_list':[None]}
    )
    assert D.expect_column_values_to_not_be_null('y')=={'success':False, 'exception_list':[None]}
    assert D.expect_column_values_to_not_be_null('n')=={'success':False, 'exception_list':[None, None]}
    assert D.expect_column_values_to_not_be_null('z')=={'success':True, 'exception_list':[]}

    assert D.expect_column_values_to_not_be_null('x', suppress_exceptions=True)=={'success':False, 'exception_list':None}
    assert D.expect_column_values_to_not_be_null('n', suppress_exceptions=True)=={'success':False, 'exception_list':None}
    assert D.expect_column_values_to_not_be_null('z', suppress_exceptions=True)=={'success':True, 'exception_list':None}

    assert D2.expect_column_values_to_not_be_null('a')=={'success':True, 'exception_list':[]}
    assert D2.expect_column_values_to_not_be_null('a', mostly=.90)=={'success':True, 'exception_list':[]}
    assert D2.expect_column_values_to_not_be_null('b')=={'success':False, 'exception_list':[None]}
    assert D2.expect_column_values_to_not_be_null('b', mostly=.95)=={'success':False, 'exception_list':[None]}
    assert D2.expect_column_values_to_not_be_null('b', mostly=.90)=={'success':True, 'exception_list':[None]}

    assert D2.expect_column_values_to_not_be_null('b', suppress_exceptions=True)=={'success':False, 'exception_list':None}
    assert D2.expect_column_values_to_not_be_null('b', mostly=.95, suppress_exceptions=True)=={'success':False, 'exception_list':None}
    assert D2.expect_column_values_to_not_be_null('b', mostly=.90, suppress_exceptions=True)=={'success':True, 'exception_list':None}



def test_expect_column_values_to_be_null():
    """
    !!! All values must be either None and np.nan to be True
    Cases Tested:
        F: Column with one None value and other non None value
        F: Column with one np.nan value and other non np.nan value
        F: Column with one np.nan value and None value
        T: Column with non None or np.nan values
    """

    D = ge.dataset.PandasDataSet({
        'x' : [2, None, 2],
        'y' : [2, np.nan, 2],
        'z' : [2, 5, 7],
        'a' : [None, np.nan, None],
    })

    # Test on np.an and None
    # Test exceptions (not_null values) show up properly
    assert D.expect_column_values_to_be_null('x')=={'success':False, 'exception_list':[2,2]}
    assert D.expect_column_values_to_be_null('y')=={'success':False, 'exception_list':[2,2]}
    assert D.expect_column_values_to_be_null('z')=={'success':False, 'exception_list':[2,5,7]}
    assert D.expect_column_values_to_be_null('a')=={'success':True, 'exception_list':[]}

    # Test suppress_exceptions
    assert D.expect_column_values_to_be_null('x', suppress_exceptions = True)=={'success':False, 'exception_list':None}

    # Test mostly
    assert D.expect_column_values_to_be_null('x', mostly = .2, suppress_exceptions = True)=={'success':True, 'exception_list':None}
    assert D.expect_column_values_to_be_null('x', mostly = .8, suppress_exceptions = True)=={'success':False, 'exception_list':None}

    assert D.expect_column_values_to_be_null('a', mostly = .5, suppress_exceptions = True)=={'success':True, 'exception_list':None}


def test_expect_column_mean_to_be_between():
    """
    #!!! Ignores null (None and np.nan) values. If all null values, return {'success':False, 'exception_list':None)
    Cases Tested:
        Tested with float - float
        Tested with float - int
        Tested with np.nap
    """

    D = ge.dataset.PandasDataSet({
        'x' : [2.0, 5.0],
        'y' : [5.0, 5],
        'z' : [0, 10],
        'n' : [0, None],
        's' : ['s', np.nan],
        'b' : [True, False],
    })

    #[2, 5]
    assert D.expect_column_mean_to_be_between('x', 2, 5)=={'success':True, 'true_mean':3.5}
    assert D.expect_column_mean_to_be_between('x', 1, 2)=={'success':False, 'true_mean':3.5}

    #[5, 5]
    assert D.expect_column_mean_to_be_between('y', 5, 5)=={'success':True, 'true_mean':5}
    assert D.expect_column_mean_to_be_between('y', 4, 4)=={'success':False, 'true_mean':5}

    #[0, 10]
    assert D.expect_column_mean_to_be_between('z', 5, 5)=={'success':True, 'true_mean':5}
    assert D.expect_column_mean_to_be_between('z', 13, 14)=={'success':False, 'true_mean':5}

    #[0, np.nan]
    assert D.expect_column_mean_to_be_between('n', 0, 0)=={'success':True, 'true_mean':0.0}

    typedf = ge.dataset.PandasDataSet({
        's' : ['s', np.nan, None, None],
        'b' : [True, False, False, True],
        'x' : [True, None, False, None],
    })

    # Check TypeError
    assert typedf.expect_column_mean_to_be_between('s', 0, 0)=={'success':False, 'true_mean':None}
    assert typedf.expect_column_mean_to_be_between('b', 0, 1)=={'success':True, 'true_mean':0.5}
    assert typedf.expect_column_mean_to_be_between('x', 0, 1)=={'success':True, 'true_mean':0.5}


def test_expect_column_values_to_match_regex():
    """
    Cases Tested:
        Tested mostly alphabet regex
    """

    D = ge.dataset.PandasDataSet({
        'x' : ['aa', 'ab', 'ac', 'a1', None],
        'y' : ['aa', 'ab', 'ac', 'ba', 'ca'],
    })


    D2 = ge.dataset.PandasDataSet({
        'a' : ['aaa', 'abb', 'acc', 'add', 'bee'],
        'b' : ['aaa', 'abb', 'acc', 'bdd', None],
        'c' : [ None,  None,  None,  None, None],
    })


    #!!! Why do these tests have verbose=True?
    #['aa', 'ab', 'ac', 'a1', None]
    assert D.expect_column_values_to_match_regex('x', '^a')=={'success':True, 'exception_list':[]}
    assert D.expect_column_values_to_match_regex('x', 'aa', verbose=True)=={'success':False, 'exception_list':['ab', 'ac', 'a1']}
    assert D.expect_column_values_to_match_regex('x', 'a[a-z]', verbose=True)=={'success':False, 'exception_list':['a1']}

    #['aa', 'ab', 'ac', 'ba', 'ca']
    assert D.expect_column_values_to_match_regex('y', '[abc]{2}', verbose=True)=={'success':True, 'exception_list':[]}
    assert D.expect_column_values_to_match_regex('y', '[z]', verbose=True)=={'success':False, 'exception_list':['aa', 'ab', 'ac', 'ba', 'ca']}


    assert D.expect_column_values_to_match_regex('y', '[abc]{2}', suppress_exceptions=True) == {'success':True, 'exception_list':None}
    assert D.expect_column_values_to_match_regex('y', '[z]', suppress_exceptions=True) == {'success':False, 'exception_list':None}

    assert D2.expect_column_values_to_match_regex('a', '^a', mostly=.9) == {'success':False, 'exception_list':['bee']}
    assert D2.expect_column_values_to_match_regex('a', '^a', mostly=.8) == {'success':True, 'exception_list':['bee']}
    assert D2.expect_column_values_to_match_regex('a', '^a', mostly=.7) == {'success':True, 'exception_list':['bee']}

    assert D2.expect_column_values_to_match_regex('b', '^a', mostly=.9) == {'success':False, 'exception_list':['bdd']}
    assert D2.expect_column_values_to_match_regex('b', '^a', mostly=.75) == {'success':True, 'exception_list':['bdd']}
    assert D2.expect_column_values_to_match_regex('b', '^a', mostly=.5) == {'success':True, 'exception_list':['bdd']}

    assert D2.expect_column_values_to_match_regex('b', '^a', mostly=.9, suppress_exceptions=True) == {'success':False, 'exception_list':None}
    assert D2.expect_column_values_to_match_regex('b', '^a', mostly=.75, suppress_exceptions=True) == {'success':True, 'exception_list':None}
    assert D2.expect_column_values_to_match_regex('b', '^a', mostly=.5, suppress_exceptions=True) == {'success':True, 'exception_list':None}

    #Testing for all-null columns
    assert D2.expect_column_values_to_match_regex('c', '^a') == {'success':True, 'exception_list':[]}
    assert D2.expect_column_values_to_match_regex('c', '^a', mostly=.5) == {'success':True, 'exception_list':[]}
    assert D2.expect_column_values_to_match_regex('c', '^a', suppress_exceptions=True) == {'success':True, 'exception_list':[]}
    assert D2.expect_column_values_to_match_regex('c', '^a', mostly=.5, suppress_exceptions=True) == {'success':True, 'exception_list':[]}

def test_expect_column_values_match_strftime_format():
    """
    Cases Tested:


    !!! TODO: Add tests for input types and raised exceptions

    """

    D = ge.dataset.PandasDataSet({
        'x' : [1,2,4],
        'us_dates' : ['4/30/2017','4/30/2017','7/4/1776'],
        'us_dates_type_error' : ['4/30/2017','4/30/2017', 5],
        'almost_iso8601' : ['1977-05-25T00:00:00', '1980-05-21T13:47:59', '2017-06-12T23:57:59'],
        'almost_iso8601_val_error' : ['1977-05-55T00:00:00', '1980-05-21T13:47:59', '2017-06-12T23:57:59']
    })

    tests = [
            {'input':('us_dates','%m/%d/%Y'), 'kwargs':{'mostly': None}, 'success':True, 'exception_list':[]},
            {'input':('us_dates_type_error','%m/%d/%Y'), 'kwargs':{'mostly': 0.5}, 'success':True, 'exception_list':[5]},
            {'input':('us_dates_type_error','%m/%d/%Y'), 'kwargs':{'mostly': None}, 'success':False,'exception_list':[5]},
            {'input':('almost_iso8601','%Y-%m-%dT%H:%M:%S'), 'kwargs':{'mostly': None}, 'success':True,'exception_list':[]},
            {'input':('almost_iso8601_val_error','%Y-%m-%dT%H:%M:%S'), 'kwargs':{'mostly': None}, 'success':False,'exception_list':['1977-05-55T00:00:00']}
            ]

    for t in tests:
        out = D.expect_column_values_to_match_strftime_format(*t['input'],**t['kwargs'])
        assert out['success'] == t['success']
        assert out['exception_list'] == t['exception_list']



def test_expect_column_values_to_not_match_regex():
    #!!! Need to test mostly and suppress_exceptions

    D = ge.dataset.PandasDataSet({
        'x' : ['aa', 'ab', 'ac', 'a1', None, None, None],
        'y' : ['axxx', 'exxxx', 'ixxxx', 'oxxxxx', 'uxxxxx', 'yxxxxx', 'zxxxx'],
        'z' : [None, None, None, None, None, None, None]
    })

    assert D.expect_column_values_to_not_match_regex('x', '^a') == {'success':False, 'exception_list':['aa', 'ab', 'ac', 'a1']}
    assert D.expect_column_values_to_not_match_regex('x', '^b') == {'success':True, 'exception_list':[]}

    assert D.expect_column_values_to_not_match_regex('y', '^z') == {'success':False, 'exception_list':['zxxxx']}
    assert D.expect_column_values_to_not_match_regex('y', '^z', mostly=.5) == {'success':True, 'exception_list':['zxxxx']}

    assert D.expect_column_values_to_not_match_regex('x', '^a', suppress_exceptions=True) == {'success':False, 'exception_list':None}
    assert D.expect_column_values_to_not_match_regex('x', '^b', suppress_exceptions=True) == {'success':True, 'exception_list':None}
    assert D.expect_column_values_to_not_match_regex('y', '^z', suppress_exceptions=True) == {'success':False, 'exception_list':None}
    assert D.expect_column_values_to_not_match_regex('y', '^z', mostly=.5, suppress_exceptions=True) == {'success':True, 'exception_list':None}

    assert D.expect_column_values_to_match_regex('z', '^a') == {'success':True, 'exception_list':[]}
    assert D.expect_column_values_to_match_regex('z', '^a', mostly=.5) == {'success':True, 'exception_list':[]}
    assert D.expect_column_values_to_match_regex('z', '^a', suppress_exceptions=True) == {'success':True, 'exception_list':[]}
    assert D.expect_column_values_to_match_regex('z', '^a', mostly=.5, suppress_exceptions=True) == {'success':True, 'exception_list':[]}


def test_expect_column_values_to_be_between():
    """

    """

    D = ge.dataset.PandasDataSet({
        'x' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'y' : [1, 2, 3, 4, 5, 6, 7, 8, 9, "abc"],
        'z' : [1, 2, 3, 4, 5, None, None, None, None, None],
    })

    assert_equal(
        D.expect_column_values_to_be_between('x', 1, 10),
        {'success':True, 'exception_list':[]}
    )
    assert D.expect_column_values_to_be_between('x', 0, 20) == {'success':True, 'exception_list':[]}
    assert D.expect_column_values_to_be_between('x', 1, 9) == {'success':False, 'exception_list':[10]}
    assert D.expect_column_values_to_be_between('x', 3, 10) == {'success':False, 'exception_list':[1, 2]}

    assert D.expect_column_values_to_be_between('x', 1, 10, suppress_exceptions=True) == {'success':True, 'exception_list':None}
    assert D.expect_column_values_to_be_between('x', 0, 20, suppress_exceptions=True) == {'success':True, 'exception_list':None}
    assert D.expect_column_values_to_be_between('x', 1, 9, suppress_exceptions=True) == {'success':False, 'exception_list':None}
    assert D.expect_column_values_to_be_between('x', 3, 10, suppress_exceptions=True) == {'success':False, 'exception_list':None}

    assert D.expect_column_values_to_be_between('x', 1, 10, mostly=.9) == {'success':True, 'exception_list':[]}
    assert D.expect_column_values_to_be_between('x', 0, 20, mostly=.9) == {'success':True, 'exception_list':[]}
    assert D.expect_column_values_to_be_between('x', 1, 9, mostly=.9) == {'success':True, 'exception_list':[10]}
    assert D.expect_column_values_to_be_between('x', 3, 10, mostly=.9) == {'success':False, 'exception_list':[1, 2]}

    assert D.expect_column_values_to_be_between('y', 1, 10, mostly=.95) == {'success':False, 'exception_list':["abc"]}
    assert D.expect_column_values_to_be_between('y', 1, 10, mostly=.9) == {'success':True, 'exception_list':["abc"]}
    assert D.expect_column_values_to_be_between('y', 1, 10, mostly=.8) == {'success':True, 'exception_list':["abc"]}

    assert D.expect_column_values_to_be_between('z', 1, 4, mostly=.9) == {'success':False, 'exception_list':[5]}
    assert D.expect_column_values_to_be_between('z', 1, 4, mostly=.8) == {'success':True, 'exception_list':[5]}



def test_expect_column_values_to_not_be_in_set():
    """
    Cases Tested:
    -Repeat values being returned
    -Running expectations only on nonmissing values
    """

    D = ge.dataset.PandasDataSet({
        'x' : [1,2,4],
        'y' : [1,2,5],
        'z' : ['hello', 'jello', 'mello'],
        'a' : [1,1,2],
        'n' : [None,None,2],
    })

    assert D.expect_column_values_to_not_be_in_set('x',[1,2])=={'success':False, 'exception_list':[1,2]}
    assert D.expect_column_values_to_not_be_in_set('x',[5,6])=={'success':True, 'exception_list':[]}
    assert D.expect_column_values_to_not_be_in_set('z',['hello', 'jello'])=={'success':False, 'exception_list':['hello', 'jello']}
    assert D.expect_column_values_to_not_be_in_set('z',[])=={'success':True, 'exception_list':[]}

    # Test if False exceptions list returns repeat values
    # assert D.expect_column_values_to_not_be_in_set('a', [1]) == {'success':False, [1]}
    assert D.expect_column_values_to_not_be_in_set('a', [1]) == {'success':False, 'exception_list':[1, 1]}

    # Test nonmissing values support
    assert D.expect_column_values_to_not_be_in_set('n', [2]) == {'success':False, 'exception_list':[2]}
    assert D.expect_column_values_to_not_be_in_set('n', []) == {'success':True, 'exception_list':[]}

    # Test suppress_exceptions
    assert D.expect_column_values_to_not_be_in_set('n', [2], suppress_exceptions=True) == {'success':False, 'exception_list':None}

    # Test mostly
    assert D.expect_column_values_to_not_be_in_set('a', [1], mostly=.2, suppress_exceptions=True) == {'success':True, 'exception_list':None}
    assert D.expect_column_values_to_not_be_in_set('n', [2], mostly=1) == {'success':False, 'exception_list':[2]}



#def test_expect_column_values_to_be_of_type():
#    """
#    Cases Tested:
#
#    """
#
#    D = ge.dataset.PandasDataSet({
#        'x' : [1,2,4],
#        'y' : [1.0,2.2,5.3],
#        'z' : ['hello', 'jello', 'mello'],
#        'n' : [None, np.nan, None],
#        'b' : [False, True, False],
#        's' : ['hello', 'jello', 1],
#        's1' : ['hello', 2.0, 1],
#    })
#
#    assert D.expect_column_values_to_be_of_type('x','double precision')=={'success':True, [])
#    assert D.expect_column_values_to_be_of_type('x','text')=={'success':False, [1,2,4])
#    assert D.expect_column_values_to_be_of_type('y','double precision')=={'success':True, [])
#    assert D.expect_column_values_to_be_of_type('y','boolean')=={'success':False, [1.0,2.2,5.3])
#    assert D.expect_column_values_to_be_of_type('z','text')=={'success':True, [])
#    assert D.expect_column_values_to_be_of_type('b','boolean')=={'success':True, [])
#    assert D.expect_column_values_to_be_of_type('b','boolean')=={'success':True, [])
#    assert D.expect_column_values_to_be_of_type('n','boolean')=={'success':True, [])
#    assert D.expect_column_values_to_be_of_type('n','text')=={'success':True, [])
#    assert D.expect_column_values_to_be_of_type('n','double precision')=={'success':True, [])
#    assert D.expect_column_values_to_be_of_type('n','double precision')=={'success':True, [])
#
#    assert D.expect_column_values_to_be_of_type('x','crazy type you\'ve never heard of')=={'success':True, [])
#    # Test suppress_exceptions and mostly
#    assert D.expect_column_values_to_be_of_type('s','text', suppress_exceptions=True, mostly=.4)=={'success':True, 'exception_list':None)
#    assert D.expect_column_values_to_be_of_type('s','text', suppress_exceptions=False, mostly=.4)=={'success':True, [1])
#    assert D.expect_column_values_to_be_of_type('s1','text', suppress_exceptions=False, mostly=.2)=={'success':True, [2.0 ,1])
#    assert D.expect_column_values_to_be_of_type('s1','double precision', suppress_exceptions=False, mostly=.2)=={'success':True, ['hello'])




def test_expect_table_row_count_to_be_between():
    D = ge.dataset.PandasDataSet({'c1':[4,5,6,7],'c2':['a','b','c','d'],'c3':[None,None,None,None]})

    out1 = D.expect_table_row_count_to_be_between(3,5)
    assert out1['success']==True
    assert out1['true_row_count']==4


def test_expect_table_row_count_to_equal():
    D = ge.dataset.PandasDataSet({'c1':[4,5,6,7],'c2':['a','b','c','d'],'c3':[None,None,None,None]})

    out1 = D.expect_table_row_count_to_equal(4)
    assert out1['success']==True
    assert out1['true_row_count']==4


def test_expect_column_value_lengths_to_be_between():
    s1 = ['smart','silly','sassy','slimy','sexy']
    s2 = ['cool','calm','collected','casual','creepy']
    D = ge.dataset.PandasDataSet({'s1':s1,'s2':s2})
    out1 = D.expect_column_value_lengths_to_be_between('s1', min_value=3, max_value=5)
    out2 = D.expect_column_value_lengths_to_be_between('s2', min_value=4, max_value=6)
    out3 = D.expect_column_value_lengths_to_be_between('s2', min_value=None, max_value=10)
    assert_equal( out1['success'], True)
    assert_equal( out2['success'], False)
    assert_equal( len(out2['exception_list']), 1)
    assert_equal( out3['success'], True)



def test_expect_column_values_to_match_regex_list():
    pass


def test_expect_column_values_to_be_dateutil_parseable():
    dates = ['03/06/09','23 April 1973','January 9, 2016']
    other = ['197234567','covfefe',25]
    D = ge.dataset.PandasDataSet({'dates':dates, 'other':other})
    out = D.expect_column_values_to_be_dateutil_parseable('dates')
    out2 = D.expect_column_values_to_be_dateutil_parseable('other')
    assert out['success'] == True
    assert len(out['exception_list']) == 0
    assert out2['success'] == False
    assert len(out2['exception_list']) == 3


def test_expect_column_values_to_be_valid_json():
    d1 = json.dumps({'i':[1,2,3],'j':35,'k':{'x':'five','y':5,'z':'101'}})
    d2 = json.dumps({'i':1,'j':2,'k':[3,4,5]})
    D = ge.dataset.PandasDataSet({'json_col':[d1,d2]})
    out = D.expect_column_values_to_be_valid_json('json_col')
    assert out['success'] == True


def test_expect_column_stdev_to_be_between():
    D = ge.dataset.PandasDataSet({'randn':np.random.randn(100)})
    out1 = D.expect_column_stdev_to_be_between('randn',.5,1.5)
    out2 = D.expect_column_stdev_to_be_between('randn',2,3)
    assert out1['success'] == True
    assert out2['success'] == False


def test_expect_two_column_values_to_be_subsets():
    A = [0,1,2,3,4,3,2,1,0]
    B = [2,3,4,5,6,5,4,3,2]
    C = [0,1,2,3,4,5,6,7,8]
    D = ge.dataset.PandasDataSet({'A':A,'B':B,'C':C})
    out1 = D.expect_two_column_values_to_be_subsets('A','C')
    out2 = D.expect_two_column_values_to_be_subsets('A','B',mostly=.5)

    assert out1['success'] == True
    assert out2['success'] == True
    assert out2['not_in_subset'] == set([0,1,5,6])


def test_expect_two_column_values_to_be_many_to_one():
    pass



#!!! Deprecated
# def test_expect_column_values_to_be_equal_across_columns():
#     """
#     Cases Tested:
#         Column values in x and y are equal
#         Column values in x and z are not equal
#         Column values in a and z are not equal
#     """

#     D = ge.dataset.PandasDataSet({
#         'x' : [2, 5, 8],
#         'y' : [2, 5, 8],
#         'z' : [2, 5, 6],
#         'a' : [1, 2, 3],
#     })

#     #Test True case for col x==y
#     assert D.expect_column_values_to_be_equal_across_columns('x', 'y', suppress_exceptions=True)=={'success':True,'exception_list':None}
#     #Test one value False case for col x==z
#     assert D.expect_column_values_to_be_equal_across_columns('x', 'z', suppress_exceptions=True)=={'success':False,'exception_list':None}
#     #Test True
#     assert D.expect_column_values_to_be_equal_across_columns('a', 'z', suppress_exceptions=True)=={'success':False,'exception_list':None}


### DEPRECATED: see test_expect_column_value_lengths_to_be_between
#def test_expect_column_value_lengths_to_be_less_than_or_equal_to():
#    """
#    Cases Tested:
#
#    """
#
#    D = ge.dataset.PandasDataSet({
#        'x' : [1,2,4],
#        'y' : ['three','four','five'],
#        'n' : [None,np.nan,None],
#    })
#
#    assert D.expect_column_value_lengths_to_be_less_than_or_equal_to('x',6)=={'success':True, [])
#    assert D.expect_column_value_lengths_to_be_less_than_or_equal_to('y',2)=={'success':False, ['three','four','five'])
#    assert D.expect_column_value_lengths_to_be_less_than_or_equal_to('y',6)=={'success':True, [])
#    assert D.expect_column_value_lengths_to_be_less_than_or_equal_to('n',0)=={'success':True, [])


