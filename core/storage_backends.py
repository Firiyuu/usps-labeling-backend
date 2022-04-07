from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'


class PrivateMediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'private'
    custom_domain = False


class PublicMediaStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'
