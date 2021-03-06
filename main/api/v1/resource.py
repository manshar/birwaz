# coding: utf-8

from __future__ import absolute_import

import datetime
import logging

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
@api_v1.resource('/resource/', endpoint='api.resource.list')
class ResourceListAPI(flask_restful.Resource):
  # @auth.admin_required
  def get(self):
    resource_keys = util.param('resource_keys', list)
    if resource_keys:
      resource_db_keys = [ndb.Key(urlsafe=k) for k in resource_keys]
      resource_dbs = ndb.get_multi(resource_db_keys)
      return helpers.make_response(resource_dbs, model.Resource.FIELDS)

    resource_dbs, next_cursor = model.Resource.get_dbs()
    return helpers.make_response(
        resource_dbs, model.Resource.FIELDS, next_cursor,
      )

  @auth.admin_required
  def delete(self):
    resource_keys = util.param('resource_keys', list)
    if not resource_keys:
      helpers.make_not_found_exception(
          'Resource(s) %s not found' % resource_keys
        )
    resource_db_keys = [ndb.Key(urlsafe=k) for k in resource_keys]
    delete_resource_dbs(resource_db_keys)
    return flask.jsonify({
        'result': resource_keys,
        'status': 'success',
      })


@api_v1.resource('/resource/<string:key>/', endpoint='api.resource')
class ResourceAPI(flask_restful.Resource):
  @auth.login_required
  def get(self, key):
    resource_db = ndb.Key(urlsafe=key).get()
    if not resource_db and resource_db.user_key != auth.current_user_key():
      helpers.make_not_found_exception('Resource %s not found' % key)
    return helpers.make_response(resource_db, model.Resource.FIELDS)

  @auth.login_required
  def delete(self, key):
    resource_db = ndb.Key(urlsafe=key).get()
    if not resource_db or (
      resource_db.user_key != auth.current_user_key() and
      not auth.current_user_db().admin):
      helpers.make_not_found_exception('Resource %s not found' % key)
    delete_resource_key(resource_db.key)
    return helpers.make_response(resource_db, model.Resource.FIELDS)

@api_v1.resource('/resource/<string:key>/approve', endpoint='api.resource.approve')
class ResourceApproveAPI(flask_restful.Resource):
  @auth.admin_required
  def put(self, key):
    resource_db = ndb.Key(urlsafe=key).get()
    if not resource_db:
      helpers.make_not_found_exception('Resource %s not found' % key)
    review = model.ResourceReview(parent=resource_db.key,
        reviewer_user_key=auth.current_user_key(), value=10)
    review.put()
    resource_db.reset_hotness()
    resource_db.put()
    return helpers.make_response(resource_db, model.Resource.FIELDS)

@api_v1.resource('/resource/<string:key>/reject', endpoint='api.resource.reject')
class ResourceRejectAPI(flask_restful.Resource):
  @auth.admin_required
  def put(self, key):
    resource_db = ndb.Key(urlsafe=key).get()
    if not resource_db:
      helpers.make_not_found_exception('Resource %s not found' % key)
    review = model.ResourceReview(parent=resource_db.key,
        reviewer_user_key=auth.current_user_key(), value=-10)
    review.put()
    resource_db.reset_hotness()
    resource_db.put()
    return helpers.make_response(resource_db, model.Resource.FIELDS)

@api_v1.resource('/resource/upload/', endpoint='api.resource.upload')
class ResourceUploadAPI(flask_restful.Resource):
  @auth.login_required
  def get(self):
    count = util.param('count', int) or 1
    urls = []
    for i in range(count):
      urls.append({'upload_url': blobstore.create_upload_url(
          flask.request.path,
          gs_bucket_name=config.CONFIG_DB.bucket_name or None,
        )})
    return flask.jsonify({
        'status': 'success',
        'count': count,
        'result': urls,
      })

  @auth.login_required
  def post(self):
    resource_db = resource_db_from_upload()
    if resource_db:
      return helpers.make_response(resource_db, model.Resource.FIELDS)
    flask.abort(500)


###############################################################################
# Helpers
###############################################################################
@ndb.transactional(xg=True)
def delete_resource_dbs(resource_db_keys):
  for resource_key in resource_db_keys:
    delete_resource_key(resource_key)


def delete_resource_key(resource_key):
  resource_db = resource_key.get()
  if resource_db:
    blobstore.BlobInfo.get(resource_db.blob_key).delete()
    resource_db.key.delete()


def resource_db_from_upload():
  try:
    uploaded_file = flask.request.files['file']
  except:
    return None
  headers = uploaded_file.headers['Content-Type']
  blob_info_key = werkzeug.parse_options_header(headers)[1]['blob-key']
  blob_info = blobstore.BlobInfo.get(blob_info_key)

  logging.info('Photo Info')
  logging.info('blob_info.size: {}'.format(blob_info.size))
  logging.info('blob_info.md5_hash: {}'.format(blob_info.md5_hash))
  logging.info('blob_info.creation: {}'.format(blob_info.creation))
  image_obj = images.Image(blob_key=blob_info.key())
  # image_obj.im_feeling_lucky()
  image_obj.resize(width=100)
  output = image_obj.execute_transforms(parse_source_metadata=True)
  logging.info('image_obj.width: {}'.format(image_obj.width))
  logging.info('image_obj.height: {}'.format(image_obj.height))

  metadata = image_obj.get_original_metadata()
  logging.info('metadata: {}'.format(metadata))
  logging.info('type(metadata): {}'.format(type(metadata)))

  image_url = None
  if blob_info.content_type.startswith('image'):
    try:
      image_url = images.get_serving_url(blob_info.key(), secure_url=True)
    except:
      pass

  taken_at = metadata.get('DateTimeOriginal')
  if taken_at:
    taken_at = datetime.datetime.fromtimestamp(float(taken_at))
  resource_db = model.Resource(
      user_key=auth.current_user_key(),
      blob_key=blob_info.key(),
      name=blob_info.filename,
      content_type=blob_info.content_type,
      size=blob_info.size,
      image_url=image_url,
      metadata=metadata,
      taken_at=taken_at,
      camera_make=metadata.get('Make'),
      camera_model=metadata.get('Model'),
      md5_hash=blob_info.md5_hash,
      width=metadata.get('ImageWidth') or image_obj.width,
      height=metadata.get('ImageLength') or image_obj.height,
      bucket_name=config.CONFIG_DB.bucket_name or None,
    )
  resource_db.put()
  return resource_db
