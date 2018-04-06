import os

from django.core.exceptions import ValidationError


def validate_file_extension(value, valid_extensions):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Неподдерживаемый формат файла! Разрешены: %s' % valid_extensions)


def validate_photo_file_extension(value):
    valid_extensions = ['.jpg', 'jpeg']
    validate_file_extension(value, valid_extensions)


def validate_audio_file_extension(value):
    valid_extensions = ['.mp3', 'ogg', 'wav']
    validate_file_extension(value, valid_extensions)
