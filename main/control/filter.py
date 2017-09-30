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


# ###############################################################################
# # List Filters
# ###############################################################################
# @app.route('/resource/', endpoint='resource_grid')
# def resource_grid():
#   resource_dbs, cursors = model.Resource.get_dbs(
#     model.Resource.query(model.Resource.hotness > 0),
#     limit=20, prev_cursor=True, order='-hotness')
#   return flask.render_template(
#     'resource/resource_grid.html',
#     html_class='resource-grid',
#     title=u'تصفح الصور',
#     resource_dbs=resource_dbs,
#     next_url=util.generate_next_url(cursors.get('next')),
#     prev_url=util.generate_next_url(cursors.get('prev')),
#     api_url=flask.url_for('api.resource.list'),
#   )


# ###############################################################################
# # View
# ###############################################################################
# @app.route('/resource/<int:resource_id>/', endpoint='resource_view')
# def resource_view(resource_id):
#   resource_db = model.Resource.get_by_id(resource_id)
#   if not resource_db:
#     return flask.abort(404)
#   user_db = resource_db.user_key.get()
#   return flask.render_template(
#     'resource/resource_view.html',
#     html_class='resource-view',
#     title='%s' % (resource_db.name),
#     resource_db=resource_db,
#     user_db=user_db,
#     api_url=flask.url_for('api.resource', key=resource_db.key.urlsafe()),
#   )


###############################################################################
# Update
###############################################################################
class FilterUpdateForm(flask_wtf.FlaskForm):
  label = wtforms.TextField(u'عنوان الفلتر', [wtforms.validators.required()])
  filter_property = wtforms.TextField(u'اسم الخاصية', [wtforms.validators.required()])
  filter_value = wtforms.TextField(u'قيمة الخاصية', [wtforms.validators.required()])
  description = wtforms.TextAreaField(u'وصف الفلتر', [wtforms.validators.optional()])


@app.route('/admin/filter/create/', methods=['GET', 'POST'])
@app.route('/admin/filter/<string:filter_id>/update/', methods=['GET', 'POST'], endpoint='filter_update')
@auth.admin_required
def filter_update(filter_id=''):
  if filter_id:
    filter_db = model.Filter.get_by_id(filter_id)
  else:
    filter_db = model.Filter(
      id='{}-{}'.format(util.param('filter_value'), util.param('filter_value')),
      label='')

  if not filter_db or not auth.current_user_db().admin:
    return flask.abort(404)

  form = FilterUpdateForm(obj=filter_db)
  if form.validate_on_submit():
    form.populate_obj(filter_db)
    filter_db.put()
    return flask.redirect(flask.url_for('admin_filter_list'))

  return flask.render_template(
    'filter/filter_update.html',
    html_class='filter-update',
    title='%s' % (filter_db.label or 'فلتر جديد'),
    filter_db=filter_db,
    form=form,
    api_url=flask.url_for('api.filter', key=filter_db.key.urlsafe()) if filter_db.key else '',
  )


###############################################################################
# Admin Filters List
###############################################################################
@app.route('/admin/filter/', endpoint='admin_filter_list')
@auth.admin_required
def admin_filter_list():
  filter_dbs, cursors = model.Filter.get_dbs(
    limit=30, prev_cursor=True, order='-photos_count')

  return flask.render_template(
    'filter/filter_list.html',
    html_class='filter-list',
    title=u'قائمة الفلاتر',
    filter_dbs=filter_dbs,
    next_url=util.generate_next_url(cursors.get('next')),
    prev_url=util.generate_next_url(cursors.get('prev')),
    api_url=flask.url_for('api.filter.list'),
  )
