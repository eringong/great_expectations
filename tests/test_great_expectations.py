import json
import hashlib
import datetime
import numpy as np
import random
import os
import sys
import inspect

from nose.tools import *
import great_expectations as ge

def test_custom_class_1():
    #https://stackoverflow.com/questions/18833759/python-prime-number-checker
    def isprime(n):
        '''check if integer n is a prime'''

        # make sure n is a positive integer
        n = abs(int(n))

        # 0 and 1 are not primes
        if n < 2:
            return False

        # 2 is the only even prime number
        if n == 2: 
            return True    

        # all other even numbers are not primes
        if not n & 1: 
            return False

        # range starts with 3 and only needs to go up 
        # the square root of n for all odd numbers
        for x in range(3, int(n**0.5) + 1, 2):
            if n % x == 0:
                return False

        return True

    class CustomPandasDataSet(ge.dataset.PandasDataSet):
        
        @ge.dataset.DataSet.column_expectation
        def expect_column_values_to_be_prime(self, column, mostly=None, suppress_expectations=False):
            notnull = self[column].notnull()
            
            result = self[column][notnull].map(isprime)
            exceptions = list(self[column][notnull][result==False])
            
            if mostly:
                #Prevent division-by-zero errors
                if len(not_null_values) == 0:
                    return {
                        'success':True,
                        'exception_list':exceptions
                    }

                percent_properly_formatted = float(sum(properly_formatted))/len(not_null_values)
                return {
                    "success" : percent_properly_formatted >= mostly,
                    "exception_list" : exceptions
                }
            else:
                return {
                    "success" : len(exceptions) == 0,
                    "exception_list" : exceptions
                }

    script_path = os.path.dirname(os.path.realpath(__file__))
    df = ge.read_csv(
        script_path+'/examples/titanic.csv',
        dataset_class=CustomPandasDataSet
    )

    assert_equal(
        df.expect_column_values_to_be_prime('Age'),
        {'exception_list':[30.0,25.0,0.92000000000000004,63.0,39.0,58.0,50.0,24.0,36.0,26.0,25.0,25.0,28.0,45.0,39.0,30.0,58.0,45.0,22.0,48.0,44.0,60.0,45.0,58.0,36.0,33.0,36.0,36.0,14.0,49.0,36.0,46.0,27.0,27.0,26.0,64.0,39.0,55.0,70.0,69.0,36.0,39.0,38.0,27.0,27.0,4.0,27.0,50.0,48.0,49.0,48.0,39.0,36.0,30.0,24.0,28.0,64.0,60.0,49.0,44.0,22.0,60.0,48.0,35.0,22.0,45.0,49.0,54.0,38.0,58.0,45.0,46.0,25.0,21.0,48.0,49.0,45.0,36.0,55.0,52.0,24.0,16.0,44.0,51.0,42.0,35.0,35.0,38.0,35.0,50.0,49.0,46.0,58.0,42.0,40.0,42.0,55.0,50.0,16.0,21.0,30.0,15.0,30.0,46.0,54.0,36.0,28.0,65.0,33.0,44.0,55.0,36.0,58.0,64.0,64.0,22.0,28.0,22.0,18.0,52.0,46.0,56.0,33.0,27.0,55.0,54.0,48.0,18.0,21.0,34.0,40.0,36.0,50.0,39.0,56.0,28.0,56.0,56.0,24.0,18.0,24.0,45.0,40.0,6.0,57.0,32.0,62.0,54.0,52.0,62.0,63.0,46.0,52.0,39.0,18.0,48.0,49.0,39.0,46.0,64.0,60.0,60.0,55.0,54.0,21.0,57.0,45.0,50.0,50.0,27.0,20.0,51.0,21.0,36.0,40.0,32.0,33.0,30.0,28.0,18.0,34.0,32.0,57.0,18.0,36.0,28.0,51.0,32.0,28.0,36.0,4.0,1.0,12.0,34.0,26.0,27.0,15.0,45.0,40.0,20.0,25.0,36.0,25.0,42.0,26.0,26.0,0.82999999999999996,54.0,44.0,52.0,30.0,30.0,27.0,24.0,35.0,8.0,22.0,30.0,20.0,21.0,49.0,8.0,28.0,18.0,28.0,22.0,25.0,18.0,32.0,18.0,42.0,34.0,8.0,21.0,38.0,38.0,35.0,35.0,38.0,24.0,16.0,26.0,45.0,24.0,21.0,22.0,34.0,30.0,50.0,30.0,1.0,44.0,28.0,6.0,30.0,45.0,24.0,24.0,49.0,48.0,34.0,32.0,21.0,18.0,21.0,52.0,42.0,36.0,21.0,33.0,34.0,22.0,45.0,30.0,26.0,34.0,26.0,22.0,1.0,25.0,48.0,57.0,27.0,30.0,20.0,45.0,46.0,30.0,48.0,54.0,64.0,32.0,18.0,32.0,26.0,20.0,39.0,22.0,24.0,28.0,50.0,20.0,40.0,42.0,21.0,32.0,34.0,33.0,8.0,36.0,34.0,30.0,28.0,0.80000000000000004,25.0,50.0,21.0,25.0,18.0,20.0,30.0,30.0,35.0,22.0,25.0,25.0,14.0,50.0,22.0,27.0,27.0,30.0,22.0,35.0,30.0,28.0,12.0,40.0,36.0,28.0,32.0,4.0,36.0,33.0,32.0,26.0,30.0,24.0,18.0,42.0,16.0,35.0,16.0,25.0,18.0,20.0,30.0,26.0,40.0,24.0,18.0,0.82999999999999996,20.0,25.0,35.0,32.0,20.0,39.0,39.0,6.0,38.0,9.0,26.0,4.0,20.0,26.0,25.0,18.0,24.0,35.0,40.0,38.0,9.0,45.0,27.0,20.0,32.0,33.0,18.0,40.0,26.0,15.0,45.0,18.0,27.0,22.0,26.0,22.0,20.0,32.0,21.0,18.0,26.0,6.0,9.0,40.0,32.0,26.0,18.0,20.0,22.0,22.0,35.0,21.0,20.0,18.0,18.0,38.0,30.0,21.0,21.0,21.0,24.0,33.0,33.0,28.0,16.0,28.0,24.0,21.0,32.0,26.0,18.0,20.0,24.0,24.0,36.0,30.0,22.0,35.0,27.0,30.0,36.0,9.0,44.0,45.0,22.0,30.0,34.0,28.0,0.33000000000000002,27.0,25.0,24.0,22.0,21.0,26.0,33.0,1.0,0.17000000000000001,25.0,36.0,36.0,30.0,26.0,65.0,42.0,32.0,30.0,24.0,24.0,24.0,22.0,18.0,16.0,45.0,21.0,18.0,9.0,48.0,16.0,25.0,38.0,22.0,16.0,33.0,9.0,38.0,40.0,14.0,16.0,9.0,10.0,6.0,40.0,32.0,20.0,28.0,24.0,28.0,24.0,20.0,45.0,26.0,21.0,27.0,18.0,26.0,22.0,28.0,22.0,27.0,42.0,27.0,25.0,27.0,20.0,48.0,34.0,22.0,33.0,32.0,26.0,49.0,1.0,33.0,4.0,24.0,32.0,27.0,21.0,32.0,20.0,21.0,30.0,21.0,22.0,4.0,39.0,20.0,21.0,44.0,42.0,21.0,24.0,25.0,22.0,22.0,39.0,26.0,4.0,22.0,26.0,1.5,36.0,18.0,25.0,22.0,20.0,26.0,22.0,32.0,21.0,21.0,36.0,39.0,25.0,45.0,36.0,30.0,20.0,21.0,1.5,25.0,18.0,63.0,18.0,15.0,28.0,36.0,28.0,10.0,36.0,30.0,22.0,14.0,22.0,51.0,18.0,45.0,28.0,21.0,27.0,36.0,27.0,15.0,27.0,26.0,22.0,24.0],'success':False}
    )

    primes = [3,5,7,11,13,17,23,31]
    df["primes"] = df.Age.map(lambda x: random.choice(primes))
    assert_equal(
        df.expect_column_values_to_be_prime("primes"),
        {'exception_list': [], 'success': True}
    )


def test_custom_class_2():

    def expectation(func):

        def wrapper(self, *args, **kwargs):

            #Get the name of the method
            method_name = func.__name__

            #Fetch argument names
            method_arg_names = inspect.getargspec(func)[0][1:]

            #Construct the expectation_config object
            expectation_config = dict(
                zip(method_arg_names, args)+\
                kwargs.items()
            )

            #Add the expectation_method key
            expectation_config['expectation_type'] = method_name

            #Append the expectation to the config.
            self.append_expectation(expectation_config)

            #Finally, execute the expectation method itself
            return func(self, *args, **kwargs)

        wrapper.__doc__ = func.__doc__
        return wrapper

    # @expectation
    # def column_expectation(expectation_method_name):
        
    #     def outer_wrapper(self, func):
    #         print expectation_method_name
    #         print func
    #         # print func.__class__
    #         # print self

    #         def inner_wrapper(self, column, mostly=None, suppress_expectations=False):
    #             print 'Here'
    #             print self

    #             notnull = self[column].notnull()
                
    #             success = func(self[column][notnull])
    #             exceptions = list(self[column][notnull][success==False])
                
    #             if mostly:
    #                 #Prevent division-by-zero errors
    #                 if notnull.sum() == 0:
    #                     return {
    #                         'success':True,
    #                         'exception_list':exceptions
    #                     }

    #                 percent_success = float(success.sum())/notnull.sum()
    #                 return {
    #                     "success" : percent_success >= mostly,
    #                     "exception_list" : exceptions
    #                 }
    #             else:
    #                 return {
    #                     "success" : len(exceptions) == 0,
    #                     "exception_list" : []
    #                 }

    #         return inner_wrapper

    #     return outer_wrapper

    # def column_expectation(func):

    #     @expectation
    #     def inner_wrapper(self, column, mostly=None, suppress_expectations=False):
    #         notnull = self[column].notnull()
            
    #         success = func(self, self[column][notnull])
    #         exceptions = list(self[column][notnull][success==False])

    #         if mostly:
    #             #Prevent division-by-zero errors
    #             if notnull.sum() == 0:
    #                 return {
    #                     'success':True,
    #                     'exception_list':exceptions
    #                 }

    #             percent_success = float(success.sum())/notnull.sum()
    #             return {
    #                 "success" : percent_success >= mostly,
    #                 "exception_list" : exceptions
    #             }

    #         else:
    #             return {
    #                 "success" : len(exceptions) == 0,
    #                 "exception_list" : exceptions
    #             }

    #     return inner_wrapper


    def column_expectation(func):

        @expectation
        def inner_wrapper(self, column, mostly=None, suppress_expectations=False):
            null_indexes = self._get_null_indexes(column)

            nonnull_values = self._get_nonnull_values(column, null_indexes)
            nonnull_count = self._get_null_count(null_indexes)
            
            successful_indexes = func(self, nonnull_values)
            success_count = self._get_success_count(successful_indexes)

            exceptions = list(self._get_exceptions(column, successful_indexes))

            if mostly:
                #Prevent division-by-zero errors
                if notnull.sum() == 0:
                    return {
                        'success':True,
                        'exception_list':exceptions
                    }

                percent_success = float(success_count)/notnull_count
                return {
                    "success" : percent_success >= mostly,
                    "exception_list" : exceptions
                }

            else:
                return {
                    "success" : len(exceptions) == 0,
                    "exception_list" : exceptions
                }

        return inner_wrapper

    def elementwise_expectation(func):

        @expectation
        def inner_wrapper(self, column, mostly=None, suppress_expectations=False):
            notnull = self[column].notnull()
            
            success = self[column][notnull].map(lambda x: func(self,x))
            exceptions = list(self[column][notnull][success==False])

            if mostly:
                #Prevent division-by-zero errors
                if notnull.sum() == 0:
                    return {
                        'success':True,
                        'exception_list':exceptions
                    }

                percent_success = float(success.sum())/notnull.sum()
                return {
                    "success" : percent_success >= mostly,
                    "exception_list" : exceptions
                }

            else:
                return {
                    "success" : len(exceptions) == 0,
                    "exception_list" : exceptions
                }

        return inner_wrapper

    class CustomPandasDataSet(ge.dataset.PandasDataSet):
        
        @expectation
        def expect_column_values_to_equal_1(self, column, mostly=None, suppress_expectations=False):
            notnull = self[column].notnull()
            
            result = self[column][notnull] == 1
            exceptions = list(self[column][notnull][result==False])
            
            if mostly:
                #Prevent division-by-zero errors
                if len(not_null_values) == 0:
                    return {
                        'success':True,
                        'exception_list':exceptions
                    }

                percent_properly_formatted = float(sum(properly_formatted))/len(not_null_values)
                return {
                    "success" : percent_properly_formatted >= mostly,
                    "exception_list" : exceptions
                }
            else:
                return {
                    "success" : len(exceptions) == 0,
                    "exception_list" : exceptions
                }

        @column_expectation
        def expect_column_values_to_equal_2(self, series):
            return series.map(lambda x: x==2)

        @elementwise_expectation
        def expect_column_values_to_equal_3(self, element):
            return element == 3

    df = CustomPandasDataSet({
        'x' : [1,2,3,4,5],
        'a' : [1,1,1,1,1],
        'b' : [2,2,2,2,2],
        'c' : [3,3,3,3,3],
    })

    assert_equal(
        df.expect_column_values_to_equal_1('x'),
        {
            "success": False,
            "exception_list": [2,3,4,5]
        }
    )
    assert_equal(
        df.expect_column_values_to_equal_1('a'),
        {
            "success": True,
            "exception_list": []
        }
    )

    assert_equal(
        df.expect_column_values_to_equal_2('x'),
        {
            "success": False,
            "exception_list": [1,3,4,5]
        }
    )
    assert_equal(
        df.expect_column_values_to_equal_2('b'),
        {
            "success": True,
            "exception_list": []
        }
    )

    assert_equal(
        df.expect_column_values_to_equal_3('x'),
        {
            "success": False,
            "exception_list": [1,2,4,5]
        }
    )
    assert_equal(
        df.expect_column_values_to_equal_3('c'),
        {
            "success": True,
            "exception_list": []
        }
    )

