Prioridad Alta:
1. Tabla warranties — El plan la menciona explícitamente en el diseño de DB pero no existe como modelo independiente (la garantía está embebida en repair_items como campo warranty_status)
2. Tabla warranties separada — Gestión de garantías con seguimiento propio, fechas de vencimiento, estado
3. Asientos contables automáticos — Al generar factura desde reparación, no se crea automáticamente el asiento en journal_entries. El plan dice: "Facturación → Asiento contable automático en libro diario"
4. Uso de partes de inventario en reparaciones — Al usar repuestos, no se descuenta automáticamente del inventario
5. Facturación electrónica XML UBL 2.1 — Los campos cufe, xml_ubl, estado_dian existen pero no hay lógica de generación/envío a DIAN
6. Libros contables automáticos — Libro Mayor, Libro de Ventas, Libro de Compras (solo existe Libro Diario básico)
7. Reportes para declaraciones tributarias — Declaración de IVA, retenciones, ingresos y patrimonios
8. Upload de logo de empresa — El modelo Company tiene logo_url pero no hay endpoint de upload
9. Creación de usuario admin en setup — El wizard de empresa no crea el usuario administrador inicial
10. Refresh tokens — El plan menciona "JWT con refresh tokens" pero solo hay access token
Prioridad Media:
11. Permisos granulares por módulo — Solo hay roles, no permisos por acción
12. Auditoría de cambios — Log de accesos y modificaciones a datos críticos
13. Políticas de contraseñas seguras — Validación de complejidad, expiración
14. i18n (internacionalización) — El plan lo menciona para el frontend
15. Escáner de código de barras con cámara — Simulado, no integrado con QuaggaJS/ZXing
16. Programa de lealtad en monedero — Mencionado como posible feature
17. Límites de crédito para proveedores — No implementado
18. Health checks en Docker Compose — Mencionados en el plan pero no configurados
19. Tests — Directorios tests/unit/ e tests/integration/ existen pero están vacíos
20. Manejo de excepciones personalizado — No hay exception handlers globales en FastAPI
21. Logging estructurado — No configurado en main.py
22. Notas crédito/débito — No hay modelo para documentos de ajuste DIAN
Prioridad Baja:
23. CI/CD pipeline
24. Backup y recuperación automatizada
25. Monitoreo en producción
26. Documentación y entrenamiento
27. Control de secuencias y rangos de facturación DIAN