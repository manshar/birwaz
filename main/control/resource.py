# coding: utf-8

import urllib
import re

from google.appengine.ext import blobstore
import flask
import flask_wtf
import wtforms

import auth
import config
import model
import util

from main import app


###############################################################################
# Upload
###############################################################################
@app.route('/resource/upload/')
@auth.login_required
def resource_upload():
  return flask.render_template(
    'resource/resource_upload.html',
    title='Resource Upload',
    html_class='resource-upload',
    get_upload_url=flask.url_for('api.resource.upload'),
    has_json=True,
    upload_url=blobstore.create_upload_url(
      flask.request.path,
      gs_bucket_name=config.CONFIG_DB.bucket_name or None,
    ),
  )


###############################################################################
# Public List
###############################################################################
@app.route('/resource/', endpoint='resource_grid')
def resource_grid():
  resource_dbs, cursors = model.Resource.get_dbs(
    model.Resource.query(model.Resource.hotness > 0),
    limit=20, prev_cursor=True, order='-hotness')

  return flask.render_template(
    'resource/resource_grid.html',
    html_class='resource-grid',
    title='Resource Grid',
    resource_dbs=resource_dbs,
    next_url=util.generate_next_url(cursors.get('next')),
    prev_url=util.generate_next_url(cursors.get('prev')),
    api_url=flask.url_for('api.resource.list'),
  )


###############################################################################
# Public Search
###############################################################################
@app.route('/resource/search/', endpoint='resource_search')
def resource_search():
  query = model.Resource.query(model.Resource.hotness > 0)
  tags = util.param('tags', list)
  if tags:
    query = query.filter(model.Resource.tags.IN(tags))
  address_first_line = util.param('address_first_line')
  if address_first_line:
    query = query.filter(
      model.Resource.address_first_line == address_first_line)
  address_second_line = util.param('address_second_line')
  if address_second_line:
    query = query.filter(
      model.Resource.address_second_line == address_second_line)
  city = util.param('city')
  if city:
    query = query.filter(model.Resource.city == city)
  country = util.param('country')
  if country:
    query = query.filter(model.Resource.country == country)

  resource_dbs, cursors = model.Resource.get_dbs(
    query,
    limit=20, prev_cursor=True, order='-hotness')

  return flask.render_template(
    'resource/resource_grid.html',
    html_class='resource-grid',
    title='Resource Grid',
    resource_dbs=resource_dbs,
    next_url=util.generate_next_url(cursors.get('next')),
    prev_url=util.generate_next_url(cursors.get('prev')),
    api_url=flask.url_for('api.resource.list'),
  )

###############################################################################
# View
###############################################################################
@app.route('/resource/<int:resource_id>/', endpoint='resource_view')
def resource_view(resource_id):
  resource_db = model.Resource.get_by_id(resource_id)
  if not resource_db:
    return flask.abort(404)
  user_db = resource_db.user_key.get()
  return flask.render_template(
    'resource/resource_view.html',
    html_class='resource-view',
    title='%s' % (resource_db.name),
    resource_db=resource_db,
    user_db=user_db,
    api_url=flask.url_for('api.resource', key=resource_db.key.urlsafe()),
  )


###############################################################################
# Update
###############################################################################
class ResourceUpdateForm(flask_wtf.FlaskForm):
  name = wtforms.TextField(u'عنوان الصورة', [wtforms.validators.required()])
  description = wtforms.TextAreaField(u'وصف الصورة', [wtforms.validators.optional()])
  address_first_line = wtforms.TextField(u'عنوان الشارع', [wtforms.validators.optional()])
  address_second_line = wtforms.TextField(u'القرية/الحارة/المنطقة', [wtforms.validators.optional()])
  city = wtforms.TextField(u'المدينة', [wtforms.validators.optional()])
  country = wtforms.TextField(u'البلد', [wtforms.validators.optional()])
  tags = wtforms.FieldList(wtforms.TextField(u'كلمة وصفية'), min_entries=2, label=u'الكلمات الوصفية الحالية')
  new_tags = wtforms.TextField(u'كلمات وصفية جديدة (افصل بينهم بفاصلة)')


@app.route('/resource/<int:resource_id>/update/', methods=['GET', 'POST'], endpoint='resource_update')
@auth.login_required
def resource_update(resource_id):
  resource_db = model.Resource.get_by_id(resource_id)

  if not resource_db or resource_db.user_key != auth.current_user_key():
    return flask.abort(404)

  form = ResourceUpdateForm(obj=resource_db)

  if form.validate_on_submit():
    form.populate_obj(resource_db)
    print 'form.new_tags.data'
    print form.new_tags.data.encode('utf8')
    if form.new_tags.data:
      new_tags = re.split(ur'[,\u060c]', form.new_tags.data)
      resource_db.tags = set(
        resource_db.tags +
        list(set([tag.strip() for tag in new_tags if tag])))
    resource_db.tags = [tag for tag in resource_db.tags if len(tag) > 0]

    print resource_db.tags
    resource_db.put()
    return flask.redirect(flask.url_for(
      'resource_view', resource_id=resource_db.key.id(),
    ))

  return flask.render_template(
    'resource/resource_update.html',
    html_class='resource-update',
    title='%s' % (resource_db.name),
    resource_db=resource_db,
    form=form,
    api_url=flask.url_for('api.resource', key=resource_db.key.urlsafe()),
  )


###############################################################################
# Download
###############################################################################
@app.route('/resource/<int:resource_id>/download/')
@auth.login_required
def resource_download(resource_id):
  resource_db = model.Resource.get_by_id(resource_id)
  if not resource_db or resource_db.user_key != auth.current_user_key():
    return flask.abort(404)
  name = urllib.quote(resource_db.name.encode('utf-8'))
  url = '/serve/%s?save_as=%s' % (resource_db.blob_key, name)
  return flask.redirect(url)


###############################################################################
# Admin List
###############################################################################
@app.route('/admin/resource/', endpoint='admin_resource_list')
@auth.admin_required
def admin_resource_list():
  resource_dbs, cursors = model.Resource.get_dbs(hotness=-1,
    limit=10, prev_cursor=True, order='-created')

  return flask.render_template(
    'resource/resource_list.html',
    html_class='resource-list',
    title='Resource List',
    resource_dbs=resource_dbs,
    next_url=util.generate_next_url(cursors.get('next')),
    prev_url=util.generate_next_url(cursors.get('prev')),
    api_url=flask.url_for('api.resource.list'),
  )
