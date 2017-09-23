# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
import flask

from api import fields
import model
import util


class ResourceReview(model.Base):
  reviewer_user_key = ndb.KeyProperty(kind=model.User, required=True)
  value = ndb.IntegerProperty(default=1)

  FIELDS = {
    'value': fields.Integer,
  }

  FIELDS.update(model.Base.FIELDS)
