# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import simplejson as json
from sqlalchemy import types
from yelp_lib import dates

from replication_handler.config import env_config

try:
    from yelp_conn.session import declarative_base
    from replication_handler.models.yelp_sqla import get_tracker_session
    from replication_handler.models.yelp_sqla import get_state_session
except ImportError:
    # falling back to SQLAlchamy
    from sqlalchemy.ext.declarative import declarative_base
    from replication_handler.models.default_sqla import get_tracker_session
    from replication_handler.models.default_sqla import get_state_session


CLUSTER_NAME = env_config.rbr_state_cluster

# The common declarative base used by every data model.
Base = declarative_base()
Base.__cluster__ = CLUSTER_NAME

schema_tracker_session = get_tracker_session()
rbr_state_session = get_state_session()


class UnixTimeStampType(types.TypeDecorator):
    """ A datetime.datetime that is stored as a unix timestamp."""
    impl = types.Integer

    def process_bind_param(self, value, dialect=None):
        if value is None:
            return None
        return int(dates.to_timestamp(dates.get_datetime(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return dates.from_timestamp(value)


def default_now(context):
    return dates.default_now().replace(microsecond=0)


class JSONType(types.TypeDecorator):
    """ A JSONType is stored in the db as a string and we interact with it like a
    dict.
    """
    impl = types.Text
    separators = (',', ':')

    def process_bind_param(self, value, dialect=None):
        """ Dump our value to a form our db recognizes (a string)."""
        if value is None:
            return None

        return json.dumps(value, separators=self.separators)

    def process_result_value(self, value, dialect=None):
        """ Convert what we get from the db into a json dict"""
        if value is None:
            return None
        return json.loads(value)
