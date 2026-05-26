# Parche de Corrección: Cálculo de IVA en Compras (Régimen Simple)

Este documento detalla los pasos para aplicar la corrección del cálculo del IVA en el módulo de compras directamente en el servidor de producción.

## 1. Identificar el problema
En producción, cuando una empresa con `Régimen Simple` realiza una compra y el proveedor cobra IVA, el sistema estaba forzando el valor del IVA a cero ($0). Esto provocaba que el **Costo de Inventario** y las **Cuentas por Pagar** quedaran registrados por un valor inferior al total real facturado.

## 2. Archivo a modificar
Ruta relativa al proyecto:
`backend/app/services/purchase_service.py`

## 3. Código a reemplazar

Busca el método `_calculate_item_values` (aproximadamente en la línea 40). 

**Encontrarás este bloque de código original:**
```python
        subtotal_after_discount = subtotal - discount_amount

        if company_regimen == "SIMPLE":
            tax_amount = Decimal("0.00")
        else:
            tax_rate = Decimal(str(item.tax_rate))
            tax_amount = subtotal_after_discount * (tax_rate / 100)

        line_total = subtotal_after_discount + tax_amount
```

**Reemplázalo completamente por este nuevo código:**
```python
        subtotal_after_discount = subtotal - discount_amount

        # Se elimina la restricción del Régimen Simple para que el IVA
        # siempre sea sumado como mayor valor del costo/inventario.
        tax_rate = Decimal(str(item.tax_rate))
        tax_amount = subtotal_after_discount * (tax_rate / 100)

        line_total = subtotal_after_discount + tax_amount
```

## 4. Reiniciar los servicios
Una vez que hayas guardado los cambios en el archivo `purchase_service.py` en el servidor de producción, debes reiniciar el contenedor del backend para que los cambios surtan efecto.

Ejecuta el siguiente comando en la raíz del proyecto (donde está el archivo `docker-compose.yml`):

```bash
docker compose restart backend
```

## 5. Validar la corrección
Para validar que el parche funciona en producción:
1. Elimina o anula cualquier factura de prueba que haya quedado con el IVA en $0.
2. Crea una nueva compra y añade un producto con porcentaje de IVA (ej. 19%).
3. Verifica en la parte inferior del formulario que el total incluya correctamente la suma del Subtotal + IVA.
4. Revisa en Contabilidad -> Libro de Compras que la factura tenga el valor total correcto.
