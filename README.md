# Athletics sports club

This project is a web application that mimics, at very small scale, an athletics club for kids, to be used by students to learn:

1. How to securely deploy web applications into production environments using a CI/CD pipeline.
2. How to create front-end web applications that use a REST API as back-end.

It follows the [twelve-factor app methodology](https://www.12factor.net/), up to a certain point.

> If you are somewhat familiar with web frameworks but not with Django, [this roadmap](https://roadmap.sh/django) can help you land the necessary conceps.

## Tech stack

This project is a headless application using Django Ninja, split into different applications, making use of the following components:

* The model, using [Django's ORM](https://docs.djangoproject.com/en/stable/topics/db/models/).
* A [PostgreSQL](https://postgresql.org/) database to store data.
* A private back-office using [Django's admin panel](https://docs.djangoproject.com/en/stable/ref/contrib/admin/), for internal use, to manage application settings and browse and modify data.
* [Django Ninja](https://django-ninja.dev/) to create the REST API (using Pydantic for validations).
* [NGINX](https://nginx.org/) as reverse proxy and load balancer.
* [Docker Compose](https://docs.docker.com/compose/) to define and manage the containerised services.

To keep things simple, access to the database and tests will not use asynchronous methods. Moreover, the application neither includes authentication nor authorisation.

> Each student can fork the project on Github so that he or she can start making modifications.

## Security

A CI/CD pipeline is a security-enabling framework, serving as the backbone for *DevSecOps*, some of its benefits being:

* Automated security integration.
* Reduced human error.
* Faster patching.

> Most of [the twelve factors](https://www.12factor.net/) are used in this example repository, therefore can be used to teach good security practices.

Via the application in this repository, not only can students learn how to securely build a CI/CD pipeline, but also security concepts related to web applications, such as:

* `Auditory` base class that includes auditory attributes and methods. To keep it simple, it supports soft-deletion and restoration, and datetimes for creation, modification and deletion of records. In a production environment, it would have to support more auditory attributes, to keep track of which user performed which operation, and GDPR methods, e.g., anonimisation and purging.
* Use of `environment variables` to store configuration, via the `.env` file and the `environ` package.
* Execution of application as stateless process.
* Strict separation of build and run stages.
* Explicit declaration and isolation of dependencies (the default `requirements.txt` file does not abide by this rule on purpose, so students can correct that).
* Keeping development and production as similar as possible.
* Maximize robustness with fast startup and graceful shutdown.
* CORS Headers.
* Public ID separate from internal ID (primary key).
* Validation of input data via schemas.

> Authentication is enabled in the admin panel using cookie-based sessions, but the endpoints do not support any form of authentication, e.g., bearer tokens or JSON Web Tokens, which will be added in a future version.

Regarding security integration in the CI pipeline, this application does only linting using the [Ruff](https://docs.astral.sh/ruff/) library. Students are meant to add additional jobs that run more security tools, such as:

* Bandit. A tool designed to find common security issues in Python code by processing the Abstract Syntax Tree (AST) to find events like SQL injection, XSS, or weak cryptography usage.
* Safety. A dependency checker that scans your installed packages (via `requirements.txt` or environment) and compares them against a known database of vulnerabilities and malicious packages.
* TruffleHog. A scanner that searches through your git history and file system for high-entropy strings and secrets, such as AWS keys, database passwords, and API tokens.
* Semgrep. A fast, open-source static analysis tool that finds bugs and enforces code standards using logic that looks like the code you are writing; excellent for custom security rules.
* Django Deployment Check. Django’s built-in command (`python manage.py check --deploy`) that validates your project settings against a checklist of production security best practices (e.g., `DEBUG` status, SSL config).
* Pip-audit. An official tool from the Python Packaging Authority (PyPA) that scans Python environments for packages with known vulnerabilities using the Open Source Vulnerability database.
* CodeQL. GitHub's semantic code analysis engine that treats code as data, allowing you to query for security vulnerabilities and bugs; it is the engine behind GitHub Advanced Security.
* SonarCloud. A comprehensive platform that provides continuous inspection of code quality to detect bugs, code smells, and security vulnerabilities across the entire codebase.
* Gitleaks. A lightweight, fast, and open-source tool specifically designed to detect hardcoded secrets like passwords, API keys, and tokens in your git repositories.

## Additional concepts

Additional concepts that can be taught using this repository are:

* Blue/Green deployments.
* Makefile to automate tasks.

## The model

This is the list of models or entities it has, with a  brief description of each one:

* `Auditory`: a base class that includes auditory attributes and methods.
* `Person`: a base class that includes basic attributes of a person, used by athletes and coaches.
* `Address`: a weak entity that stores postal addresses, used by athletes, coaches and venues.
* `Venue`: locations where sports are practised. Uses an `ENUM` to type them (see below).
* `Athlete`: people practising sports.
* `Coach`: people training athletes.
* `Activity`: a scheduled activity. Uses polymorphism to have `Competition` and `Training`.

The following disciplines are supported (from all the practised ones):

* Sprints. Short-distance races, typically from 60 to 100 metres, focused on maximum speed.
* Long-distance running. Races over 500 metres or more, testing endurance and stamina.
* Relays. Team races where runners pass a baton, combining speed and coordination.
* High jump. Athletes leap over a horizontal bar without knocking it down.
* Long jump. Athletes sprint and jump into a sandpit, aiming for maximum distance.

## Apps

The project has four apps, and models are spread among them:

| App          | Models                                |
|--------------|---------------------------------------|
| `core`       | `Address`, `Auditory`                 |
| `inventory`  | `VenueType`, `Venue`                  |
| `people`     | `Person`, `Athlete`, `Coach`          |
| `scheduling` | `Activity`, `Competition`, `Training` |


## Structure of each app

We will slightly modify the default structure of each app so that:

| Module  | Default location | New location | Notes                                |
|---------|------------------|--------------|--------------------------------------|
| Admin   | `admin.py`       | `admin/`     | One file per entity                  |
| Models  | `models.py`      | `models/`    | One file per entity                  |
| API     |                  | `api/`       | One file per entity                  |
| Schemas |                  | `schemas/`   | One file per entity                  |
| Tests   | `tests.py`       | `tests/`     | One file per type of test and entity |

Taking `core` as an example, we will end up with this structure:

```
sportsclub/
└── core
    ├── admin.py
    ├── apps.py
    ├── __init__.py
    ├── migrations
    │   └── __init__.py
    ├── models.py
    │   ├── __init__.py
    │   ├── address.py
    │   ├── audit.py
    │   └── managers.py
    ├── tests
    │   ├── __init__.py
    │   ├── test_api_addresses.py
    │   ├── test_models_address.py
    │   ├── test_models_audit.py
    │   ├── test_models.py
    │   └── test_schemas.py
    └── views.py
```

> Acceptance tests will be dealt with later on.

## Auditory base class

Having auditory fields is very common and best handled using an abstract class, which we will name `Auditory` and define in the `core/models/auditory.py` file. This class will have three attributes, all of type `models.DateTimeField`:

* `created_at`, to store the date the record was created. Automatically set, it cannot be modified.
* `updated_at`, to store the date the record was last updated. Automatically set, it changes with the record.
* `deleted_at`, to store the date the record was deleted. Automatically set, this implement soft delete, meaning the record is not physically deleted, but logically.

For this to work, we also need to implement `soft_delete()` and `restore()` methods. Moreover, we will also implement a `SoftDeleteManager` class in the `core/models/managers.py` file, which will help us query the database automatically excluding soft-deleted records.

> To keep it simple, this `Auditory` class will not support a three-tier deletion strategy.

Other models will simply inherit from this base class in order to get the auditory fields automatically:

```python
class Venue(Auditory):
    [..]
```

In a more advanced scenario, if we were to meet the requirements set by GDPR and similar laws, we would also be implementing attributes and methods to anonymise and purge records, and we would keep track of which user performed which operation. 

Advantages of using base classes in Django's ORM:

* Avoids code duplication, as fields and methods are shared.
* No additional tables, as each subclass becomes its own database table.

## Person base class

In the `people` app we define the abstract, or base, class `Person`, which is then used by the `Athlete` and `Coach` entities. This class will have four attributes:

* `first_name`, to store the first name of the person.
* `last_name`, to store the last name of the person.
* `email`, to store the e-mail address of the person.
* `phone`, to store the phone number of the person, using international format, e.g., `+34.<number>`.

It will inherit from the `Auditory` class, so the auditory fields will already be present in the `Athlete` and `Coach` models.

## VenueType class

Venue is a broad term that encompasses any location where an activity takes place. Venues can be of type:

* `Stadium`: Used for competitions, often featuring an outdoor track and field events with spectator seating.
* `Gymnasium`, or Gym: Used for indoor training sessions.
* `Track`: Used for both training and competition in running events and relays.
* `Field`: The open area within a stadium or track facility where field events (e.g., long jump) are held.

We will define the `VenueType` class in the `inventory/models/venue.py` file, to be used in the `Venue` model, using the `models.TextChoices` base class, which inherits from `enum.ENUM`.

Django Admin automatically generates a dropdown menu for `venue_type`, so we can filter and query easily.

## Polymorphism

Taking the `Activity` entity as example, we can see that it is typed:

* `Training`. A practice session aimed at skill development. Has coaches, participants, and a focus area.
* `Competition`. A competitive event with athletes and coaches, usually with a score result.

We will model this using *abstract base class inheritance* for each activity type:

```python
class Activity(Auditory):
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    coaches = models.ManyToManyField(Coach, blank=True)
    athletes = models.ManyToManyField(Athlete, blank=True)

    class Meta:
        abstract = True
        ordering = ["-date"]

    def __str__(self):
        return f"{self.name} ({self.date.strftime('%Y-%m-%d')})"

class Training(Activity):
    focus = models.CharField(
        max_length=255, blank=True, help_text="Main focus of the training session"
    )

class Competition(Activity):
    score = models.JSONField(blank=True, null=True, help_text="Aggregate score summary")
```

Conceptual differences between using a single table with an ENUM and using abstract base class inheritance:

| Aspect                | Single table and ENUM                            | Abstract base class inheritance                               |
|-----------------------|--------------------------------------------------|---------------------------------------------------------------|
| Data shape            | All entities share identical columns             | Each subtype has its own table with shared and unique columns |
| Querying              | Filter by `type`                                 | Query each subclass separately                                |
| Flexibility           | Easy to add new types, but all share same schema | New subclasses can have unique schema                         |
| Performance           | Simple, single-table queries                     | No JOINs needed; each subclass is independent                 |
| Normalization         | Less normalized (fields unused for some types)   | Fully normalized                                              |
| Schema changes        | Changing one model affects one table             | Each subclass has its own migrations                          |
| API/UI representation | Same serializer/view for all types               | Different serializers/views per subclass                      |
| Teaching value        | Easier for beginners                             | Demonstrates inheritance and code reuse                       |
| Use case              | Simple typed entity                              | True object hierarchy (e.g. `Competition`, `Training`)        |

With abstract base class inheritance, the parent class (`Activity`) does not create a database table. Instead, each child class (`Competition`, `Training`) gets its own table containing all fields from both the parent and child.

```python
# Each subclass has its own table and queryset
trainings = Training.objects.all()
competitions = Competition.objects.all()

# You cannot query Activity directly (it's abstract)
# Activity.objects.all()  # This would raise an error
```

Each subclass can:

* Have its own fields (e.g. `score` for Competition, `focus` for Training).
* Have its own business logic and methods.
* Be exposed via its own serializer or endpoint (e.g., `/api/v1/competitions/`, `/api/v1/trainings/`).

This fits real-world domains where `Activity` is an abstract concept, but `Competition` and `Training` are *distinct business entities* that happen to share common attributes.

Practical effects of inheritance:

* **In the database**, each subclass has its own table with all inherited fields plus its own specific fields. No JOINs are needed.
* **In the UI**, each subclass can have its own form, admin view, or template, avoiding conditional logic.
* **In the ORM**, each model can override methods and define its own constraints while sharing common field definitions.
* **In the API layer**, we have different endpoints and schemas per subtype (`/api/v1/competitions/`, `/api/v1/trainings/`). Common fields are defined once in the base class but each subtype has its own serializer.

```python
  # Base schema with common fields (defined in Activity)
  class ActivityOut(Schema):
      public_id: str
      name: str
      date: datetime
      venue: VenueOut | None
      season: SeasonOut
      coaches: list[CoachOut]
      athletes: list[AthleteOut]

  # Subclass schemas add their specific fields
  class TrainingOut(ActivityOut):
      focus: str

  class CompetitionOut(ActivityOut):
      score: dict | None
```

* **Querying** is straightforward since each subclass is independent:
```python
  # Get all trainings for a season
  Training.objects.filter(season__name="Temporada 2025")

  # Get all competitions at a venue
  Competition.objects.filter(venue__name="Estadi Atlètic Son Moix")

  # Get upcoming activities requires querying both
  from itertools import chain
  upcoming = sorted(
      chain(
          Training.objects.filter(date__gte=now),
          Competition.objects.filter(date__gte=now),
      ),
      key=lambda x: x.date
  )
```

### Abstract vs Multi-table Inheritance

Django supports two forms of model inheritance:

| Aspect              | Abstract Base Class (`abstract = True`)          | Multi-table Inheritance                          |
| ------------------- | ------------------------------------------------ | ------------------------------------------------ |
| Parent table        | No table created                                 | Parent table is created                          |
| Child tables        | Each child has all fields                        | Child tables link to parent via foreign key      |
| Querying parent     | Not possible                                     | Returns all subclass instances                   |
| Performance         | Faster (no JOINs)                                | Slower (requires JOINs)                          |
| Polymorphic queries | Must query each subclass separately              | Can query parent to get all types                |
| Use case            | Code reuse without shared table                  | True polymorphism with unified querying          |

We chose abstract base class inheritance for `Activity` because:

1. `Competition` and `Training` are queried and managed separately in the API.
2. No need for a unified "all activities" query in our use case.
3. Better performance without JOIN overhead.
4. Simpler database schema and fixtures.

If you needed to query all activities together (e.g., a calendar showing both trainings and competitions), multi-table inheritance would be more appropriate, allowing `Activity.objects.all()` to return mixed results.

## Installation

Start with system requirements:

```bash
# Install system requirements
sudo apt-get install --yes curl jq python3-venv
```

Continue by creating the project directory, then create and activate the virtual environment, and upgrade the `pip` package:

```bash
# Create project directory
mkdir --parents ~/Projects/sportsclub

# Create and activate virtual environment
python3 -m venv ~/Projects/sportsclub/.venv
source ~/Projects/sportsclub/.venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

Finally, create a `requirements.txt` file with our Python packages, and use `pip` to install them into the virtualenv:

```bash
# Create the requirements.txt file
tee ~/Projects/sportsclub/requirements.txt << EOF
django-cors-headers
django-environ
django-json-widget
django-nanoid-field
django-ninja
django-ratelimit
pydantic[email]
psycopg[binary,pool]
whitenoise
EOF

# Install the requirements
pip install --requirement requirements.txt
```

We are now ready to create the Django project:

```bash
cd ~/Projects/sportsclub
django-admin startproject sportsclub
```

You project folder will look like:

```
sportsclub/
├── manage.py
└── sportsclub/
    ├── asgi.py
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

> We will be serving static contents using [Whitenoise](https://whitenoise.readthedocs.io/en/stable/django.html), a Python library designed to simplify static file serving for WSGI-compatible web applications.

## Settings

Let's create a `.env` file in the project root, using the `.env.example` file as reference. This is the standard convention and will serve as a single source of truth throughout our project (Django, Docker Compose, CI/CD, shell scripts, etc.):

```bash
cp .env.example .env
```

Customise the values in the `.env` file to your needs.

Edit the `sportsclub/settings.py` file and configure the `django-environ` package. The following code has been adapted from the [quick start guide of Django Environ](https://django-environ.readthedocs.io/en/latest/quickstart.html).

```python
# sportsclub/settings.py
from pathlib import Path

import environ

# Initialise environ.Env class with type casting rules and default values for environment variables
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)

# Set the project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
environ.Env.read_env(BASE_DIR.parent / ".env")
```

We can now load the variables from the `.env` file, with default packages to make the pipeline less complicated:

```python
SECRET_KEY = env("SECRET_KEY", default="insecure-build-time-key")
DEBUG = env("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
ADMINS = env.list("ADMINS", default=[])
MANAGERS = env.list("MANAGERS", default=[])
SERVER_EMAIL = env("SERVER_EMAIL", default="root@localhost")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="webmaster@localhost")
```

Next, in the same `sportsclub/settings.py` file, configure now the applications:

```python
INSTALLED_APPS = [
    # Default Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "corsheaders",
    "django_json_widget",
    "nanoid_field",
    "ninja",
]
```

Only packages that provide Django-specific functionality (models, admin, middleware, template tags, management commands) need to be in `INSTALLED_APPS`:

* `django-environ` is a configuration utility that runs at settings load time and parses environment variables.
* `django-ratelimit` works purely through decorators (e.g., `@ratelimit`) that we apply directly to our views.

A special case is `django-ninja`. For a development environment, we do not need to add `ninja` to the list of installed apps because it works by mounting its API directly in the `urls.py` file. However, if we want the interactive Swagger/OpenAPI documentation to work properly with static files in production, we may need `ninja` in `INSTALLED_APPS` so that `collectstatic` picks up its static assets.

In the same `sportsclub/settings.py` file, configure now the middlewares:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

In the same file, also configure the PostgreSQL database:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="sportsclub"),
        "USER": env("POSTGRES_USER", default="sportsclub"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="sportsclub"),
        "HOST": env("POSTGRES_HOST", default="localhost"),
        "PORT": env("POSTGRES_PORT", default="5432"),
    }
}
```

In the same file, configure the Nano ID options, too:

```python
# NanoidField from django-nanoid-field
NANOID_SIZE=12
NANOID_ALPHABET='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
```

And the CORS options:

```python
# CORS options from django-cors-headers

# Development: Allow all origins
CORS_ALLOW_ALL_ORIGINS = True

# Production: Specific origins
# CORS_ALLOWED_ORIGINS = [
#     "https://sportsclub.com",
#     "https://app.sportsclub.com",
# ]
```

Note that the default time zone is UTC, which is just fine:

```python
TIME_ZONE = 'UTC'
```

Finally, the static files directives when using Whitenoise:

```python
# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

> We will use the local disk for media and static files for the time being.

## Applications

Django supports multiple apps. Business areas, or domains, are meant to be split into apps. There is not a one size fits all approach to this, but basic principles would be:

* Single responsibility. Each app should have a clear purpose.
* Future growth. Leave room for domain-based apps.
* Logical grouping. Related models should live in the same app.

Based on domain-driven design principles, an app structure for the project could be:

| Django app   | Purpose                                | Example entities             |
| ------------ | ---------------------------------------|------------------------------|
| `core`       | Common utilities and abstract models   | `Auditory`, `Address`        |
| `people`     | Humans entities                        | `Person`, `Athlete`, `Coach` |
| `inventory`  | Facility and inventory management      | `Venue`, `Equipment`         |
| `scheduling` | Time-based organisation                | `Season`, `Team`, `Activity` |

> `Activity` includes its subclasses `Training` and `Competition`.

We will create the applications with the following commands:

```bash
cd ~/Projects/sportsclub/sportsclub
python manage.py startapp core
python manage.py startapp inventory
python manage.py startapp people
python manage.py startapp scheduling
```

The resulting directory structure of the `core` app should look like this:

```
sports_club/
└── core
    ├── admin.py
    ├── apps.py
    ├── __init__.py
    ├── migrations
    │   └── __init__.py
    ├── models.py
    ├── tests.py
    └── views.py
```

> Apps `inventory`, `people`, and `scheduling` will have the same content as `core`.

Edit the `sportsclub/settings.py` file and configure the newly-created apps:

```python
INSTALLED_APPS = [
    [..]

    # Our apps
    'core',
    'inventory',
    'people',
    'scheduling',
]
```

For apps with just one entity, we will:

* Edit the `admin.py` file to register the entity with the `admin` module.
* Create the `api.py` file to define the endpoints for the entity.
* Edit the `models.py` file to define the entity class.
* Create the `schemas.py` file to define the Pydantic schemas used for request/response validation and serialisation.

For such apps with more than one entity, we will not create such files, and delete the existing ones and, instead, we will create the following directories:

* `admin/`, to register the entities with the `admin` module.
* `api/`, to define the endpoints of the multiple entities.
* `models/`, to define the model classes.
* `schemas/,` to define the validation schemas.

Regarding the `tests.py`file, in any case we will delete it and create the `tests/` directory, where we will place multiple files with unit, integration and acceptance tests. Even with just one entity we will have multiple test files.

## Model

We would now edit the `models.py` file in each app to define the models. However, we do not want to put all our models into a single, big file, but split them into separate files. Therefore we will create a module named `models/` (with an `__init__.py` file inside) and several Python files, one per model:

```bash
cd ~/Projects/sportsclub/sportsclub
rm core/models.py
mkdir --parents core/models
```

We will follow the same pattern in all apps, even if they only have one model. The end result will look like this:

| App        | File                    | Entities                     |
|------------|-------------------------|------------------------------|
| core       | `models/__init__.py`    |                              |
| core       | `models/address.py`     | Address                      |
| core       | `models/auditory.py`    | Auditory                     |
| core       | `models/enums.py`       | Discipline                   |
| core       | `models/managers.py`    | SoftDeleteManager            |
| inventory  | `models/venue.py`       | Venue, VenueType             |
| people     | `models/__init__.py`    |                              |
| people     | `models/athlete.py`     | Athlete                      |
| people     | `models/coach.py`       | Coach, CoachingCertification |
| people     | `models/person.py`      | Person                       |
| scheduling | `models/__init__.py`    |                              |
| scheduling | `models/activity.py`    | Activity                     |
| scheduling | `models/competition.py` | Competition                  |
| scheduling | `models/season.py`      | Season                       |
| scheduling | `models/training.py`    | Training                     |

### Models module

We will be creating the `core/models/__init__.py` file that indicates that the directory is to be treated as a package, allowing it to be imported:

```python
# core/models/__init__.py
"""Managers and models for the core app."""
from .managers import SoftDeleteManager
from .auditory import Auditory
from .address import Address


__all__ = [
    'SoftDeleteManager',
    'Auditory',
    'Address',
]
```

This `__init__.py` file imports specific classes defined in other modules from within the same package and uses `__all__` to explicitly define that these are the only names that should be imported when someone uses `from core.models import *`.

The rest of apps will follow a similar pattern.

### Auditory base class

The `Auditory` class is a reusable base class that gives any model:

* Automatic timestamps: `created_at` and `updated_at` tracked without extra code.
* Soft deletion: records are marked deleted rather than removed from the database.
* Consistent interface: all models share the same deletion and restore behaviour.

Any model inheriting from `Auditory` gets these features automatically.

Let's define this base class by creating a `core/models/auditory.py` file with the following content:

```python
# core/models/auditory.py
from django.db import models
from django.utils import timezone

from .managers import SoftDeleteManager


class Auditory(models.Model):
    """
    Base class for auditory fields with support for soft-deletion.
    It does not implement anonymisation or purging of records.
    It does not keep track of which user last performed a given operation.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Default manager that excludes soft-deleted records
    objects = SoftDeleteManager()

    # Manager to access all records including soft-deleted
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark record as deleted without removing from database."""

        self.deleted_at = timezone.now()
        self.save(
            update_fields=["deleted_at", "updated_at"]
        )

    def restore(self):
        """Restore a soft-deleted record."""

        self.deleted_at = None
        self.save(
            update_fields=["deleted_at", "updated_at"]
        )

    # Query Helpers
    @classmethod
    def get_soft_deleted(cls):
        """Get only soft-deleted records."""
        return cls.all_objects.filter(
            deleted_at__isnull=False
        )

    # Properties
    @property
    def is_soft_deleted(self):
        """Check if record is soft deleted."""
        return self.deleted_at is not None
```

> Instance methods `soft_delete()` and `restore()` operate on a single, specific record, whereas class method `get_soft_deleted()` operate on the model class (i.e., the table) itself, returning a `queryset`.

By default we access active objects only, but we can still access all objects, i.e., including soft-deleted. And we can restore them, too:

```python
athletes = Athlete.objects.all()                # Only active athletes are returned
all_athletes = Athlete.all_objects.all()        # Includes soft-deleted
athlete.soft_delete()                           # Soft delete an athlete
Athlete.objects.filter(id=athlete.id).exists()  # False
athlete.restore()                               # Restore a soft-deleted athlete
Athlete.objects.filter(id=athlete.id).exists()  # True
```

### Soft-delete manager

Django models have a default `objects` manager. A manager is the interface through which Django models interact with the database. Every time we query the database, we are using a manager. Managers let us customise or extend query behavior.

In our case, we want to exclude soft-deleted records from the query. For that, we will define a `SoftDeleteManager` that overrides the default `queryset` behaviour. Let's define it by creating the `core/models/managers.py` file with the following code:

```python
# core/models/managers.py
"""Custom model managers for the core app."""
from django.db import models


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects by default."""
    
    def get_queryset(self):
        """Return queryset excluding soft-deleted records."""
        return super().get_queryset().filter(deleted_at__isnull=True)
```

This `SoftDeleteManager` overrides the default queryset behavior. Instead of actually deleting records from the database, "soft delete" sets a `deleted_at` timestamp. The `manager` ensures that soft-deleted records are automatically excluded from normal queries.

### Model classes

Whenever we do not need an entity to be audited, we can inherit directly from the `models.Model` base class. However, when we want an entity to be audited, we will inherit from the base class `Auditory`.

```python
# core/models/address.py
class Address(Auditory):
    """A postal address."""

    id = models.BigAutoField(primary_key=True)
    public_id = NanoidField(unique=True, editable=False, db_index=True)
    line1 = models.CharField(max_length=255)
    [..]
```

Moreover, inheritance can be chained. For example, we can define the base class `Person` that inherits from it, then have the `Athlete` and `Coach` entities inherit from `Person`.

```python
# people/models/person.py
class Person(Auditory):
    """Base class for people."""

    id = models.BigAutoField(primary_key=True)
    public_id = NanoidField(unique=True, editable=False, db_index=True)
    first_name = models.CharField(max_length=100)
    [..]

# people/models/athlete.py
class Athlete(Person):
    """People practising sports."""

    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    jersey_number = models.IntegerField(null=True, blank=True)
```

All entities described at the beginning of this section will follow these patterns.

## Migrations

Once all model classes have been defined, we are ready to generate the migrations files and apply them:

```bash
cd ~/Projects/sportsclub/sportsclub
python manage.py makemigrations core
python manage.py makemigrations inventory
python manage.py makemigrations people
python manage.py makemigrations scheduling
python manage.py migrate
```

Django analyzes all apps, determines dependencies, and creates migrations in the correct order. For most cases, this works perfectly. Should we have circular or complex dependencies between apps, Django might get confused about the order. Creating them explicitly ensures the dependency chain is correct.

> Migration files are generated for each app separately.

While we are in the development environment, if we need to delete the data in the database, we can do so using the following command:

```bash
cd ~/Projects/sportsclub/sportsclub
python manage.py flush --no-input
```

> The command `manage.py flush` keeps the schema intact, but it reloads the initial data fixtures, if any.

Then migrate:

```bash
cd ~/Projects/sportsclub/sportsclub
python manage.py migrate
```

Also while in development, if we want or need to delete all the migration files, e.g., we have made a lot of small modifications to the model and we want a clean slate, we can delete the migration files using the following commands:

```bash
cd ~/Projects/sportsclub/sportsclub
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
```

We can add a `~/Projects/sportsclub/Makefile` target for convenience:

```makefile
# Makefile
reset-migrations:
	find sportsclub/ -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find sportsclub/ -path "*/migrations/*.pyc" -delete
```

Then run it with `make reset-migrations`. Using a `Makefile` in a project is common practice, as it helps us automate ways to solve practical problems.

## Superuser

We need to create a superuser, which will have all permissions and which we will use to access the admin panel for the first time:

```bash
python manage.py createsuperuser --username admin --email root@localhost
```

## Admin panel

If we want to use Django's admin panel (at `/admin/`), we need to configure how each entity appears in it. This is done in the `admin.py` file of each app. They all follow the same pattern, described next for the `Address` model in the `core/admin.py` file, as an example.

First, register the model with the admin site. Without this, the model would not appear in the admin panel.

```python
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
```

Then configure the list view, which controls the table view when we browse all addresses:

```python
# Which columns appear in the table
list_display = ['public_id', 'line1', 'city', 'country', 'postal_code']

# Which columns are clickable links to the edit page
list_display_links = ['public_id', 'line1']

# Which fields the search box queries
search_fields = ['public_id', 'line1', 'line2', 'city', 'state', 'country', 'postal_code']

# Adds filter dropdowns in the sidebar
list_filter = ['country', 'state', 'city']

# Pagination: 50 records per page
list_per_page = 50

# Default sort order
ordering = ['country', 'city', 'line1']

# Adds save buttons at the top of the form, not just the bottom
save_on_top = True
```

Next configure the settings that control the edit/create form:

```python
# Groups fields into collapsible sections with headers and descriptions.
# The 'classes': ('collapse',) makes "System information" collapsed by default.
fieldsets = (
    ('Address information', {
        'fields': ('line1', 'line2'),
        'description': 'Primary address details'
    }),
    ('Location', {
        'fields': ('postal_code', 'city', 'state', 'country'),
        'description': 'Geographic location details'
    }),
    ('System information', {
        'fields': ('id', 'public_id', 'formatted_address'),
        'classes': ('collapse',),
        'description': 'Read-only system fields for debugging'
    }),
)

# These fields are displayed but cannot be edited
readonly_fields = ['id', 'public_id', 'formatted_address']
```

Finally, we can define a custom display method:

```python
# Adds a computed field showing the address as it would appear when converted to string (via the model's `__str__` method).
# The `short_description` attrbite sets its label in the admin.
def formatted_address(self, obj):
    """Display how the address will be formatted in the system."""
    return str(obj)
formatted_address.short_description = 'Formatted display'
```

## API endpoints

API endpoints are defined in the `api.py` file of each app, and the schemas to validate requests and responses are defined in the `schemas.py` file of each app.

Unless we have a single entity in an app, we want to split the API endpoints into separate files. Therefore, we will create the `api/` directory inside apps that require it:

```bash
mkdir --parents ~/Projects/sportsclub/people/api
rm --force ~/Projects/sportsclub/people/api.py
```

This directory will contain three files: `__init__.py`, `athletes.py` and `coaches.py`. Here is the `__init__.py` content example:

```python
# people/api/__init__.py
from ninja import Router

from people.api.athletes import router as athletes_router
from people.api.coaches import router as coaches_router

router = Router(tags=["people"])
router.add_router("", athletes_router)
router.add_router("", coaches_router)
```

> In this simple application we are demonstrating two ways of doing this, but one would want to always use the same criteria project-wide.

### Pydantic schemas

[Pydantic](https://pydantic.dev/) is a data validation package for Python. It enables defining models we can use, and reuse, to verify that data conforms to the format we expect before we store or process it.

We will start by creating the file `core/schemas.py` and adding the Pydantic schemas for the `Address` entity. Note that Pydantic schemas are completely independent from Django models, i.e., they do not automatically inherit field constraints, so we have to define them separately. Actually, defining validation in both places (Pydantic schema and Django's ORM schema) is intentional, and follows a principle called "defense in depth":

```python
# core/schemas.py
from ninja import Field, Schema
from pydantic import ConfigDict, field_validator


class AddressIn(Schema):
    """Schema for creating/updating an address."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "line1": "Av. de Jaume III, 15",
                    "line2": "Centre",
                    "postal_code": "07012",
                    "city": "Palma",
                    "state": "Illes Balears",
                    "country": "Spain",
                }
            ]
        }
    )

    line1: str = Field(
        ..., min_length=1, max_length=255, description="Primary address information"
    )
    line2: str = Field(
        "",
        max_length=255,
        description="Secondary address information",
    )
    postal_code: str = Field("", max_length=20, description="Postal code")
    city: str = Field("", max_length=100, description="City name")
    state: str = Field("", max_length=100, description="State, province or region")
    country: str = Field("", max_length=100, description="Country name")

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, v):
        """Remove whitespace for consistency."""
        if v:
            v = v.strip()
        return v


class AddressOut(Schema):
    """Schema for returning address data."""

    public_id: str
    line1: str
    line2: str
    postal_code: str
    city: str
    state: str
    country: str
    formatted_address: str

    @staticmethod
    def resolve_formatted_address(obj):
        """Generate formatted address from the model's __str__ method."""
        return str(obj)


class AddressListOut(Schema):
    """Simplified schema for listing addresses."""

    public_id: str
    formatted_address: str

    @staticmethod
    def resolve_formatted_address(obj):
        """Generate formatted address from the model's __str__ method."""
        return str(obj)
```

These three classes inherit from the Pydantic `Schema` class to instruct Django abour serialisation and validaton of data:

* `AddressIn`: What the API accepts when creating/updating (no id or public_id).
* `AddressOut`: What the API returns (includes all fields).
* `AddressListOut`: Lighter version for list endpoints (optional, but good practice).
* `AddressPatch`: Version with all fields optional for partial updates.
* `ErrorResponse`: Standard error response to be used project-wide.
* `ValidationErrorResponse`: Validation error response with field-level details, to be used project-wide.

Similarly to the cases of models, API endpoints, and tests, when we have multiple entities in a single app, we can split the `schemas.py` file into several, inside a `schemas/` directory.

```bash
mkdir --parents ~/Projects/sportsclub/people/schemas
rm --force ~/Projects/sportsclub/people/schemas.py
```

The newly-created `people/schemas/` directory will have four files: `__init__.py`, `common.py`, `athletes.py`, and `coaches.py`.

These would be the contents of the `people/schemas/__init__.py` file:

```python
# people/schemas/__init__.py
from people.schemas.common import PersonRef
from people.schemas.athletes import (
    AthleteIn,
    AthleteListOut,
    AthleteOut,
    AthletePatch,
    AthleteRef,
)
from people.schemas.coaches import (
    CoachIn,
    CoachListOut,
    CoachOut,
    CoachPatch,
    CoachRef,
)

__all__ = [
    "PersonRef",
    "AthleteIn",
    "AthleteListOut",
    "AthleteOut",
    "AthletePatch",
    "AthleteRef",
    "CoachIn",
    "CoachListOut",
    "CoachOut",
    "CoachPatch",
    "CoachRef",
]
```

### App endpoints

Let's now define the endpoints in the `core/api.py` file, which we will have to create:

```python
# core/api.py
from django.shortcuts import get_object_or_404
from ninja import Router

from .models import Address
from .schemas import AddressIn, AddressListOut, AddressOut

router = Router()


@router.get("/addresses", response=list[AddressListOut], tags=["Addresses"])
def list_addresses(request):
    """
    List all addresses.

    Returns a simplified view of all addresses with only essential fields.
    """
    addresses = Address.objects.all()
    return addresses


@router.get("/addresses/{public_id}", response=AddressOut, tags=["Addresses"])
def get_address(request, public_id: str):
    """
    Get a single address by its public ID.

    Args:
        public_id: The unique public identifier for the address

    Returns:
        Complete address details including all fields
    """
    address = get_object_or_404(Address, public_id=public_id)
    return address


@router.post("/addresses", response={201: AddressOut}, tags=["Addresses"])
def create_address(request, payload: AddressIn):
    """
    Create a new address.

    Args:
        payload: Address data including line1 (required) and optional fields

    Returns:
        The newly created address with generated public_id
    """
    address = Address.objects.create(**payload.model_dump())
    return 201, address


@router.put("/addresses/{public_id}", response=AddressOut, tags=["Addresses"])
def update_address(request, public_id: str, payload: AddressIn):
    """
    Fully update an existing address (all fields replaced).

    Args:
        public_id: The unique public identifier for the address
        payload: Complete address data (all fields will be updated)

    Returns:
        The updated address
    """
    address = get_object_or_404(Address, public_id=public_id)

    for attr, value in payload.model_dump().items():
        setattr(address, attr, value)

    address.save()
    return address


@router.patch("/addresses/{public_id}", response=AddressOut, tags=["Addresses"])
def partial_update_address(request, public_id: str, payload: AddressIn):
    """
    Partially update an existing address (only provided fields updated).

    Args:
        public_id: The unique public identifier for the address
        payload: Partial address data (only provided fields will be updated)

    Returns:
        The updated address
    """
    address = get_object_or_404(Address, public_id=public_id)

    # Only update fields that were actually provided
    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(address, attr, value)

    address.save()
    return address


@router.delete("/addresses/{public_id}", response={204: None}, tags=["Addresses"])
def delete_address(request, public_id: str):
    """
    Permanently delete an address.

    Warning: This action cannot be undone. Ensure no entities (venues, athletes)
    are referencing this address before deletion.

    Args:
        public_id: The unique public identifier for the address

    Returns:
        204 No Content on successful deletion
    """
    address = get_object_or_404(Address, public_id=public_id)
    address.delete()
    return 204, None
```

Notice these important bits from the code:

* We specify the HTTP methods via the router: `router.get`, `router.post`, and so on.
* Django Ninja automatically serializes the model to JSON using the `response=AddressOut` schema.
* Django Ninja automatically validates incoming JSON using the `payload: AddressIn` schema.
* Endpoints in the API docs are grouped via the `tags` parametre.
* Parametres in the path are typed so they can be validated, e.g., `{public_id: str}`.
* A 404 error is returned if no object is found via the `get_object_or_404()` method.

Regarding ID and public ID, we use `public_id` exclusively in our API so that we never expose internal database IDs (security) and we can change databases or merge data without breaking APIs.

### Project API

Next, we need to create the main `sportsclub/api.py` file for our API module:

```python
# sportsclub/api.py
from ninja import NinjaAPI
from ninja.errors import ValidationError
from django.http import Http404
from core.api import router as core_router


api = NinjaAPI(
    title="Athletics Sports Club API",
    version="1.0.0",
    description="API for managing athletic sports clubs",
    docs_url="/docs",  # Swagger UI at /api/v1/docs
    openapi_url="/openapi.json",  # OpenAPI spec at /api/v1/openapi.json
    # Unique ID to prevent "multiple NinjaAPIs" conflicts during test discovery
    urls_namespace="sportsclub_api",
)

@api.exception_handler(Http404)
def not_found(request, exc):
    return api.create_response(
        request,
        {"detail": "Resource not found"},
        status=404,
    )

@api.exception_handler(ValidationError)
def validation_error(request, exc):
    return api.create_response(
        request,
        {"detail": exc.errors},
        status=422,
    )

# Register app routers
api.add_router("/core/", core_router)

# For future reference
# api.add_router("/people/", people_router)
# api.add_router("/scheduling/", scheduling_router)
# api.add_router("/inventory/", inventory_router)
```

### Routing

We are now ready to update the main `sportsclub/urls.py` file with all the API endpoints, which will be served under `/api/`:

```python
# sportsclub/urls.py
from django.contrib import admin
from django.urls import path
from sportsclub.api import api


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', api.urls),
]
```

## Running the project

Run the development server:

```bash
python manage.py runserver
```

We can now access:

1. The API documentation at http://127.0.0.1:8000/api/v1/docs
2. If you have registered the moduleThe admin panel at http://127.0.0.1:8000/admin/.

Use `curl` and `jq` to test the endpoints:

```bash
# Create an address
curl -X POST http://127.0.0.1:8000/api/v1/core/addresses \
  -H "Content-Type: application/json" \
  -d '{
    "line1": "Av. de Jaume III, 15",
    "line2": "Centre",
    "postal_code": "07012",
    "city": "Palma",
    "country": "Spain"
  }' | jq

# Save the `<public_id>` for later use

# Create another address
curl -w "\n" -X POST http://127.0.0.1:8000/api/v1/core/addresses \
  -H "Content-Type: application/json" \
  -d '{
    "line1": "Plaça de la Porta de Santa Catalina, 10",
    "line2": "Centre",
    "postal_code": "07012",
    "city": "Palma",
    "state": "Illes Balears",
    "country": "Spain"
  }' | jq

# List all addresses
curl -w "\n" http://127.0.0.1:8000/api/v1/core/addresses | jq

# Get address by ID
curl -w "\n" http://127.0.0.1:8000/api/v1/core/addresses/<public_id> | jq

# Update address
curl -w "\n" -X PUT http://127.0.0.1:8000/apiv1//core/addresses/<public_id> \
  -H "Content-Type: application/json" \
  -d '{
    "line1": "C/ de Miquel dels Sants Oliver, 2",
    "postal_code": "07012",
    "city": "Palma",
    "country": "Spain"
  }' | jq

# Partial update of address
curl -w "\n" -X PATCH http://127.0.0.1:8000/api/v1/core/addresses/<public_id> \
  -H "Content-Type: application/json" \
  -d '{"line2": "Nord"}' | jq

# Delete address
curl -w "\n" -X DELETE http://127.0.0.1:8000/api/v1/core/addresses/<public_id> | jq
```

> Take the `<public_id>` from the output of the first command

## Home page

If we try to load the home page at http://127.0.0.1:8000/ we will get a 404 error. This is bacause we have not yet defined any home page. Let's create a simple view and template for the root URL.

Start by creating a template directory in the `sportsclub` app:

```bash
mkdir --parents ~/Projects/sportsclub/sportsclub/templates
```

Continue by creating the template `sportsclub/templates/home.html` with the content you want:

```html
<!-- sportsclub/templates/home.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sports Club</title>
</head>
<body>
    <h1>Sports Club API</h1>
    <p>Welcome to the Sports Club management system.</p>
    <ul>
        <li><a href="/api/v1/docs">API Documentation</a></li>
        <li><a href="/admin/">Admin Panel</a></li>
    </ul>
</body>
</html>
```

In the `sportsclub/settings.py` file, update the `DIRS` key in the `TEMPLATES` variable to include the templates directory:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

And, finally, update the `urlspatterns` variable in the `sportsclub/urls.py` file:

```python
# sportsclub/urls.py
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from .api import api

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
]
```

> `TemplateView` is Django's built-in generic view for rendering simple templates without needing to write a custom view function.

Stop the development server if it is running, then start it:

```bash
python manage.py runserver
```

And load the home page at http://127.0.0.1:8000/.

## Tests

Django's test runner automatically discovers tests following these rules:

1. Looks for a file named `tests.py` or a `tests/` module[^4] inside each app.
2. Looks for files matching the `test*.py` pattern inside the `tests/` directory.
3. Looks for classes inheriting from `unittest.TestCase` or `django.test.TestCase`.
3. Looks for class methods starting with `test_`.

[^4]: In Python, a module is a directory with a `__init__.py` file inside, which can be empty.
Django Ninja has two test clients, a synchronous one, named `TestClient`, and an asynchronous one, named `TestAsyncClient`.

`TestClient` is meant for regular synchronous views, is based on Django's test client, and is simpler to use and understand. `TestAsyncClient` is meant for asynchronous views (using `async def`), requires Python's `asyncio`, and is more complex to use and understand but necessary for async code, e.g., asynchronous database queries, external APIs, etc.

In this project we will not use `asyncio`, therefore we will not make use of the `TestAsyncClient`. Moreover, due to bugs in the Django Ninja's `TestClient`, we will be using Django's `TestCase` client:

* [Router already attached / Multiple NinjaAPIs error](https://github.com/vitalik/django-ninja/issues/1195).
* [TestClient instantiation errors](https://github.com/vitalik/django-ninja/issues/354).
* [Discussion on testing with TestClient](https://github.com/vitalik/django-ninja/discussions/1213).
* [Testing exception handlers](https://github.com/vitalik/django-ninja/discussions/1211).

The core issue is that `TestClient` with a `NinjaAPI` instance (rather than a `Router`) triggers validation conflicts when multiple tests run, especially with `django.test.TestCase`.

### Test types

In a headless Django Ninja application, we will be working with the following types of tests:

* **Unit tests** test individual components in isolation, such as models, utilities, schema validation logic, or business logic.
* **API tests** test API endpoints. These are integration tests, as they test the full stack from request to response.
* **Contract tests** ensure API contracts (schemas) remain stable, i.e., field names, types, and structure.
* **End-to-end tests** test complete workflows across multiple endpoints/apps. These are acceptance tests that represent user stories and business requirements, and span across multiple apps (e.g., "As a club manager, I can register an athlete and assign him or her to a team").

Cross-app integration tests will be located in two different places:

* Within-app tests will be kept in the respective app, e.g., `people/tests/test_api.py` will have tests for `Athlete` endpoitns that reference `Address`.
* Cross-app workflow tests will be kept in the project-level `tests/test_workflows.py`. There tests will span across mutiple apps.

Therefore, the test structure we will be using is as follows:

```
sportsclub/
├── core/
│   └── tests/
│       ├── __init__.py
│       ├── test_models_<entity>.py # Unit tests for models
│       ├── test_schemas.py         # Unit and contract tests for schema validation and serialisation
│       ├── test_api_<entity>.py    # API endpoint tests (integration tests)
│       └── test_utils.py           # Unit tests for utilities
│
└── tests/                          # Project-level tests
    ├── __init__.py
    ├── test_workflows.py           # Cross-app workflow tests (business logic, acceptance tests)
    ├── test_contracts.py           # API contract tests
    └── fixtures.py                 # Prepared test data loaded into the database
```

So, to conclude this section, let's create the two necessary sub-directories:

```bash
cd ~/Projects/sportsclub/sportsclub
mkdir core/tests inventory/tests people/tests scheduling/tests tests
```

Optionally, you can delete the `tests.py` file inside each application:

```bash
cd ~/Projects/sportsclub/sportsclub
rm core/tests.py inventory/tests.py people/tests.py scheduling/tests.py
```

For reference, a bit of testing nomenclature:

| Term     | Definition                                                           | Example                                         | When to use                                         |
|----------|----------------------------------------------------------------------|-------------------------------------------------|-----------------------------------------------------|
| Fixtures | Prepared test data loaded into the database                          | A `setUp()` method creating `Address` objects   | Test data for your own models                       |
| Mocks    | Fake objects that record how they are called and verify interactions | Mocking an external payment API                 | Verify interactions with external systems           |
| Stubs    | Fake objects that return predetermined responses                     | A stub email service that always returns `sent` | Replace external dependencies with simple responses |
| Fakes    | Working implementations with shortcuts                               | A in-memory database instead of PostgreSQL      | Speed up tests                                      |

### The tests module

Before writing any tests, let's create the `core/tests/__init__.py` file so that Python will consider it a module:

```python
# core/tests/__init__.py
"""Test suite for the core app."""
```

We will structure our tests inside `core/tests/` the following way:

* `test_models_address.py`: Unit tests for the `Address` model.
* `test_models_auditory.py`: Unit tests for the `Auditory` base model.
* `test_schemas.py`: Unit tests for the Pydantic schema validation.
* `test_api_addresses.py`: Integration tests for the `Address` API endpoints.

### Unit tests

We will have a separate file, with one or more classes, for each entity. Let's being with the test of the abstract model `Auditory`:

```python
# core/tests/test_models_auditory.py
"""Unit tests for the Auditory base model."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import Address

User = get_user_model()


class AuditoryModelTest(TestCase):
    """Unit tests for the Auditory abstract model behavior."""

    def setUp(self):
        """Create a test user for auditory fields."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_soft_delete(self):
        """Test soft delete functionality."""
        address = Address.objects.create(line1="Test Address")

        # Verify address exists
        self.assertEqual(Address.objects.count(), 1)

        # Soft delete
        address.soft_delete()

        # Verify it is marked as deleted
        self.assertIsNotNone(address.deleted_at)

        # Verify default manager excludes it
        self.assertEqual(Address.objects.count(), 0)

        # Verify all_objects manager includes it
        self.assertEqual(Address.all_objects.count(), 1)

    [..]
```

> Note that we are using the `django.test.TestCase` client instead of the `ninja.TestClient` because of bugs in the latter that could not be solved.

In the `Auditory` model we used just one class but for the `Address` model we will be using different classes as a way to group related tests:

* `AddressCreationTest`, to test address creation.
* `AddressPublicIDTest`, to test the `public_id` field behaviour.
* `AddressStringRepresentationTest`, to test the `__str__()` method.
* `AddressMetaConfigurationTest`, to test the model `Meta` configuration.
* `AddressQueryMethodsTest`, to test the model query methods.

### Schema tests

The `core/tests/test_schemas.py` file tests the Pydantic schemas working as intended. We will be testing the different validation schemas (`AddressIn`, `AddressListOut`, `AddressOut`, `AddressPatch`) separately, similarly to what we did with the unit tests of the `Address` model.

```python
# core/tests/test_schemas.py
"""Unit tests for Ninja schemas (validation, serialization)."""

from django.test import TestCase
from pydantic import ValidationError

from core.models.address import Address
from core.schemas import AddressIn, AddressListOut, AddressOut, AddressPatch


class AddressInSchemaTest(TestCase):
    """Test the AddressIn schema validation."""

    def test_valid_full_address(self):
        """Test validation with all fields."""
        data = {
            "line1": "Av. de Jaume III, 15",
            "line2": "Centre",
            "postal_code": "07012",
            "city": "Palma",
            "state": "Illes Balears",
            "country": "Spain",
        }
        schema = AddressIn(**data)

        self.assertEqual(schema.line1, "Av. de Jaume III, 15")
        self.assertEqual(schema.line2, "Centre")
        self.assertEqual(schema.postal_code, "07012")
        self.assertEqual(schema.city, "Palma")
        self.assertEqual(schema.state, "Illes Balears")
        self.assertEqual(schema.country, "Spain")
    
    [..]
```

### API tests

The `core/tests/test_api_addresses.py` file will hold our integration tests for the `Address` model. We will be using the `setUp()` class method to set up sample data before each test is run.

```python
# core/tests/test_api_addresses.py
import json
from django.test import TestCase
from core.models import Address


class AddressAPITestCase(TestCase):
    """
    Test suite for Address API endpoints.

    Uses Django's built-in test client with full URL paths (/api/v1/...).
    """

    def setUp(self):
        """Set up sample data before each test."""
        self.address1 = Address.objects.create(
            line1="Av. de Jaume III, 15",
            line2="Centre",
            postal_code="07012",
            city="Palma",
            state="Illes Balears",
            country="Spain",
        )

        self.address2 = Address.objects.create(
            line1="Plaça de la Porta de Santa Catalina, 10",
            postal_code="07012",
            city="Palma",
            state="Illes Balears",
            country="Spain",
        )

    def test_list_addresses(self):
        """Test GET /api/v1/core/addresses."""
        response = self.client.get("/api/v1/core/addresses")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

        first_address = data[0]
        self.assertIn("public_id", first_address)
        self.assertIn("formatted_address", first_address)
    
    [..]
```

### Running the tests

Let's now run these tests:

```bash
cd ~/Projects/sportsclub/sportsclub
python manage.py test core
```

We could also run the test verbosely, and for a specific test class only:

```bash
cd ~/Projects/sportsclub/sportsclub
python manage.py test core.tests.test_api_addresses.AddressAPITestCase -v 2
```

When we have more apps, we can run all the tests from all the apps with a single command:

```bash
cd ~/Projects/sportsclub/sportsclub
python manage.py test
```

## Acceptance tests

Next we have a list of acceptance tests, all located inside `~/Projects/sportsclub/sportsclub/tests/` (inside the Django project directory, alongside the apps), divided into files.

```
sportsclub/tests/
├── __init__.py
├── test_acceptance_core.py        # Address CRUD workflows
├── test_acceptance_inventory.py   # Venue CRUD workflows
├── test_acceptance_people.py      # Athlete/Coach workflows and relationships
├── test_acceptance_scheduling.py  # Season/Competition/Training workflows
├── test_acceptance_api_docs.py    # OpenAPI schema availability
└── test_acceptance_workflows.py   # Cross-app workflows (e.g., create full competition with venue, coaches, athletes)
```

> There are no authentication tests because this project, for simplicity, does not use any.

These tests can be run by path, as the `tests/` directory at `~/Projects/sportsclub/sportsclub/tests/` is not a Python package that Django can discover automatically:

```bash
cd ~/Projects/sportsclub/sportsclub
python manage.py test tests
```

They will still be run as part of the general test command:

```bash
cd ~/Projects/sportsclub/sportsclub
python manage.py test
```

## Fixtures

Django has a native mechanism to load test data into the database: fixtures. We can create JSON/YAML files with test data and load them via `python manage.py loaddata`. Advantages of using this system versus loading the data via SQL into the database are:

1. It is database-agnostic.
2. It respects Django model validation.
3. It is version-controlled.

Fixtures will be made available as a set of files inside the `fixtures/` subdirectory of each Django app. For example:

```json
[
  {
    "model": "core.address",
    "pk": 1,
    "fields": {
      "public_id": "addr_estadio_olimpico",
      "line1": "Avinguda de l'Estadi, 60",
      "line2": "Montjuïc",
      "city": "Barcelona",
      "state": "Catalunya",
      "postal_code": "08038",
      "country": "Spain",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z",
      "deleted_at": null
    }
  }
]
```

## Github Actions

GitHub Actions is a continuous integration and continuous delivery (CI/CD) platform that allows us to automate our build, test, and deployment workflows directly within GitHub. It enables creating automated processes that trigger when specific events occur in a repository, such as when someone opens a pull request, creates an issue, or pushes a commit.

Key components are:

* **Workflows**: Automated processes defined in YAML files stored in the `.github/workflows` directory of the repository that run one or more job.
* **Events**: Activities that trigger workflows, like pull requests, issues, commits, or scheduled times.
* **Jobs**: Sets of steps that execute on the same runner, which can run in parallel or sequentially.
* **Actions**: Reusable code packages that perform specific tasks like pulling the repository, setting up build environments, or deploying to cloud providers.
* **Runners**: Servers that execute workflows.

This project includes a `.github/workflows/ci.yml` file that has four jobs:

| Job         | Purpose                                 | Runs when              |
|-------------|-----------------------------------------|------------------------|
| lint        | Check code style with Ruff              | Always                 |
| test        | Run Django tests against PostgreSQL     | Always                 |
| build       | Verify Docker image builds successfully | After lint & test pass |
| integration | Start full stack and test API endpoints | After lint & test pass |

Key features of this workflow:

* PostgreSQL service container: GitHub Actions spins up a real PostgreSQL instance for tests
* Dependency caching: Speeds up subsequent runs by caching pip packages
* Docker layer caching: Uses GitHub Actions cache for faster Docker builds
* Parallel execution: `build` and `integration` run in parallel after `lint` and `test`
* Failure handling: Logs are shown if integration tests fail
* Environment variables now match `.env.example` (except DEBUG=False for CI safety)

## Ruff formatting

Our first push to the Github repository will trigger the `ci.yml` workflow. We will be able to follow its execution via the `Actions` tab in our repository at Github. To make sure we do not get linting errors not caused by us, e.g., use of single quotes in strings instead of double quotes in files created by the `manage.py startapp` command, run these commands before pushing:

```bash
cd ~/Projects/sportsclub
pip install ruff
ruff check --fix .
ruff format .
```

Review the changes made by `ruff check --fix` and `ruff format`, delete unnecessary files, such as the `views.py` file in each app, stage the changed files and commit them. Then push the commits.
