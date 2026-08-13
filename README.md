# TESLIAN Odoo

Repositorio de módulos personalizados Odoo desarrollados por TESLIAN GROUP.

## Proyecto inicial

### teslian_billing_reconciliation

Módulo de conciliación de facturación para Seguimiento Global.

Flujo principal:

Odoo
→ TESLIAN CONNECT
→ RED GPS
→ conciliación de cliente y activos
→ habilitar o bloquear facturación.

## Regla principal

La facturación solo puede continuar cuando la información
de Odoo coincide con RED GPS.

Ante una discrepancia:

- la facturación queda bloqueada;
- el estado pasa a revisión;
- se requiere validación manual.