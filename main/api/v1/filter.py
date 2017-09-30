# coding: utf-8

from __future__ import absolute_import

from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
import flask
import flask_restful
import werkzeug

from api import helpers
import auth
import config
import model
import util

from main import api_v1


###############################################################################
# Endpoints
###############################################################################
@api_v1.resource('/filter/', endpoint='api.filter.list')
class FilterListAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self):
    pass
    # resource_keys = util.param('resource_keys', list)
    # if resource_keys:
    #   resource_db_keys = [ndb.Key(urlsafe=k) for k in resource_keys]
    #   resource_dbs = ndb.get_multi(resource_db_keys)
    #   return helpers.make_response(resource_dbs, model.Resource.FIELDS)

    # resource_dbs, next_cursor = model.Resource.get_dbs()
    # return helpers.make_response(
    #     resource_dbs, model.Resource.FIELDS, next_cursor,
    #   )

  @auth.admin_required
  def delete(self):
    pass
    # resource_keys = util.param('resource_keys', list)
    # if not resource_keys:
    #   helpers.make_not_found_exception(
    #       'Resource(s) %s not found' % resource_keys
    #     )
    # resource_db_keys = [ndb.Key(urlsafe=k) for k in resource_keys]
    # delete_resource_dbs(resource_db_keys)
    # return flask.jsonify({
    #     'result': resource_keys,
    #     'status': 'success',
    #   })


@api_v1.resource('/filter/<string:key>/', endpoint='api.filter')
class FilterAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self, key):
    filter_db = ndb.Key(urlsafe=key).get()
    if not filter_db:
      helpers.make_not_found_exception('Filter %s not found' % key)
    return helpers.make_response(filter_db, model.Filter.FIELDS)

  @auth.admin_required
  def delete(self, key):
    filter_db = ndb.Key(urlsafe=key).get()
    if not filter_db:
      helpers.make_not_found_exception('Filter %s not found' % key)
    delete_filter_key(filter_db.key)
    return helpers.make_response(filter_db, model.Filter.FIELDS)

@api_v1.resource('/filter/create/', endpoint='api.filter.create')
class FilterCreateAPI(flask_restful.Resource):
  @auth.admin_required
  def post(self):
    filter_db = model.Filter(
      id=u'{}-{}'.format(util.param('filter_value'), util.param('filter_value')),
      label=util.param('label'),
      filter_property=util.param('filter_property'),
      filter_value=util.param('filter_value'),
    )
    filter_db.put()
    return helpers.make_response(filter_db, model.Filter.FIELDS)

# ###############################################################################
# # Helpers
# ###############################################################################
# @ndb.transactional(xg=True)
# def delete_resource_dbs(resource_db_keys):
#   for resource_key in resource_db_keys:
#     delete_resource_key(resource_key)


def delete_filter_key(filter_key):
  filter_db = filter_key.get()
  if filter_db:
    filter_db.key.delete()
