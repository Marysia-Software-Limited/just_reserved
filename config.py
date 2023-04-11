import os

from beret_utils import get_config
from beret_utils.config import bool_value, EnvValue
from beret_utils import PathData

base_dir = PathData.main()
assets_dir = base_dir("assets")

DEFAULT_CONFIG = (
    ('PROJECT_NAME', 'just_reserved'),
    ('PROJECT_ENV', 'local'),
    ('POSTGRES_ENGINE', 'django.db.backends.postgresql'),
    ('POSTGRES_DB', 'postgres'),
    ('POSTGRES_USER', 'postgres'),
    ('POSTGRES_PASSWORD', 'postgres'),
    ('POSTGRES_HOST', 'db'),
    ('POSTGRES_PORT', ''),
    ('SECRET_KEY', "django-insecure-aj#exo2bw$h%ps^hr4o+ch)e_u2ao1j19rd6z0q)l1o#e!9rn5"),
    ('DJANGO_EMAIL_HOST_USER', 'just_reserved@marysia.app'),
    ('DJANGO_EMAIL_HOST_PASSWORD', 'key'),
    ('DEEP_AI_API_KEY', 'api-key'),
    ("DJANGO_ALLOWED_HOSTS", "ala.hipisi.org.pl eskape.marysia.app localhost 94.23.247.130 0.0.0.0 127.0.0.1 hipisi.org.pl"),
    ('OPENAI_KEY', 'api-key'),
    ('OPENAI_ORG', 'marysia'),
 )

ENV_FILES = (
    '.local.env',
    '.env',
)

Config = get_config(DEFAULT_CONFIG, ENV_FILES)
config = Config()

if __name__ == '__main__':
    for key, value in config.items():
        print(f"{key}={value}")
