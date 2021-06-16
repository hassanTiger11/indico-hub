# from marshmallow import Schema
# from webargs import fields


# TODO: Implement Marshmallow schemas for the API request data

from flask_marshmallow import *
from marshmallow import *
from marshmallow_sqlalchemy import *
from webargs.core import T
from .models import *
"""
payload = {
        'url': BASE_URL,
        'contact': contact,
        'email': email,
        'organization': "it"
    }
"""
class instanceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Instance
        include_relationships = True
        include_fk = True
        load_instance = True

class validationSchema(Schema):
    uuid = fields.String(required=True)
    enabled = fields.Boolean(required=True)
    url = fields.String(required=True)
    contact = fields.String(required=True)
    email = fields.Email(required=True)
    organization = fields.String(required=True)
    crawl_date = fields.DateTime()
    #crawled_data = db.Column(JSONEncodedDict)
    #geolocation = db.Column(JSONEncodedDict)
    registration_date = fields.DateTime(required=True)

    @post_load
    def createInstance(self, data, **kwargs):
        return Instance(**data)

class UpdateInstance(Schema):
    enabled = fields.Boolean()
    url = fields.String()
    contact = fields.String()
    email = fields.Email()
    organization = fields.String()
