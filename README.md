# Reload Matrix 🚀

![Vue.js](https://img.shields.io/badge/Frontend-Vue.js-4FC08D?style=flat-square&logo=vue.js)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)
![Docker](https://img.shields.io/badge/Container-Docker-2496ED?style=flat-square&logo=docker)

**Reload Matrix** es un completo sistema de gestión empresarial (ERP) diseñado para facilitar la administración de negocios, con un enfoque especial en tiendas de tecnología y talleres de reparación. Integra múltiples módulos para controlar el inventario, facturación, contabilidad completa (basada en normativas colombianas), tesorería y un avanzado módulo técnico de reparaciones.

---

## ✨ Características Principales

*   📦 **Inventario**: Gestión de productos, control de stock y categorías.
*   🧾 **Facturación (Invoicing)**: Generación de facturas, visualización de historial e impresión térmica (POS) o tamaño carta.
*   🔧 **Módulo de Reparación**: Creación de órdenes de servicio, seguimiento de estados, asignación de técnicos y aplicación de garantías.
*   👥 **Socios (Partners)**: Gestión unificada de clientes y proveedores con validación de documentos (NIT/CC).
*   💰 **Tesorería y Monedero**: Control de cajas, cuentas bancarias, transferencias y flujo de efectivo.
*   📊 **Contabilidad Avanzada**: Plan de cuentas, asientos contables automáticos, libro mayor, balances y cierres de mes.
*   🏢 **Gestión de Empresas**: Soporte multi-tenant básico y personalización de información empresarial (logo, NIT, etc.).

---

## 🛠️ Tecnologías Utilizadas

El proyecto está construido bajo una arquitectura cliente-servidor moderna y completamente dockerizada para garantizar la consistencia entre entornos.

### Frontend
*   [Vue.js 3](https://vuejs.org/) - Framework progresivo de JavaScript.
*   [Vuex](https://vuex.vuejs.org/) - Manejo de estado centralizado.
*   [Vue Router](https://router.vuejs.org/) - Enrutamiento dinámico.
*   CSS Nativo y diseño responsivo premium.

### Backend
*   [FastAPI](https://fastapi.tiangolo.com/) - Framework web rápido y moderno para construir APIs en Python.
*   [SQLAlchemy](https://www.sqlalchemy.org/) - ORM para la interacción con la base de datos.
*   [Pydantic](https://docs.pydantic.dev/) - Validación de datos y gestión de esquemas.
*   Base de datos relacional (SQLite por defecto para desarrollo ágil, compatible con PostgreSQL).

### Infraestructura
*   [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/) para la orquestación de contenedores.

---

## 🚀 Requisitos Previos

Para ejecutar este proyecto de manera local, solo necesitas tener instalado:
*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)
*   *Opcional:* Node.js y Python 3.10+ si deseas ejecutar los servidores fuera de contenedores.

---

## ⚙️ Instalación y Ejecución Local

La forma más rápida de levantar el proyecto es utilizando Docker Compose.

1. **Clona este repositorio:**
   ```bash
   git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   cd reload_Matrix
   ```

2. **Levanta los contenedores:**
   ```bash
   docker-compose up --build
   ```
   *Nota: Añade la bandera `-d` al final si quieres que se ejecute en segundo plano.*

3. **Accede a las aplicaciones:**
   *   **Frontend (App Web):** `http://localhost:8081`
   *   **Backend (API Base):** `http://localhost:8001/api/v1`
   *   **Documentación API (Swagger):** `http://localhost:8001/docs`

---

## 📂 Estructura del Proyecto (Monorepo)

```text
reload_Matrix/
│
├── backend/               # Servidor de FastAPI
│   ├── app/               # Lógica de negocio (routers, services, models)
│   ├── Dockerfile         # Receta de construcción del backend
│   └── requirements.txt   # Dependencias de Python
│
├── frontend/              # Aplicación Vue.js
│   ├── src/               # Componentes, vistas y store
│   ├── Dockerfile         # Receta de construcción del frontend
│   └── package.json       # Dependencias de Node
│
├── docker-compose.yml     # Orquestador principal de servicios
└── .gitignore             # Archivos excluidos del control de versiones
```

---

## 🛡️ Licencia

Este proyecto es privado. Todos los derechos reservados.
