# Manual del Dueño - Malargüe Tech (MVP)

## 1) Ingreso al sistema
1. Abrir `http://localhost:8000/admin/`.
2. Iniciar sesión con usuario administrador.

## 2) Cargar técnicos
1. Ir a **Users** y crear usuario técnico.
2. Ir a **Perfiles de usuario** y asignar rol `Técnico`.

## 3) Registrar repuestos
1. Ir a **Repuestos**.
2. Crear cada repuesto con `SKU`, `stock_actual`, `stock_minimo` y `precio_unitario`.

## 4) Registrar cliente y equipo
1. Ir a **Clientes** y crear cliente.
2. Ir a **Equipos** y asociarlo al cliente.

## 5) Crear orden de reparación
1. Ir a **Ordenes reparacion**.
2. Cargar problema reportado, técnico asignado y estado inicial.
3. Guardar.
4. El sistema genera automáticamente:
   - Token QR
   - Imagen QR
   - URL de seguimiento del cliente

## 6) Asociar repuestos a la orden
1. Dentro de la orden, agregar líneas de **Orden repuesto**.
2. Definir cantidad y precio unitario.

## 7) Cambio de estado y automatizaciones
- Al cambiar estado:
  - Se envía email automático al cliente (si tiene email).
- Al pasar a `Reparado`:
  - Se descuenta stock automáticamente.
  - Se registra movimiento de stock tipo `SALIDA`.

## 8) Seguimiento para cliente
- Compartir la URL o QR de la orden.
- El cliente puede ver estado, diagnóstico, precio estimado, técnico y repuestos.

## 9) Buenas prácticas para el parcial
- Mantener siempre cargado stock antes de iniciar reparaciones.
- Verificar que cada cliente tenga email para demostrar notificaciones.
- Mostrar en vivo:
  1. Alta de orden
  2. Escaneo/URL de QR
  3. Cambio de estado
  4. Descuento de stock automático
