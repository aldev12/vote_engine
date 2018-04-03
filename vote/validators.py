import os
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.mp3', 'ogg', 'wav', '.jpg', 'jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Неподдерживаемый формат файла! Разрешены: .jpg, .jpeg, .mp3, .ogg, .wav')
