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

        # Project, Filter, Sort, Paginate, Include
        self._attrs = None
        self._filter = []
        self._sort = []
        self._include = []
        self.page = 1
        self.per_page = 10

    def attrs(self, attributes=None):
        """ Projection. Query only those attributes which you need.

            attributes - list of attribute names (fields)
        """

        if not isinstance(attributes, list):
            raise OMSQueryException("attributes must be a list")

        self._attrs = attributes

        return self

    def filter(self, attribute, value, operator="EQ"):
        """ Filtering of a result set

            attribute - name of a attribute (field)
            value - filtering against value
            operator - one of supported operators (OMS_FILTER_OPERATORS)
        """

        if not isinstance(operator, str):
            raise OMSQueryException("operator name must be a string")

        operator = operator.upper()

        if operator not in OMS_FILTER_OPERATORS:
            raise OMSQueryException("{op} is not supported operator".format(op=operator))

        self._filter.append("filter[{k}][{op}]={v}".format(k=attribute, op=operator, v=value))

        return self

    def sort(self, attribute, asc=True):
        """ Sort result set

            attribute - name of attribute (field)
            asc - ascending direction or not
        """

        if not isinstance(attribute, str):
            raise OMSQueryException("attribute name must be a string")

        if not asc:
            attribute = "-"+attribute

        self._sort.append(attribute)

        return self

    def paginate(self, page=1, per_page=10):
        """ Paginate result set """

        self.page = page
        self.per_page = per_page

        return self

    def include(self, key):
        """ Include special flags to a query """

        if key not in OMS_INCLUDES:
            raise OMSQueryException("{key} is not supported include".format(key=key))

        self._include.append(key)

        return self

    def data(self, verbose=False):
        """ Execute query and retrieve data """

        url = "{base_url}/{resource}/".format(base_url=self.base_url,
                                              resource=self.resource)

        url_params = []

        # Project
        if self._attrs:
            url_params.append("fields=" + ",".join(self._attrs))

        # Filter
        url_params.extend(self._filter)

        # Sort
        if self._sort:
            url_params.append("sort=" + ",".join(self._sort))

        # Include
        if self._include:
            url_params.append("include=" + ",".join(self._include))

        # Paginate
        page_offset = self.per_page * (self.page - 1)
        url_params.append("page[offset]={offset}".format(offset=page_offset))
        url_params.append("page[limit]={per_page}".format(per_page=self.per_page))

        if url_params:
            url = url + "?" + "&".join(url_params)

        if verbose:
            print(url)

        return requests.get(url)

    def meta(self):
        """ TODO Get meta information about resource without fetching data """
        pass

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
