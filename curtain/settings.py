
import os   #static path를 위해
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-k+=(x9e#b%wxk1p*@$u%s%sa=kc2q8qs7ra@%d@&f#l&*-ybnv'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# 네이버맵 CLIENT_ID Setting
NAVER_MAP_CLIENT_ID = config('NAVER_MAP_CLIENT_ID')

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '0.0.0.0',
    '10.138.51.172',  # cmd ipconfig address
    '54.180.195.59', # AWS EC2 Public IP
    '갓파더위크.kr',
    'www.갓파더위크.kr',
    'xn--739ap1l9xrh1i6id.kr',
    'www.xn--739ap1l9xrh1i6id.kr',

]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
]

#추가되는 앱을 넣는 곳
INSTALLED_APPS += [
    #'main.apps.MainConfig',
    'main',
    #Rest framework and CORS
    'rest_framework',
    'corsheaders',
    #'manager.apps.myappConfig',
    'manager',
    #'customer.apps.MemberConfig',
    'customer',
    #'contract.apps.partBoardConfig',
    'contract',
    #'construction.apps.placeBoardConfig',
    'construction',
]

#Rest framework config
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    )

}

MIDDLEWARE = [
    #COR 설정
    'corsheaders.middleware.CorsMiddleware',
    #default 설정
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# 신뢰할 수 있는 출처 [갓파더위크.kr]
CSRF_TRUSTED_ORIGINS = [
    'https://xn--739ap1l9xrh1i6id.kr',
    'http://xn--739ap1l9xrh1i6id.kr',
    'https://갓파더위크.kr',
    'http://갓파더위크.kr',
]

# HTTPS 및 보안 관련 설정
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

ROOT_URLCONF = 'curtain.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # 템플릿 디렉토리 경로 설정
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media', #이미지 관련
            ],
        },
    },
]

WSGI_APPLICATION = 'curtain.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

'''
#default SQL 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
'''
#config 이용해서 key와 password 숨기기
# - pip install python-decouple 실행
# -app과 같은 level에서 setting ini 파일을 만들고 설정



SECRET_KEY = config('DJANGO_SECRET_KEY')
#PostgreSQL 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'Curtain' ,
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',

    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'manager.Manager'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
# ModelBackend는 AUTH_USER_MODEL 설정을 기반으로 인증을 시도합니다.
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'

# 정적 파일 디렉토리 설정
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# 정적 파일을 수집할 디렉토리 설정
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

#Media 설정
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


