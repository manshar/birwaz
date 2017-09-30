# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
import flask

from api import fields
import model
import util


class Filter(model.Base):
  label = ndb.StringProperty(required=True)
  filter_property = ndb.StringProperty(required=True) # tags, city, country...etc
  filter_value = ndb.StringProperty(required=True)
  photos_count = ndb.IntegerProperty(default=0)
  description = ndb.TextProperty()

  FIELDS = {
    'label': fields.String,
    'description': fields.String,
    'filter_property': fields.String,
    'filter_value': fields.String,
    'photos_count': fields.Integer,
  }

  FIELDS.update(model.Base.FIELDS)

  # TODO(mk): Add a cron job to keep the photos_count accurate