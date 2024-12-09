import os
from decouple import config

class Config:
    SECRET_KEY = config('SECRET_KEY', default='dev')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CMC_API_KEY = config('CMC_API_KEY')
    EMAIL_USER = config('EMAIL_USER')
    EMAIL_PASSWORD = config('EMAIL_PASSWORD')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = config('DATABASE_URL', default='').replace('postgres://', 'postgresql://')

config_by_name = dict(
    dev=DevelopmentConfig,
    prod=ProductionConfig
)
