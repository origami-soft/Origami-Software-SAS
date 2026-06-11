# -*- coding: utf-8 -*-
{
    'name': 'hr_expenses_perceptions',
    'version': '1.0.0',
    'category': 'Accounting',
    'summary': 'Percepciones en reportes de gastos',
    'author': 'BLUEORANGE GROUP S.R.L.',
    'website': 'https://www.blueorange.com.ar',
    'license': 'OPL-1',
    'depends': [
        'l10n_ar_perceptions',
        'hr_expense',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_expense_sheet_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'description': """
=====================================================
Percepciones en Reportes de Gastos de Empleados
=====================================================

Objetivo del módulo
====================

**Este módulo resuelve ese problema** al incorporar una sección de percepciones
directamente dentro del reporte de gastos, permitiendo:

- Registrar las percepciones que figuran en los comprobantes de gasto.
- Calcular automáticamente los importes de percepción a partir de la base y la
  alícuota.
- Incluir dichos importes en el total del reporte de gastos y en el asiento
  contable generado.
- Garantizar la correcta vinculación impositiva con el sistema de percepciones
  argentinas.

Funcionalidad
==============

Carga de percepciones en el reporte de gastos
-----------------------------------------------

Al abrir un reporte de gastos en el que el modo de pago sea **"Empleado (a
reembolsar)"**, el usuario encontrará una nueva sección denominada
**"Percepciones"**, ubicada debajo de las líneas de gasto.

Desde esta sección se pueden realizar las siguientes acciones:

1. **Agregar una percepción**: hacer clic en "Agregar línea" y seleccionar el
   tipo de percepción del desplegable. El sistema completará automáticamente la
   descripción, la jurisdicción y la base imponible.

2. **Ajustar la alícuota**: si la alícuota predeterminada no coincide con la del
   comprobante, el usuario puede modificarla. El importe de la percepción se
   recalculará automáticamente.

3. **Verificar el importe**: el campo de importe se calcula como
   Base × Alícuota. Representa el monto de la percepción.

4. **Eliminar una percepción**: seleccionar la línea y eliminarla desde la grilla.

Cálculo automático de la base
-------------------------------

Cada vez que se modifican las líneas de gasto (se agregan, editan o eliminan gastos),
el sistema recalcula automáticamente la base imponible de todas las percepciones
cargadas. La base corresponde a la suma de los importes netos (sin impuestos) de
todas las líneas de gasto del reporte.

Impacto en el total del reporte
---------------------------------

El total del reporte de gastos incluye las percepciones. En la zona de totales se
muestra un renglón adicional con la etiqueta "Percepciones" que indica la suma
de todos los importes de percepción convertidos a la moneda de la empresa.

Generación del asiento contable
---------------------------------

Cuando el reporte de gastos es aprobado y se genera el asiento contable, las
percepciones cargadas se trasladan automáticamente al asiento. Esto garantiza que:

- Los importes de percepción queden correctamente registrados en la contabilidad.
- Se vinculen los impuestos de percepción correspondientes a las líneas del asiento.
- El asiento refleje el total real pagado por el empleado, incluyendo las percepciones.

El asiento contable se genera en estado borrador y no se publica automáticamente,
permitiendo su revisión antes de la confirmación.

Conversión de moneda
----------------------

Si el gasto fue realizado en una moneda distinta a la moneda de la empresa, el
sistema convierte automáticamente el importe de la percepción a la moneda de la
empresa, utilizando la fecha contable del reporte como referencia para el tipo de
cambio.

Campos principales
===================

Campos de la sección "Percepciones" del reporte de gastos
------------------------------------------------------------

- **Percepción** (Obligatorio): Tipo de percepción a aplicar. Se selecciona de un
  listado que muestra únicamente las percepciones de compra configuradas para la
  empresa actual. Al seleccionar una percepción, se completan automáticamente la
  descripción, la jurisdicción y la base imponible.

- **Alícuota** (Obligatorio): Tasa porcentual de la percepción (por ejemplo, 3,00 %).
  Se muestra con formato de porcentaje. Al modificar este valor, el importe se
  recalcula automáticamente.

- **Base** (Obligatorio): Importe sobre el cual se aplica la alícuota. Se calcula
  automáticamente como la suma de los importes netos de todas las líneas de gasto
  del reporte. Puede ser ajustado manualmente si fuera necesario.

- **Importe** (Obligatorio): Resultado del cálculo Base × Alícuota. Representa el
  monto de la percepción que se sumará al total del reporte.

- **Descripción** (Opcional, se completa automáticamente): Nombre descriptivo de la
  percepción. Se completa automáticamente al seleccionar el tipo de percepción.

- **Jurisdicción** (Obligatorio, se completa automáticamente): Nivel jurisdiccional
  del tributo: Nacional, Provincial o Municipal. Se completa automáticamente al
  seleccionar el tipo de percepción.

- **Moneda** (Obligatorio, se completa automáticamente): Moneda en la que está
  expresada la percepción. Generalmente coincide con la moneda del reporte de gastos.

- **Total de Percepciones** (Calculado automáticamente): Suma de todos los importes
  de percepción del reporte, expresada en la moneda de la empresa. Se muestra en la
  zona de totales del reporte únicamente cuando el importe es mayor a cero.

Validaciones y reglas de negocio
==================================

Percepción duplicada
----------------------

No se permite cargar más de una percepción del mismo tipo en un mismo reporte de
gastos. Si el usuario intenta agregar una percepción que ya existe en el reporte,
el sistema mostrará el siguiente mensaje de error:

"No puede haber más de una percepción similar en un mismo reporte de gastos"

Acción requerida: eliminar la percepción duplicada o modificar la existente.

Percepción sin impuesto asociado
----------------------------------

Al generar el asiento contable, el sistema verifica que cada percepción tenga un
impuesto correctamente asociado en la configuración del sistema. Si no se encuentra
un impuesto vinculado, se mostrará un mensaje de error indicando:

"No hay impuesto que contenga la percepción [nombre]. Por favor asociar la
percepción al impuesto correspondiente en la configuración de impuestos"

Acción requerida: el administrador contable debe asociar la percepción al
impuesto correspondiente desde la configuración de impuestos.

Múltiples impuestos para una misma percepción
------------------------------------------------

Si el sistema detecta que una percepción está asociada a más de un impuesto, se
mostrará un mensaje de error:

"Hay más de un impuesto que tiene configurada la percepción [nombre]. Por
favor revisar la configuración de los impuestos [lista de impuestos]"

Acción requerida: el administrador contable debe revisar la configuración de
impuestos y asegurar que cada percepción esté vinculada a un único impuesto.

Edición según el estado del reporte
--------------------------------------

Las percepciones solo pueden agregarse, modificarse o eliminarse cuando el reporte
de gastos se encuentra en alguno de los siguientes estados:

- Borrador
- Enviado
- Aprobado

Una vez que el reporte alcanza el estado Publicado o posterior, las percepciones
quedan en modo de solo lectura y no pueden ser modificadas.

Modo de pago
--------------

La sección de percepciones solo está disponible cuando el modo de pago del reporte
es "Empleado (a reembolsar)". Para gastos pagados directamente por la empresa,
la sección de percepciones no se muestra.

Configuraciones necesarias
============================

Antes de utilizar este módulo, es necesario completar las siguientes configuraciones:

1. Configuración de percepciones
----------------------------------

Acceder a la configuración de percepciones argentinas desde:
Contabilidad → Configuración → Percepciones argentinas

Para cada percepción que se necesite utilizar en los reportes de gastos, verificar
que esté correctamente definida con los siguientes datos:

- Nombre descriptivo de la percepción.
- Jurisdicción (Nacional, Provincial o Municipal).
- Tipo de uso: debe ser "Compras".

2. Configuración de impuestos
-------------------------------

Acceder a la configuración de impuestos desde:
Contabilidad → Configuración → Impuestos

Para cada percepción configurada en el paso anterior, debe existir un único
impuesto que cumpla con las siguientes condiciones:

- Estar vinculado a la percepción correspondiente.
- Ser de tipo percepción en su configuración de cálculo.
- Tener alcance de "Compras".
- Pertenecer a la empresa correcta (o estar definido como global si aplica a
  todas las empresas).

Si un impuesto no está correctamente asociado a la percepción, el sistema
impedirá la generación del asiento contable y mostrará un mensaje de error.


Flujo de trabajo recomendado
==============================

1. El empleado crea un reporte de gastos con modo de pago "Empleado (a
   reembolsar)" y carga las líneas de gasto correspondientes.

2. En la sección "Percepciones", el empleado o el aprobador agrega las
   percepciones que figuran en los comprobantes de gasto, seleccionando el tipo de
   percepción y verificando la alícuota e importe.

3. El sistema calcula automáticamente la base imponible (suma de netos de los
   gastos) y el importe de cada percepción (base × alícuota).

4. El total del reporte se actualiza para incluir las percepciones.

5. El reporte transita el circuito de aprobación habitual (envío → aprobación).

6. Al generarse el asiento contable, las percepciones se registran
   automáticamente en el asiento en estado borrador, vinculando los impuestos
   correspondientes.

7. El área contable revisa y publica el asiento contable.

Limitaciones y consideraciones
================================

- El módulo no genera percepciones automáticamente a partir de reglas
  fiscales. Las percepciones deben ser cargadas manualmente por el usuario en cada
  reporte de gastos, en base a los comprobantes recibidos.

- Solo aplica a reportes de gastos con modo de pago "Empleado (a reembolsar)".
  Los gastos pagados directamente por la empresa no contemplan esta funcionalidad.

- Los asientos contables generados no se publican automáticamente, lo que
  permite al área contable revisarlos antes de su confirmación.
""",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: