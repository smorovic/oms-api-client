# pylint: disable=W0702,R0902
""" CMS OMS Aggregation API python client
"""

from __future__ import print_function
import requests

OMS_FILTER_OPERATORS = ["EQ", "NEQ", "LT", "GT", "LE", "GE", "LIKE"]
OMS_INCLUDES = ["meta", "presentation_timestamp"]

class OMSQueryException(Exception):
    """ OMS API Client Exception """
    pass

class OMSQuery(object):
    """ OMS Query object """

    def __init__(self, base_url, resource):
        self.base_url = base_url
        self.resource = resource
        self.verbose = True

        self._attrs = None  # Projection
        self._filter = []   # Filtering
        self._sort = []     # Sorting
        self._include = []  # Include

        # Pagination
        self.page = 1
        self.per_page = 10

        # Metadata
        self.metadata = None

        self._load_meta()

    def _attr_exists(self, attr):
        """ Check if attribute exists

            Returns:
                bool: False if attribute does not exist
                      True if exists or it is not available to check
        """

        if self.metadata and attr not in self.metadata:
            self._warn("Attribute [{attr}] does not exist".format(attr=attr))
            return False

        return True

    def _load_meta(self):
        """ Load meta information about resource without fetching data"""

        url = "{base_url}/{resource}/meta".format(base_url=self.base_url,
                                                  resource=self.resource)

        response = requests.get(url)

        if response.status_code != 200:
            self._warn("Failed to fetch meta information")
        else:
            try:
                self.metadata = response.json()["meta"]["fields"]
            except:
                self._warn("Meta information is incorrect")

    def _warn(self, message, raise_exc=False):
        """ Print Warning message or raise Exception

            Args:
                message (str): warning message to be printed or raised as exception
                raise_exc (bool):  raise Exception or just print warning
        """

        if raise_exc:
            raise OMSQueryException(message)

        if self.verbose:
            print("Warning: {message}".format(message=message))

    def set_verbose(self, verbose):
        """ Set verbose flag

            Args:
                verbose (bool): True/False

            Examples:
                .set_verbose(True)
        """
        self.verbose = verbose

    def attrs(self, attributes=None):
        """ Projection. Query only those attributes which you need.

            Args:
                attributes (list): list of attribute names.

            Examples:
                .attrs(["fill_number", "run_number"])
        """

        if not isinstance(attributes, list):
            self._warn("attrs() - attributes must be a list", raise_exc=True)

        # Find only existing attributes, remove duplicates
        self._attrs = [attr for attr in set(attributes) if self._attr_exists(attr)]

        return self

    def filter(self, attribute, value, operator="EQ"):
        """ Filtering of a result set

            Args:
                attribute (str): name of a attribute (field)
                value (str/int/bool): filtering against value
                operator (str): one of supported operators (OMS_FILTER_OPERATORS)

            Examples:
                .filter("fill_number", 5000, "GT")
        """

        if not isinstance(operator, str):
            self._warn("filter() - operator name must be a string", raise_exc=True)

        operator = operator.upper()

        if operator not in OMS_FILTER_OPERATORS:
            self._warn("filter() - [{op}] is not supported operator".format(op=operator), raise_exc=True)



        if self._attr_exists(attribute):
            # Check metadata if attribute is searchable
            searchable = True
            try:
                searchable = metadata["searchable"]
            except:
                # Metadata is not available or not complete
                pass

            if searchable:
                self._filter.append("filter[{k}][{op}]={v}".format(k=attribute,
                                                                   op=operator,
                                                                   v=value))
        return self

    def clear_filter(self):
        """ Remove all filters
        """
        
        self._filter = []
        
        return self


    def sort(self, attribute, asc=True):
        """ Sort result set

            Args:
                attribute (str): name of attribute (field)
                asc (bool): ascending direction or not

            Examples:
                .sort("fill_number", asc=False)
        """

        if not isinstance(attribute, str):
            self._warn("sort() - attribute name must be a string", raise_exc=True)

        if self._attr_exists(attribute):
            # Check metadata if attribute is sortable
            sortable = True
            try:
                sortable = metadata["fields"]["sortable"]
            except:
                # Metadata is not available or not complete
                pass

            if sortable:
                if not asc:
                    attribute = "-"+attribute

                self._sort.append(attribute)

        return self

    def paginate(self, page=1, per_page=10):
        """ Paginate result set

            Args:
                page (int): page number
                per_page (int): page size(limit)

            Examples:
                .paginate(2, 25)
        """

        self.page = page
        self.per_page = per_page

        return self

    def include(self, key):
        """ Include special flags to a query

            Args:
                key (str): one of supported keys

            Examples:
                .include("meta")
        """

        if key not in OMS_INCLUDES:
            self._warn("{key} is not supported include".format(key=key), raise_exc=True)

        self._include.append(key)

        return self

    def data(self):
        """ Execute query and retrieve data

            Returns:
                requests.Response object
        """

        url = "{base_url}/{resource}/".format(base_url=self.base_url,
                                              resource=self.resource)

        url_params = []

        # Project
        if self._attrs:
            url_params.append("fields=" + ",".join(set(self._attrs)))

        # Filter
        url_params.extend(self._filter)

        # Sort
        if self._sort:
            url_params.append("sort=" + ",".join(set(self._sort)))

        # Include
        if self._include:
            url_params.append("include=" + ",".join(set(self._include)))

        # Paginate
        page_offset = self.per_page * (self.page - 1)
        url_params.append("page[offset]={offset}".format(offset=page_offset))
        url_params.append("page[limit]={per_page}".format(per_page=self.per_page))

        if url_params:
            url = url + "?" + "&".join(url_params)

        if self.verbose:
            print(url)

        return requests.get(url)

    def meta(self):
        """ Returns metadata of a resource.

            Returns:
                str: if metadata is available
                None: if metadata is unavailable
        """
        return self.metadata


class OMSAPI(object):
    """ Base OMS API client """

    def __init__(self, api_url="", api_version="v1"):
        self.api_url = api_url
        self.api_version = api_version

        self.base_url = "{api_url}/{api_version}".format(api_url=api_url,
                                                         api_version=api_version)

        self._auth = None

    def query(self, resource):
        """ Create query object """

        q = OMSQuery(self.base_url, resource=resource)

        return q

    def auth(self):
        """ TODO Authorisation details for https """
        pass
