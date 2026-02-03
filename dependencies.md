# Gestión de Vulnerabilidades en Dependencias

## Índice
1. [Herramientas Nativas de GitHub](#herramientas-nativas-de-github)
2. [Activación y Configuración de Dependabot](#activación-y-configuración-de-dependabot)
3. [Análisis de la Pestaña Security](#análisis-de-la-pestaña-security)
4. [Alternativas para Cloud Privado](#alternativas-para-cloud-privado)
5. [Comparativa de Herramientas](#comparativa-de-herramientas)
6. [Implementación de pip-audit en CI](#implementación-de-pip-audit-en-ci)
7. [Ejecución Local Realizada](#ejecución-local-realizada)

---

## Herramientas Nativas de GitHub

GitHub tiene varias opciones integradas para gestionar la seguridad de dependencias:

**Dependency Graph**: Detecta automáticamente tus dependencias en `requirements.txt`, `setup.py` o `Pipfile`, mostrando qué versión tienes instalada de cada paquete.

**Dependabot Alerts**: Te notifica cuando encuentra vulnerabilidades conocidas en tus dependencias, indicando la severidad y sugiriendo versiones actualizadas.

**Dependabot Security Updates**: Crea PRs automáticos cuando detecta vulnerabilidades, incluyendo el CVE y los detalles de qué se corrige.

**Dependabot Version Updates**: También puede crear PRs periódicamente para mantener las dependencias actualizadas (sin vulnerabilidades).

---

## Activación y Configuración de Dependabot

Lo primero es ir a **Settings** del repo → **Security** → **Code security and analysis**. Ahí activas:
- **Dependency graph** (suele estar ya activado)
- **Dependabot alerts** (para que te notifique de vulnerabilidades)
- **Dependabot security updates** (para que cree PRs automáticas)

Luego configura las actualizaciones automáticas creando `.github/dependabot.yml`:

```yaml
# .github/dependabot.yml
version: 2

registries:
  # Si usas repositorios privados de Python
  python-private:
    type: python-index
    url: https://pypi.ejemplo.com/simple
    username: ${{ secrets.PYPI_USERNAME }}
    password: ${{ secrets.PYPI_PASSWORD }}

updates:
  # Configuración para dependencias de Python
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "Europe/Madrid"
    open-pull-requests-limit: 5
    reviewers:
      - "equipo-seguridad"
    labels:
      - "dependencias"
      - "seguridad"
    commit-message:
      prefix: "deps"
      include: "scope"
    ignore:
      # Ignorar actualizaciones mayores de Django (requieren revisión manual)
      - dependency-name: "Django"
        update-types: ["version-update:semver-major"]
    groups:
      # Agrupar actualizaciones de paquetes relacionados
      django-ecosystem:
        patterns:
          - "django*"
      pydantic:
        patterns:
          - "pydantic*"

  # Configuración para GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "ci"
      - "github-actions"

  # Configuración para Docker
  - package-ecosystem: "docker"
    directory: "/docker/app"
    schedule:
      interval: "monthly"
    labels:
      - "docker"
```

Una vez commits el archivo, puedes verlo en **Insights** → **Dependency graph** para confirmar que se aplicó correctamente.

---

## Análisis de la Pestaña Security

En la pestaña **Security** encontrarás las alertas de Dependabot. Cada una te muestra qué paquete tiene el problema, en qué versiones, qué versión lo arregla, y el CVE asociado.

Si encuentra algo:
- Si es crítico o alto, actúa rápido
- Si es medio o bajo, inclúyelo en el próximo sprint
- Evalúa si esa funcionalidad vulnerable está realmente expuesta

Puedes aceptar la PR automática de Dependabot o actualizar manualmente `requirements.txt`. Luego verifica que todo sigue funcionando.

---

## Alternativas para Cloud Privado

Si el repositorio está en un servidor privado (no en GitHub), necesitas otras herramientas para escanear vulnerabilidades.

### pip-audit

Herramienta de Python respaldada por Google y la PyPA. Es gratis, simple y no requiere conexión a servidores externos.

```bash
pip install pip-audit
pip-audit -r requirements.txt
pip-audit -r requirements.txt --strict  # Falla si hay vulnerabilidades
```

**Ventajas:** Totalmente gratis, open source, fácil integración en CI, mantiene PyPA.

**Desventajas:** Solo para Python, sin interfaz web.

### Trivy

Escáner completo que funciona para múltiples lenguajes. Muy útil si además quieres analizar contenedores Docker.

```bash
sudo apt-get install trivy
trivy fs .  # Escanea el directorio actual
trivy image sportsclub-app:latest  # Escanea una imagen Docker
```

**Ventajas:** Multi-lenguaje, escanea Docker, muy popular, open source.

**Desventajas:** Un poco más complejo, consume más recursos.

### Snyk

Plataforma comercial con versión gratuita limitada. Tiene interfaz web bonita pero es de pago para uso serio.

```bash
npm install -g snyk
snyk auth
snyk test --file=requirements.txt
```

**Ventajas:** Interfaz web, sugerencias detalladas, integración con IDEs.

**Desventajas:** De pago, requiere cuenta, envía datos a la nube.

### OWASP Dependency-Check

Herramienta respaldada por OWASP. Requiere Java pero genera reportes HTML detallados.

```bash
wget https://github.com/jeremylong/DependencyCheck/releases/download/v8.4.0/dependency-check-8.4.0-release.zip
./dependency-check.sh --scan . --format HTML --out report.html
```

**Ventajas:** Respaldo de OWASP, reportes HTML, sin necesidad de cuenta.

**Desventajas:** Requiere Java, descarga inicial lenta, mejor para Java/Maven.

---

## Eligiendo una herramienta

**pip-audit** es lo más práctico para este proyecto:
- Solo Python (no necesitamos más)
- Se integra fácil en CI
- Gratis
- Mantiene PyPA (confiable)
- No envía datos a terceros

Si necesitas analizar múltiples lenguajes o contenedores, usa **Trivy**.
Si tu empresa tiene presupuesto y quiere dashboards, mira **Snyk**.
Para requisitos de cumplimiento normativo, **OWASP Dependency-Check**.

---

## Implementacion de pip-audit en CI

### Workflow Actualizado

A continuacion se muestra el archivo `.github/workflows/ci.yml` modificado para incluir escaneo de seguridad con `pip-audit`:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  SECRET_KEY: secret
  DEBUG: "False"
  ALLOWED_HOSTS: localhost,127.0.0.1
  POSTGRES_USER: sportsclub
  POSTGRES_PASSWORD: sportsclub
  POSTGRES_DB: sportsclub
  POSTGRES_HOST: localhost
  POSTGRES_PORT: 5432

jobs:
  # ============================================
  # NUEVO JOB: Escaneo de Seguridad
  # ============================================
  security:
    name: Security Scan
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install pip-audit
        run: pip install pip-audit

      - name: Run pip-audit
        run: |
          echo "Escaneando vulnerabilidades en dependencias..."
          pip-audit -r requirements.txt --strict --format json --output audit-report.json || true
          pip-audit -r requirements.txt --strict
        continue-on-error: false

      - name: Upload audit report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: security-audit-report
          path: audit-report.json
          retention-days: 30

  lint:
    name: Lint
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install linting tools
        run: |
          python -m pip install --upgrade pip
          pip install ruff

      - name: Run Ruff linter
        run: ruff check .

      - name: Run Ruff formatter check
        run: ruff format --check .

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: [security]  # Los tests solo corren si security pasa

    services:
      postgres:
        image: postgres:18
        env:
          POSTGRES_USER: sportsclub
          POSTGRES_PASSWORD: sportsclub
          POSTGRES_DB: sportsclub
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U sportsclub"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run migrations
        working-directory: ./sportsclub
        run: python manage.py migrate

      - name: Run tests
        working-directory: ./sportsclub
        run: python manage.py test --verbosity=2

  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: [lint, test, security]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build app image
        uses: docker/build-push-action@v6
        with:
          context: .
          file: docker/app/Dockerfile
          push: false
          tags: sportsclub-app:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  integration:
    name: Integration Test
    runs-on: ubuntu-latest
    needs: [lint, test, security]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Create .env file
        run: |
          cat <<EOF > .env
          SECRET_KEY=secret
          DEBUG=False
          ALLOWED_HOSTS=localhost,127.0.0.1
          POSTGRES_USER=sportsclub
          POSTGRES_PASSWORD=sportsclub
          POSTGRES_DB=sportsclub
          EOF

      - name: Build and start services
        run: docker compose up -d --build

      - name: Wait for services to be healthy
        run: |
          echo "Waiting for services..."
          sleep 30
          docker compose ps

      - name: Run migrations in container
        run: |
          docker compose exec -T app-blue python manage.py migrate

      - name: Test API endpoint (blue)
        run: |
          curl -f http://localhost:8000/blue/api/v1/openapi.json || exit 1

      - name: Test API endpoint (green)
        run: |
          curl -f http://localhost:8000/green/api/v1/openapi.json || exit 1

      - name: Test main endpoint
        run: |
          curl -f http://localhost:8000/api/v1/openapi.json || exit 1

      - name: Show logs on failure
        if: failure()
        run: docker compose logs

      - name: Stop services
        if: always()
        run: docker compose down -v
```


El flujo es: Seguridad → Lint → Test → Build → Integration Test → Deploy (si es main).

---

## Ejecucion Local Realizada

A continuacion se documentan los pasos exactos ejecutados localmente para configurar pip-tools y pip-audit:

### Paso 1: Instalacion de Dependencias del Sistema

```bash
# Instalar pip y venv (necesario en Ubuntu/Linux Mint)
sudo apt update
sudo apt install -y python3-pip python3.12-venv
```

### Paso 2: Crear Entorno Virtual

```bash
cd /home/ciber/Documents/Ejercicios/EjercicioARealizar/sportsclub-main

# Crear entorno virtual
python3 -m venv venv
```

### Paso 3: Instalar Herramientas

```bash
# Activar entorno virtual e instalar pip-tools y pip-audit
./venv/bin/pip install --upgrade pip pip-tools
./venv/bin/pip install pip-audit
```

### Paso 4: Crear Archivos de Entrada (Input Files)

Se crearon dos archivos de entrada:

**requirements.in** (Produccion):
```
Django==6.0
django-cors-headers==4.9.0
django-environ==0.12.0
django-json-widget==2.1.0
django-nanoid-field==0.1.4
django-ninja==1.5.1
django-ratelimit==4.1.0
psycopg[binary,pool]==3.3.1
pydantic==2.12.5
email-validator==2.3.0
nanoid==2.0.0
whitenoise==6.11.0
```

**requirements-dev.in** (Desarrollo):
```
-r requirements.in
ruff==0.14.10
pip-audit
```

### Paso 5: Generar Lock Files con Hashes

```bash
# Generar requirements.txt con hashes SHA256
./venv/bin/pip-compile --generate-hashes requirements.in -o requirements.txt

# Generar requirements-dev.txt con hashes SHA256
./venv/bin/pip-compile --generate-hashes requirements-dev.in -o requirements-dev.txt
```

**Salida del comando:**
```
# This file is autogenerated by pip-compile with Python 3.12
# by the following command:
#
#    pip-compile --generate-hashes --output-file=requirements.txt requirements.in
#
annotated-types==0.7.0 \
    --hash=sha256:1f02e8b43a8fbbc3f3e0d4f0f4bfc8131bcb4eebe8849b8e5c773f3a1c582a53 \
    --hash=sha256:aff07c09a53a08bc8cfccb9c85b05f1aa9a2a6f23728d790723543408344ce89
    # via pydantic
...
```

### Paso 6: Ejecutar Escaneo de Seguridad

```bash
# Ejecutar pip-audit
./venv/bin/pip-audit -r requirements.txt
```

**Resultado:**
```
No known vulnerabilities found
```

### Archivos Generados

| Archivo | Descripcion |
|---------|-------------|
| `requirements.in` | Dependencias de produccion (input file) |
| `requirements.txt` | Lock file con hashes SHA256 |
| `requirements-dev.in` | Dependencias de desarrollo (input file) |
| `requirements-dev.txt` | Lock file de desarrollo con hashes |
| `.github/dependabot.yml` | Configuracion de Dependabot |
| `.github/workflows/ci.yml` | Pipeline CI actualizado con job security |

---
