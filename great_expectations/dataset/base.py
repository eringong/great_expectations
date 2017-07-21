import json
import inspect
import copy
from functools import wraps

import pandas as pd
import numpy as np

from .util import DotDict, ensure_json_serializable

class DataSet(object):

    def __init__(self, *args, **kwargs):
        super(DataSet, self).__init__(*args, **kwargs)
        self.initialize_expectations()

    def initialize_expectations(self, config=None, name=None):

        if config != None:
            #!!! Should validate the incoming config with jsonschema here

            # Copy the original so that we don't overwrite it by accident
            self._expectations_config = DotDict(copy.deepcopy(config))

        else:
            self._expectations_config = DotDict({
                "dataset_name" : None,
                "expectations" : []
            })

            for col in self.columns:
                self._expectations_config.expectations.append({
                    "expectation_type" : "expect_column_to_exist",
                    "kwargs" : {
                        "column" : col
                    }
                })

        self._expectations_config.dataset_name = name

    def append_expectation(self, expectation_config):
        expectation_type = expectation_config['expectation_type']

        #Drop existing expectations with the same expectation_type.
        #!!! This is good default behavior, but
        #!!!    it needs to be documented, and
        #!!!    we need to provide syntax to override it.
        self._expectations_config.expectations = [f for f in filter(
            lambda exp: exp['expectation_type'] != expectation_type,
            self._expectations_config.expectations
        )]

        self._expectations_config.expectations.append(expectation_config)


    def expectation(func):

        def wrapper(self, *args, **kwargs):

            #Get the name of the method
            method_name = func.__name__

            #Fetch argument names
            method_arg_names = inspect.getargspec(func)[0][1:]

            # Combine all arguments into a single new "kwargs"
            all_args = dict(zip(method_arg_names, args))
            all_args.update(kwargs)

            all_args = ensure_json_serializable(all_args)

            #Construct the expectation_config object
            expectation_config = DotDict({
                "expectation_type" : method_name,
                ## Changed to support python 3, but note that there may be ambiguity here.
                ## TODO: ensure this is the intended logic
                "kwargs" : all_args
            })

            #Add the expectation_method key
            expectation_config['expectation_type'] = method_name

            #Append the expectation to the config.
            self.append_expectation(expectation_config)

            #Finally, execute the expectation method itself
            return func(self, **all_args)

        wrapper.__doc__ = func.__doc__
        return wrapper

    def column_map_expectation(func):

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

    def column_aggregate_expectation(func):

        @expectation
        def inner_wrapper(self, column, mostly=None, suppress_expectations=False):
            pass

    def column_elementwise_expectation(func):

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

    @staticmethod
    def old_expectation(func):
        """
        !!! This method is deprecated.
        !!! It's still in use as a legacy method within PandasDataset, but that's temporary.
        !!! @column_expectations will be fully phased out before the v0.2 release.
        """

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


    @staticmethod
    def old_column_expectation(func):
        """
        !!! This method is deprecated.
        !!! It's still in use as a legacy method within PandasDataset, but that's temporary.
        !!! @column_expectations will be fully phased out before the v0.2 release.
        """

        def wrapper(self, column, *args, **kwargs):
            #Get the name of the method
            method_name = func.__name__

            #Fetch argument names
            method_arg_names = inspect.getargspec(func)[0][2:]

            # Combine all arguments into a single new "kwargs"
            all_args = dict(zip(method_arg_names, args))
            all_args.update(kwargs)

            all_args = ensure_json_serializable(all_args)

            #Construct the expectation_config object
            expectation_config = DotDict({
                "expectation_type" : method_name,
                ## Changed to support python 3, but note that there may be ambiguity here.
                ## TODO: ensure this is the intended logic
                "kwargs" : all_args
            })
            expectation_config['kwargs']['column'] = column

            #Append the expectation to the table config.
            self.append_expectation(expectation_config)

            #Now execute the expectation method itself
            return func(self, **all_args)

        wrapper.__doc__ = func.__doc__
        return wrapper

    def get_expectations_config(self):
        return self._expectations_config

    def save_expectations_config(self, filepath=None):
        if filepath==None:
            #!!! Fetch the proper filepath from the project config
            pass

        expectation_config_str = json.dumps(self.get_expectations_config(), indent=2)
        open(filepath, 'w').write(expectation_config_str)

    def validate(self):
        results = []
        for expectation in self.get_expectations_config()['expectations']:
            expectation_method = getattr(self, expectation['expectation_type'])
            result = expectation_method(**expectation['kwargs'])

            results.append(
                dict(expectation.items() + result.items())
            )

        return {
            "results" : results
        }


    ##### Table shape expectations #####

    def expect_column_to_exist(self, column, suppress_exceptions=False):
        """Expect the specified column to exist in the data set.
        Args:
            column (str): The column name.
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }

        """
        raise NotImplementedError

    def expect_table_row_count_to_be_between(self, min_value, max_value, suppress_exceptions=False):
        """Expect the number of rows in a data set to be between two values.
        Args:
            min_value (int or None): the minimum number of rows.
            max_value (int or None): the maximum number of rows.
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }
        See Also:
            expect_table_row_count_to_equal
        """
        raise NotImplementedError

    def expect_table_row_count_to_equal(self, value, suppress_exceptions=False):
        """Expect the number of rows to be equal to a value.
        Args:
	    value (int): The value that should equal the number of rows.
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }
        See Also:
            expect_table_row_count_to_be_between
        """
        raise NotImplementedError

    ##### Missing values, unique values, and types #####

    def expect_column_values_to_be_unique(self, column, mostly=None, suppress_exceptions=False):
        """Expect each nonempty column entry to be unique (no duplicates).
        Args:
            column (str): The column name.
        Keyword Args:
            mostly=None: Return "success": True if the percentage of unique values is greater than or equal to mostly (a float between 0 and 1).
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }

        Examples:
	    Display multiple duplicated items. For example, ['2','2','2'] will return `['2','2']` for the exceptions_list.
        """
        raise NotImplementedError

    def expect_column_values_to_not_be_null(self, column, mostly=None, suppress_exceptions=False):
        """Expect each column entry to be nonempty.
        Args:
            column (str): The column name.
        Keyword Args:
            mostly=None: Return "success": True if the percentage of not null values is greater than or equal to mostly (a float between 0 and 1).
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }
        See Also:
            expect_column_values_to_be_null

        """
        raise NotImplementedError

    def expect_column_values_to_be_null(self, column, mostly=None, suppress_exceptions=False):
        """Expect the column entries to be empty.
        Args:
            column (str): The column name.
        Keyword Args:
            mostly=None: Return "success": True if the percentage of null values is greater than or equal to mostly (a float between 0 and 1).
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }
        See Also:
            expect_column_values_to_not_be_null

        """
        raise NotImplementedError

    def expect_column_values_to_be_of_type(self, column, type_, target_datasource, mostly=None, suppress_exceptions=False):
        """Expect each column entry to be a specified data type.
        Args:
            column (str): The column name.
            type_ (str): A string representing the data type that each column should have as entries.
                For example, "double integer" refers to an integer with double precision.
            target_datasource (str): The data source that specifies the implementation in the type_ parameter.
                For example, options include "numpy", "sql", or "spark".
        Keyword Args:
            mostly=None: Return "success": True if the percentage of values of type_ is greater than or equal to mostly (a float between 0 and 1).
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }

        """
        raise NotImplementedError

    ##### Sets and ranges #####

    def expect_column_values_to_be_in_set(self, column, values_set, mostly=None, suppress_exceptions=False):
        """Expect each entry in a column to be in a given set.
        Args:
            column (str): The column name.
            values_set (set-like): The set of objects or unique data points corresponding to the column.
        Keyword Args:
            mostly=None: Return "success": True if the percentage of values in values_set is greater than or equal to mostly (a float between 0 and 1).
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }
        See Also:
            expect_column_values_to_not_be_in_set

        """
        raise NotImplementedError

    def expect_column_values_to_not_be_in_set(self, column, values_set, mostly=None, suppress_exceptions=False):
        """Expect column entries to not be in the set.
        Args:
            column (str): The column name.
            values_set (list): The set of objects or unique data points that should not correspond to the column.
        Keyword Args:
            mostly=None: Return "success": True if the percentage of values not in values_set is greater than or equal to mostly (a float between 0 and 1).
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }
        See Also:
            expect_column_values_to_not_be_in_set

        """
        raise NotImplementedError

    def expect_column_values_to_be_between(self, column, min_value, max_value, mostly=None, suppress_exceptions=False):
        """Expect column entries to be a number between a minimum value and a maximum value.
        Args:
            column (str): The column name.
            min_value (int or None): The minimum value for a column entry.
            max_value (int or None): The maximum value for a column entry.
        Keyword Args:
            mostly=None: Return "success": True if the percentage of values between min_value and max_value is greater than or equal to mostly (a float between 0 and 1).
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }
        See Also:
            expect_column_value_lengths_to_be_between

        """
        raise NotImplementedError

    ##### String matching #####

    def expect_column_value_lengths_to_be_between(self, column, min_value, max_value, mostly=None, suppress_exceptions=False):
        """Expect column entries to have a measurable length which lies between a minimum value and a maximum value.
        Args:
            column (str): The column name.
            min_value (int or None): The minimum value for a column entry length.
            max_value (int or None): The maximum value for a column entry length.
        Keyword Args:
            mostly=None: Return "success": True if the percentage of value lengths between min_value and max_value is greater than or equal to mostly (a float between 0 and 1).
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }
        See Also:
            expect_column_values_to_be_between

        """
        raise NotImplementedError

    def expect_column_values_to_match_regex(self, column, regex, mostly=None, suppress_exceptions=False):
        """Expect column entries to be strings that match a given regular expression.
        Args:
            column (str): The column name.
            regex (str): The regular expression that the column entry should match.
        Keyword Args:
            mostly=None: Return "success": True if the percentage of matches is greater than or equal to mostly (a float between 0 and 1).
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }
        See Also:
            expect_column_values_to_not_match_regex
            expect_column_values_to_match_regex_list
        """
        raise NotImplementedError

    def expect_column_values_to_not_match_regex(self, column, regex, mostly=None, suppress_exceptions=False):
        """Expect column entries to be strings that do NOT match a given regular expression.
        Args:
            column (str): The column name.
            regex (str): The regular expression that the column entry should NOT match.
        Keyword Args:
            mostly=None: Return "success": True if the percentage of NOT matches is greater than or equal to mostly (a float between 0 and 1).
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }
        See Also:
            expect_column_values_to_match_regex
            expect_column_values_to_match_regex_list
        """
        raise NotImplementedError

    def expect_column_values_to_match_regex_list(self, column, regex_list, required_match="any", mostly=None, suppress_exceptions=False):
        """Expect the column entries to be strings that match at least one of a list of regular expressions.
        Args:
            column (str): The column name.
            regex_list (list): The list of regular expressions in which the column entries should match according to required_match.
        Keyword Args:
            required_match="any": Use "any" if the value should match at least one regular expression in the list. Use "all" if it should match each regular expression in the list.
            mostly=None: Return "success": True if the percentage of matches is greater than or equal to mostly (a float between 0 and 1).
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }
        See Also:
            expect_column_values_to_match_regex
            expect_column_values_to_not_match_regex
        """
        raise NotImplementedError

    ##### Datetime and JSON parsing #####

    def expect_column_values_to_match_strftime_format(self, column, strftime_format, mostly=None, suppress_exceptions=False):
        """Expect column entries to be strings representing a date or time with a given format.
        WARNING: Note that strftime formats are not universally portable across implementations.
        For example, the %z directive may not be implemented before Python 3.2.
        Args:
            column (str): The column name.
            strftime_format (str): The datetime format that the column entries should match.
        Keyword Args:
            mostly=None: Return "success": True if the percentage of matches is greater than or equal to mostly (a float between 0 and 1).
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }
        """
        raise NotImplementedError

    def expect_column_values_to_be_dateutil_parseable(self, column, mostly=None, suppress_exceptions=False):
        """Expect column entries to be interpretable as a dateutil object.
        Args:
            column (str): The column name.
        Keyword Args:
            mostly=None: Return "success": True if the percentage of parseable values is greater than or equal to mostly (a float between 0 and 1).
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }
        """
        raise NotImplementedError

    def expect_column_values_to_be_valid_json(self, column, suppress_exceptions=False):
        """Expect column entries to be data written in JavaScript Object Notation.
        Args:
            column (str): The column name.
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }
        See Also:
            expect_column_values_to_match_json_schema
        """
        raise NotImplementedError

    def expect_column_values_to_match_json_schema(self, column, json_schema, suppress_exceptions=False):
        """Expect column entries to be JSON objects with a given JSON schema.
        Args:
            column (str): The column name.
            json_schema (JSON object): The JSON schema that each column entry should resemble.
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "exceptions_list": (list) the values that did not pass the expectation
                }
        See Also:
            expect_column_values_to_be_valid_json

        """
        raise NotImplementedError

    ##### Aggregate functions #####

    def expect_column_mean_to_be_between(self, column, min_value, max_value):
        """Expect the column mean to be between a minimum value and a maximum value.
        Args:
            column (str): The column name.
            min_value (int or None): The minimum value for the column mean.
            max_value (int or None): The maximum value for the column mean.
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "true_mean": (float) the column mean
                }
        """
        raise NotImplementedError

    def expect_column_median_to_be_between(self, column, min_value, max_value):
        """Expect the column median to be between a minimum value and a maximum value.
        Args:
            column (str): The column name.
            min_value (int or None): The minimum value for the column median.
            max_value (int or None): The maximum value for the column median.
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "true_median": (float) the column median
                }
        """
        raise NotImplementedError

    def expect_column_stdev_to_be_between(self, column, min_value, max_value, suppress_exceptions=False):
        """Expect the column standard deviation to be between a minimum value and a maximum value.
        Args:
            column (str): The column name.
            min_value (int or None): The minimum value for the column standard deviation.
            max_value (int or None): The maximum value for the column standard deviation.
        Returns:
            dict:
                {
                    "success": (bool) True if the column passed the expectation,
                    "true_stdev": (float) the true standard deviation
                }
        """
        raise NotImplementedError

    def expect_column_frequency_distribution_to_be(self, column, partition_object, p=0.05, suppress_exceptions=False):
        """
        Expect the values in this column to match the distribution of the specified categorical vals and their expected_frequencies. \

        Args:
            column (str): The column name
            vals (list): A list of categorical values.
            partition_object (dict): A dictionary containing partition (categorical values) and associated weights.
                - partition (list): A list of values that correspond to the provided categorical values.
                - weights (list): A list of weights. They should sum to one. The test will scale the expected frequencies by the weights and size of the new sample.
            p (float) = 0.05: The p-value threshold for the Chai Squareed test.\
                For values below the specified threshold the expectation will return false, rejecting the null hypothesis that the distributions are the same.
            suppress_exceptions: Only return a boolean success value, not a dictionary with other results.

        Returns:
            {
                "success": (bool) True if the column passed the expectation,
                "true_value": (float) the true pvalue of the ChiSquared test
            }
        """
        raise NotImplementedError

    def expect_column_numerical_distribution_to_be(self, column, partition_object, sample_size=0, p=0.05, suppress_exceptions=False):
        """
        Expect the values in this column to match the distribution implied by the specified partition and cdf_vals. \
        The implied CDF is constructed as a linear interpolation of the provided cdf_vals.

        Args:
            column (str): The column name
            partition_object (dict): A dictionary containing partition (bin edges) and associated weights.
                - partition (list): A list of values that correspond to the endpoints of an implied partition on the real number line.
                - weights (list): A list of weights. They should sum to one.
            sample_size (int) = 0: The number of samples from column to use in comparing\
                to the provided CDF. If zero, defaults to the number of elements in the partition.
                Setting the sample size too large will cause the KS test to be very sensitive to
                even small deviations from the provided distribution.
            p (float) = 0.05: The p-value threshold for the Kolmogorov-Smirnov test.\
                For values below the specified threshold the expectation will return false, rejecting the null hypothesis that the distributions are the same.
            suppress_exceptions: Only return a boolean success value, not a dictionary with other results.

        Returns:
            {
                "success": (bool) True if the column passed the expectation,
                "true_value": (float) the true pvalue of the KS test
            }
        """
        raise NotImplementedError

    def expect_column_kl_divergence_to_be(self, column, partition_object, threshold=0.1, suppress_exceptions=False):
        """
        Expect the values in this column to have lower Kulback-Leibler divergence (relative entropy) with the distriution provided in partition_object of less than the provided threshold.

        Args:
            column (str): The column name
            partition_object (dict): A dictionary containing partition (bin edges) and associated weights.
                - partition (list): A list of values that correspond to the endpoints of an implied partition on the real number line.
                - weights (list): A list of weights. They should sum to one.
            threshold (float) = 0.1: The threshold of relative entropy.\
                For values above the specified threshold the expectation will return false.
            suppress_exceptions: Only return a boolean success value, not a dictionary with other results.

        Returns:
            {
                "success": (bool) True if the column passed the expectation,
                "true_value": (float) the true value of the KL divergence
            }
        """
        raise NotImplementedError
