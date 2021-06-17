import click
from flask import Blueprint, abort, current_app, json, jsonify
from webargs.flaskparser import use_kwargs

from .app import register_spec
from .db import db
from .models import Instance
from .schemas import InstanceSchema, UpdateInstance, ValidationSchema


#
api = Blueprint('api', __name__, cli_group=None)


@api.cli.command('openapi')
@click.option(
    '--json',
    'as_json',
    is_flag=True,
)
@click.option(
    '--test',
    '-t',
    is_flag=True,
    help='Specify a test server (useful for Swagger UI)',
)
@click.option('--host', '-h')
@click.option('--port', '-p')
def _openapi(test, as_json, host, port):
    """Generate OpenAPI metadata from Flask app."""
    with current_app.test_request_context():
        spec = register_spec(test=test, test_host=host, test_port=port)
        # TODO: Register all the exposed view functions here.
        #       Don't worry about this at the beginning though!
        # spec.path(view=...)
        spec.path(view=register)
        spec.path(view=update_instance)
        spec.path(view=get_instance)
        if as_json:
            print(json.dumps(spec.to_dict()))
        else:
            print(spec.to_yaml())


# TODO: Implement the API endpoints here
@api.route('/api/instance', methods=['POST'])
@use_kwargs(ValidationSchema, location='json')
def register(
    uuid, enabled, url, contact, email, organization, crawl_date, registration_date
):
    """
    mock function for registering an instance to the database
    ---
    parameters:
        Instance.get_json()
    responses:
          201:
            description: instance registered
          404:
            description: instance is already registered
    """
    inst = Instance().query.filter_by(uuid=uuid).first()
    if inst:
        current_app.logger.exception('register: This instance is already registered')
        abort(401, description='BAD_REQUEST')
    inst = Instance(
        uuid=uuid,
        enabled=enabled,
        url=url,
        contact=contact,
        email=email,
        organization=organization,
        crawl_date=crawl_date,
        registration_date=registration_date,
    )
    db.session.add(inst)
    db.session.commit()
    return InstanceSchema().dumps(inst), 201


@api.route('/api/instance/<string:uuid>', methods=['PATCH', 'POST'])
@use_kwargs(UpdateInstance, location='json')
def update_instance(uuid, **kwargs):
    """
    updates information regarding the instance
    ---
    parameters:
        -enabled
        -url
        -contact
        -email
        -organization
    responses:
        200: updated instance
        400: missing argument | bad_url | Instance doesn't exist
    """
    if uuid is None:
        abort(400, description='BAD_URL')
    inst = Instance().query.filter_by(uuid=uuid).first()
    if inst is None:
        abort(404, description='BAD REQUEST')
    for attr in kwargs:
        setattr(inst, attr, kwargs[attr])
    db.session.commit()
    return jsonify(InstanceSchema().dump(inst))


@api.route('/api/instance/<string:uuid>', methods=['GET'])
def get_instance(uuid):
    instance = Instance().query.filter_by(uuid=uuid).first()
    if instance is None:
        abort(404, description='instance not found')
    rv = jsonify(InstanceSchema().dump(instance))
    rv.headers['Access-Control-Allow-Origin'] = '*'
    return rv


@api.route('/all')
def all():
    all = Instance().query.all()
    schema = InstanceSchema(many=True)
    return jsonify(schema.dump(all)), 200
