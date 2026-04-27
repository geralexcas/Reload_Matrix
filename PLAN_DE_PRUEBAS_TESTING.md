# PLAN DE PRUEBAS - Sistema de Gestión Empresarial

## Objetivo
Verificar que las operaciones comerciales (creación de usuarios, proveedores, facturas de compra y ventas) se reflejen correctamente en los movimientos contables del sistema.

## Alcance
- Pruebas funcionales de los módulos: Usuarios, Proveedores, Compras, Ventas y Contabilidad
- Verificación de integración entre módulos operativos y contables
- Validación de asientos contables generados automáticamente

## Entorno de Pruebas
- **URL**: http://localhost:8081/
- **Base de datos**: PostgreSQL (según configuración del proyecto)
- **Navegador**: Chrome/Firefox última versión

## Credenciales de Acceso

### Usuario Técnico
- **Email**: geralexcas@gmail.com
- **Contraseña**: German22&
- **Rol**: TÉCNICO

### Usuario Administrador
- **Email**: Admin
- **Contraseña**: Admin@12345
- **Rol**: ADMINISTRADOR

## Casos de Prueba

### 1. Autenticación y Acceso
**ID**: TC-001
**Descripción**: Verificar acceso con diferentes roles
**Pasos**:
1. Iniciar sesión con usuario técnico (geralexcas@gmail.com / German22&)
2. Verificar permisos y menús disponibles
3. Cerrar sesión
4. Iniciar sesión con usuario administrador (Admin / Admin@12345)
5. Verificar permisos y menús disponibles
**Resultado esperado**: 
- Usuario técnico tiene acceso limitado
- Usuario administrador tiene acceso completo
- Sesiones funcionan correctamente

### 2. Creación de Usuarios
**ID**: TC-002
**Descripción**: Crear diferentes tipos de usuarios
**Pasos**:
1. Como administrador, navegar a Administración > Usuarios
2. Crear 3 usuarios con diferentes roles:
   - Vendedor: usuario1@test.com / Pass123!
   - Bodeguero: usuario2@test.com / Pass123!
   - Contador: usuario3@test.com / Pass123!
3. Verificar que los usuarios aparezcan en la lista
4. Intentar iniciar sesión con cada usuario nuevo
**Resultado esperado**:
- Usuarios creados exitosamente
- Cada usuario tiene los permisos adecuados según su rol
- Todos pueden iniciar sesión correctamente

### 3. Creación de Proveedores
**ID**: TC-003
**Descripción**: Crear proveedores para pruebas
**Pasos**:
1. Como administrador o vendedor, navegar a Socios > Proveedores
2. Crear 2 proveedores:
   - **Proveedor 1**: 
     - NIT: 123456789-0
     - Nombre: Proveedor Tecnológico SA
     - Tipo: PROVEEDOR
     - Responsabilidad fiscal: RESPONSABLE IVA
     - Límite de crédito: 10,000,000 COP
   - **Proveedor 2**:
     - NIT: 987654321-5
     - Nombre: Distribuidora Mayorista LTDA
     - Tipo: PROVEEDOR
     - Responsabilidad fiscal: NO RESPONSABLE
     - Límite de crédito: 5,000,000 COP
3. Verificar que los proveedores aparezcan en la lista
**Resultado esperado**:
- Proveedores creados con todos los datos requeridos
- Información almacenada correctamente en la base de datos
- Proveedores visibles en el listado

### 4. Creación de Factura de Compra
**ID**: TC-004
**Descripción**: Crear factura de compra y verificar asiento contable
**Pasos**:
1. Navegar a Compras > Nueva Compra
2. Seleccionar Proveedor 1 (Proveedor Tecnológico SA)
3. Agregar 2 productos:
   - Producto A: 10 unidades @ 100,000 COP c/u (IVA 19%)
   - Producto B: 5 unidades @ 200,000 COP c/u (Exento)
4. Seleccionar método de pago: CRÉDITO
5. Guardar factura
6. Verificar que la factura aparezca en el listado de compras
7. Navegar a Contabilidad > Asientos Contables
8. Buscar el asiento contable generado automáticamente
**Resultado esperado**:
- Factura de compra creada con número único
- Cálculos correctos: subtotal, IVA, total
- Asiento contable generado automáticamente con:
  - Débito a cuenta de inventario/compras
  - Crédito a cuenta de proveedores
  - Débito a cuenta de IVA por pagar (si aplica)
- Estado de la factura: EMITIDA

### 5. Pago de Factura de Compra
**ID**: TC-005
**Descripción**: Registrar pago de factura y verificar asiento contable
**Pasos**:
1. Navegar a Compras > Facturas Pendientes
2. Seleccionar la factura creada en TC-004
3. Registrar pago parcial de 1,000,000 COP
4. Método de pago: TRANSFERENCIA BANCARIA
5. Guardar pago
6. Verificar estado de la factura (PARCIAL)
7. Navegar a Contabilidad > Asientos Contables
8. Buscar el asiento contable del pago
**Resultado esperado**:
- Pago registrado correctamente
- Estado de factura cambia a PARCIAL
- Asiento contable generado con:
  - Débito a cuenta de proveedores
  - Crédito a cuenta de banco
- Saldo pendiente actualizado correctamente

### 6. Creación de Factura de Venta
**ID**: TC-006
**Descripción**: Crear factura de venta y verificar asiento contable
**Pasos**:
1. Navegar a Facturación > Nueva Factura
2. Crear un cliente nuevo:
   - NIT: 555555555-1
   - Nombre: Cliente Prueba SA
   - Tipo: CLIENTE
   - Responsabilidad fiscal: RESPONSABLE IVA
3. Agregar 2 productos:
   - Producto X: 5 unidades @ 150,000 COP c/u (IVA 19%)
   - Producto Y: 3 unidades @ 300,000 COP c/u (Exento)
4. Seleccionar método de pago: CONTADO
5. Guardar factura
6. Verificar que la factura aparezca en el listado
7. Navegar a Contabilidad > Asientos Contables
8. Buscar el asiento contable generado
**Resultado esperado**:
- Factura de venta creada con número único
- Cálculos correctos: subtotal, IVA, total
- Asiento contable generado automáticamente con:
  - Débito a cuenta de clientes
  - Crédito a cuenta de ventas
  - Crédito a cuenta de IVA cobrado (si aplica)
  - Débito a cuenta de caja/banco (por pago contado)
- Estado de la factura: PAGADA

### 7. Verificación de Libro Mayor
**ID**: TC-007
**Descripción**: Verificar que los movimientos se reflejen en el libro mayor
**Pasos**:
1. Navegar a Contabilidad > Libro Mayor
2. Seleccionar cuentas clave:
   - Proveedores
   - Clientes
   - Ventas
   - Compras
   - IVA
   - Caja/Banco
3. Verificar que los saldos reflejen las operaciones realizadas
4. Exportar reporte del libro mayor
**Resultado esperado**:
- Movimientos de compras y ventas reflejados correctamente
- Saldos de cuentas actualizados
- Balance entre débitos y créditos
- Reporte exportable en formato legible

### 8. Verificación de Balance de Prueba
**ID**: TC-008
**Descripción**: Verificar balance de prueba después de operaciones
**Pasos**:
1. Navegar a Contabilidad > Balance de Prueba
2. Generar balance de prueba para el período actual
3. Verificar que:
   - Suma de débitos = Suma de créditos
   - Cuentas de activo, pasivo, patrimonio, ingresos y gastos estén balanceadas
4. Exportar reporte
**Resultado esperado**:
- Balance de prueba equilibrado
- Todas las cuentas con saldos correctos
- Reporte exportable sin errores

### 9. Prueba de Integración Completa
**ID**: TC-009
**Descripción**: Verificar flujo completo desde compra hasta contabilidad
**Pasos**:
1. Crear nueva factura de compra con Proveedor 2
2. Registrar pago completo de la factura
3. Crear factura de venta a Cliente Prueba SA
4. Verificar asientos contables generados
5. Verificar libro mayor
6. Verificar balance de prueba
**Resultado esperado**:
- Todas las operaciones registradas correctamente
- Asientos contables generados automáticamente
- Saldos contables consistentes
- Información coherente en todos los reportes

## Criterios de Aceptación

1. **Funcionalidad**: Todas las operaciones deben completarse sin errores
2. **Integración**: Los módulos deben comunicarse correctamente
3. **Contabilidad**: Todos los movimientos deben generar asientos contables precisos
4. **Consistencia**: Los saldos deben mantenerse equilibrados
5. **Usabilidad**: La interfaz debe ser intuitiva y responsive

## Cronograma de Pruebas

| Fecha       | Actividad                                  | Responsable      |
|-------------|--------------------------------------------|------------------|
| Día 1       | Configuración y pruebas de autenticación   | Tester           |
| Día 1       | Creación de usuarios y proveedores          | Tester           |
| Día 2       | Pruebas de compras y pagos                 | Tester           |
| Día 2       | Pruebas de ventas                          | Tester           |
| Día 3       | Verificación contable completa             | Tester/Contador  |
| Día 3       | Pruebas de integración y reportes          | Tester           |

## Herramientas Utilizadas

- **Navegador**: Chrome con DevTools para debugging
- **Base de datos**: pgAdmin o DBeaver para verificación directa
- **API Testing**: Postman para verificación de endpoints
- **Documentación**: Markdown para registro de pruebas

## Registro de Defectos

Cualquier defecto encontrado será registrado con:
- ID del caso de prueba
- Descripción detallada
- Pasos para reproducir
- Severidad (Crítica/Alta/Media/Baja)
- Capturas de pantalla si aplica

## Aprobación

Este plan de pruebas debe ser aprobado por:
- **Gerente de Proyecto**: _______________________
- **Líder de Desarrollo**: _______________________
- **Contador**: _______________________

**Fecha de Aprobación**: _______________

---

*Documento generado por Mistral Vibe - Sistema de Pruebas Automatizadas*