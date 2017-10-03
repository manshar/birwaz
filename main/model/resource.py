# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
import flask

from api import fields
import model
import util
import datetime
import json

ranking_time_scale_constant = 45000
app_start_datetime = datetime.datetime(2017, 9, 1, 1, 1, 1)

class Resource(model.Base):
  user_key = ndb.KeyProperty(kind=model.User, required=True)
  blob_key = ndb.BlobKeyProperty(required=True)
  name = ndb.StringProperty(required=True)
  bucket_name = ndb.StringProperty()
  image_url = ndb.StringProperty(default='')
  content_type = ndb.StringProperty(default='')
  size = ndb.IntegerProperty(default=0)
  md5_hash = ndb.StringProperty(default='')
  metadata = ndb.JsonProperty()
  taken_at = ndb.DateTimeProperty()
  camera_make = ndb.StringProperty(default='')
  camera_model = ndb.StringProperty(default='')

  description = ndb.TextProperty()
  geo_location = ndb.GeoPtProperty()

  address_first_line = ndb.StringProperty()
  address_second_line = ndb.StringProperty()
  city = ndb.StringProperty()
  country = ndb.StringProperty()

  tags = ndb.StringProperty(repeated=True)
  # auto_tags = ndb.StringProperty(repeated=True)

  width = ndb.IntegerProperty(default=0)
  height = ndb.IntegerProperty(default=0)
  hotness = ndb.IntegerProperty(default=-1)

  @ndb.ComputedProperty
  def size_human(self):
    return util.size_human(self.size or 0)

  @property
  def metadata_pretty(self):
    return json.dumps(self.metadata, indent=2)
  @property
  def full_address(self):
    all_parts = []
    if self.address_first_line:
      all_parts.append(self.address_first_line)
    if self.address_second_line:
      all_parts.append(self.address_second_line)
    if self.city:
      all_parts.append(self.city)
    if self.country:
      all_parts.append(self.country)
    return ' - '.join(all_parts)

  @property
  def download_url(self):
    if self.key:
      return flask.url_for(
        'resource_download', resource_id=self.key.id(), _external=True
      )
    return None

  @property
  def view_url(self):
    if self.key:
      return flask.url_for(
        'resource_view', resource_id=self.key.id(), _external=True,
      )
    return None

  @property
  def serve_url(self):
    return '%s/serve/%s' % (flask.request.url_root[:-1], self.blob_key)

  def reset_hotness(self):
    reviews = model.ResourceReview.query(ancestor=self.key).fetch(20)
    self.hotness = sum([review.value for review in reviews])
    if self.hotness > 0:
      seconds = (self.created - app_start_datetime).total_seconds()
      self.hotness += int(seconds / max([1, ranking_time_scale_constant]))

  FIELDS = {
    'bucket_name': fields.String,
    'content_type': fields.String,
    'download_url': fields.String,
    'image_url': fields.String,
    'name': fields.String,
    'serve_url': fields.String,
    'size': fields.Integer,
    'size_human': fields.String,
    'view_url': fields.String,
    'hotness': fields.Integer,
    'md5_hash': fields.String,
    'width': fields.Integer,
    'height': fields.Integer,
  }

  FIELDS.update(model.Base.FIELDS)
