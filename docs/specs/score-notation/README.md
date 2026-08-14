# Manifiesto de Transcripción de Partituras de Caja

**v4** — amplía la v3 para hacer explícita la semántica temporal y cubrir figuras con puntillo, ligaduras, grupos irregulares, ghost notes, rolls y estructuras de repetición, manteniendo la sintaxis compacta utilizada hasta ahora.

Este documento define un sistema de notación textual para transcribir partituras de caja (snare drum) a texto plano, de forma que una persona pueda reconstruir la partitura original —ritmo, sticking, silencios, articulaciones y estructura— únicamente a partir del texto, sin ambigüedad.

## Principios generales

1. **Cada símbolo debe representar una sola cosa.** No reutilizamos un mismo carácter para significados distintos.
2. **El texto debe ser reversible.** Debe poder reconstruirse la partitura original a partir de la transcripción.
3. **La simplicidad no debe sacrificar precisión.** Si hace falta un símbolo para representar información musical real, se añade.
4. **Un compás = una unidad de texto**, delimitada siempre por `|`.
5. **La notación representa ataques y eventos musicales**, no únicamente letras de sticking.
6. **La información temporal debe ser inequívoca.** Cuando una figura no pueda determinarse por contexto, su valor debe indicarse explícitamente.
7. **Las articulaciones y las duraciones son conceptos independientes.** Una ligadura de duración no debe confundirse con una ligadura de fraseo.

---

# Reglas de notación

## 1. Sticking base

* `R` = golpe/ataque con mano derecha.
* `L` = golpe/ataque con mano izquierda.
* Las letras se escriben en el orden exacto en que se ejecutan.
* No se insertan espacios entre golpes pertenecientes al mismo grupo rítmico.

Ejemplo:

```text
RLRL
```

representa cuatro ataques consecutivos: derecha, izquierda, derecha, izquierda.

---

## 2. Agrupación rítmica

### 2.1. Grupos regulares

`[ ... ]` = grupo de notas o eventos que comparten la misma unidad rítmica.

Por defecto, si no se especifica valor, la unidad es la **semicorchea**.

Ejemplo:

```text
[RLRL]
```

representa cuatro semicorcheas.

Los espacios entre grupos separan eventos rítmicos consecutivos dentro de un mismo compás:

```text
[RLRL] [RLRL]
```

El espacio no tiene significado temporal propio.

### 2.2. Valor explícito

Cuando sea necesario, el valor se indica antes de `:`:

```text
[4:R]
[8:RLRL]
[16:RLRL]
[32:RLRLRLRL]
```

Valores estándar:

* `4:` = negra
* `8:` = corchea
* `16:` = semicorchea
* `32:` = fusa

`16:` puede omitirse cuando el valor por defecto sea semicorchea.

Si dentro de un mismo compás conviven grupos de valores diferentes, se recomienda indicar el valor explícitamente en todos los grupos:

```text
[8:RLRL] [16:RLRL] [16:RLRL]
```

Esto evita cualquier dependencia del contexto.

---

## 3. Figuras con puntillo

Los valores con puntillo utilizan `.` después del valor:

```text
4.:
8.:
16.:
32.:
```

Ejemplos:

```text
[8.:R]
[16.:RL]
```

representan respectivamente una corchea con puntillo y dos semicorcheas con puntillo.

La notación de puntillo afecta al valor temporal indicado y no constituye una articulación.

---

## 4. Eventos de duración excepcional dentro de un grupo

Cuando dentro de un mismo grupo existan eventos con valores temporales diferentes, el valor puede indicarse individualmente.

Sintaxis:

```text
[valor:evento valor:evento ...]
```

Ejemplo:

```text
[8:R 16:L 16:R]
```

representa una corchea seguida de dos semicorcheas.

Esta forma se utilizará únicamente cuando sea necesario representar valores distintos dentro de una misma agrupación.

Cuando todos los eventos comparten valor, se utilizará la forma compacta:

```text
[16:RLRL]
```

---

## 5. Tresillos y grupos irregulares

Los tresillos se representan mediante:

```text
(3:RLR)
```

La marca `3:` es obligatoria.

Nunca se utiliza `[ ]` para representar por sí solo un tresillo.

### 5.1. Otros grupos irregulares

La sintaxis se generaliza a:

```text
(N:contenido)
```

donde `N` indica el número de eventos del grupo.

Ejemplos:

```text
(3:RLR)
(5:RLRLR)
(6:RLRLRL)
(7:RLRLRLR)
```

representan tresillo, quintillo, seisillo y septillo, respectivamente.

### 5.2. Relación temporal explícita

Cuando sea necesario indicar qué espacio temporal ocupa el grupo, se utiliza:

```text
(N/M:contenido)
```

donde:

* `N` = número de eventos reales
* `M` = número de subdivisiones equivalentes que ocupa temporalmente el grupo

Ejemplo:

```text
(3/4:RLR)
```

= tres notas ocupando el espacio temporal de cuatro unidades equivalentes.

Esto permite representar grupos irregulares distintos del tresillo estándar.

---

## 6. Silencios

`_` = silencio de una unidad temporal equivalente al valor especificado por el grupo.

Ejemplos:

```text
[16:RLR_]
[8:R_]
```

representan respectivamente una semicorchea de silencio y una corchea de silencio.

El número de eventos representados debe permitir reconstruir la posición temporal exacta.

### 6.1. Silencios con puntillo

`_.` = silencio con puntillo.

Ejemplo:

```text
[8:R _.]
```

o, cuando resulte más claro, mediante duración explícita:

```text
[8:R 8. :_]
```

La segunda forma se reserva para casos en los que la duración del silencio necesite quedar completamente explícita.

### 6.2. Silencios prolongados

Cuando un silencio ocupa más de una unidad, puede repetirse:

```text
[16:____]
```

o expresarse como duración explícita cuando la subdivisión no sea homogénea.

Nunca se omite una posición temporal silenciosa sin indicarla de alguna manera.

---

## 7. Ligaduras de duración

La ligadura de duración se representa mediante `^`.

`R^R` significa que la segunda representación no constituye un nuevo ataque, sino la prolongación de la primera nota.

Ejemplo:

```text
R^R
```

= una nota de mano derecha prolongada.

La ligadura de duración es distinta de la ligadura de fraseo.

Puede atravesar grupos:

```text
[16:RLR] R^R
```

y también barras de compás cuando sea necesario.

---

## 8. Acentos

`!` después de la mano = golpe acentuado.

Ejemplos:

```text
R!
L!
```

Un golpe sin `!` es un golpe normal.

Los acentos se especifican nota por nota.

Ejemplo:

```text
[R!L!RL]
```

Los acentos no se aplican automáticamente a todo un grupo.

---

## 9. Ghost notes

Las ghost notes se representan mediante `°` después de la mano:

```text
R°
L°
```

Ejemplo:

```text
[R L° R L]
```

La ghost note conserva su sticking pero se diferencia dinámicamente de una nota normal.

El acento y la ghost note pueden combinarse cuando la partitura lo requiera, aunque musicalmente no suele ser habitual.

---

## 10. Grace notes y flams

Las grace notes se escriben en minúscula.

Cuando se conoce la mano del grace note:

```text
lR
rL
```

significa respectivamente:

* grace de izquierda + golpe principal de derecha
* grace de derecha + golpe principal de izquierda

La mano principal siempre aparece en mayúscula.

La forma:

```text
gR
```

se reserva para un grace note cuya mano no esté especificada en la partitura original o cuya procedencia no pueda determinarse.

Un flam estándar debe indicar la mano del grace note siempre que esta información esté disponible.

---

## 11. Rolls, buzz y tremolo

Los rolls o redobles que aparecen explícitamente indicados en la partitura deben conservar su carácter de articulación aunque el sticking pueda deducirse.

Se utilizará:

```text
{roll:contenido}
```

para un roll indicado en la partitura.

Ejemplo:

```text
{roll:RLRL}
```

Cuando el tipo de roll sea relevante:

```text
{single:...}
{double:...}
{buzz:...}
```

La presencia de una indicación de roll no debe sustituirse únicamente por una secuencia de `R` y `L`, ya que una secuencia equivalente de golpes individuales no representa necesariamente la misma articulación musical.

---

## 12. Ligaduras de fraseo

Las ligaduras de fraseo se representan mediante `~`.

Ejemplo:

```text
R~L~R~L
```

significa que los golpes forman parte de una misma frase o arco de fraseo.

`~` nunca representa una ligadura de duración.

Para prolongaciones de notas se utiliza exclusivamente `^`.

---

## 13. Articulaciones adicionales

Cuando una articulación no esté cubierta por una notación específica, se utilizará la sintaxis:

```text
{art:tipo}
```

Ejemplos:

```text
R{art:marcato}
L{art:tenuto}
```

Esto permite ampliar el sistema sin reutilizar símbolos ya existentes.

---

## 14. Orden de aplicación de símbolos

Cuando varias marcas afectan a un mismo ataque, se mantiene siempre el siguiente orden:

```text
[grace][mano][articulación dinámica][otras marcas]
```

Ejemplo:

```text
lR!
```

= grace de izquierda + ataque principal de derecha + acento.

Ejemplo:

```text
rL°
```

= grace de derecha + ataque principal de izquierda + ghost note.

Las modificaciones de duración y fraseo se consideran relaciones entre eventos y se escriben de forma independiente.

---

## 15. Separador de compás

`|` = final de compás.

Está reservado exclusivamente para este uso.

Ejemplo:

```text
[RLRL] [RLRL] |
```

Nunca se utiliza `|` para separar grupos dentro del mismo compás.

---

## 16. Compases completamente silenciosos

Un compás completamente silencioso se representa como:

```text
REST |
```

Esto evita tener que escribir todas las subdivisiones cuando no existe ningún ataque.

Para varios compases consecutivos de silencio puede utilizarse:

```text
REST x4
```

cuando la partitura indique explícitamente cuatro compases de silencio.

---

## 17. Repeticiones

Las secciones repetidas se delimitan mediante:

```text
||: ... :||
```

Ejemplo:

```text
||: [RLRL] [RLRL] :|| 
```

Si se especifica un número concreto de repeticiones:

```text
||: [RLRL] [RLRL] :|| x4
```

La repetición se considera una propiedad estructural y no forma parte del sticking.

---

## 18. Primer final y final definitivo

### Primer final

```text
{1st: ...}
```

Se ejecuta durante las repeticiones previas a la última.

### Final definitivo

```text
{final: ...}
```

Se ejecuta únicamente en la última repetición.

Ejemplo:

```text
||: [RLRL] [RLRL] | {1st: [R!L!RL]} :||
{final: [R!L!RL] R}
```

Las instrucciones como "repeat 20 times before final ending" se consideran información estructural y pueden expresarse fuera de los grupos rítmicos:

```text
(repetir 20 veces antes del final)
```

---

## 19. Repetición de compases

Cuando la partitura utiliza un símbolo de repetición de uno o varios compases, se puede representar mediante:

```text
{repeat:1}
```

o:

```text
{repeat:2}
```

según el número de compases que sustituya.

Esto evita confundir una repetición estructural con una secuencia de ataques.

---

## 20. Estructuras de navegación

Cuando una partitura completa utilice indicaciones como:

* D.C.
* D.S.
* al Coda
* al Fine
* Coda
* Fine

se representarán como instrucciones estructurales explícitas:

```text
{DC}
{DS}
{Coda}
{Fine}
{ToCoda}
```

Estas marcas no forman parte del ritmo ni del sticking.

---

# Modelo temporal

La interpretación temporal de la transcripción seguirá estas reglas:

1. Cada evento representa un ataque, silencio o prolongación situado en una posición temporal concreta.
2. El valor indicado por `4:`, `8:`, `16:`, `32:`, etc. determina la unidad temporal del evento o grupo.
3. Los grupos consecutivos se interpretan de izquierda a derecha.
4. Los espacios separan grupos pero no añaden tiempo.
5. Los silencios ocupan tiempo real; no son simplemente caracteres ausentes.
6. Una ligadura `^` prolonga una nota existente y no crea un nuevo ataque.
7. Un grupo irregular `(N/M:...)` redistribuye temporalmente sus eventos dentro del espacio indicado.
8. Las indicaciones de repetición, finales y navegación no alteran el contenido temporal de los compases que describen.

La suma de las duraciones de todos los eventos de un compás debe corresponder exactamente a la duración indicada por su compás musical.

---

# Ejemplos de aplicación

## Ejemplo 1 — semicorcheas y silencio

```text
[R!L!RL] [RLR_] |
```

Dos grupos de cuatro semicorcheas, con acento en las dos primeras notas y silencio final en el segundo grupo.

## Ejemplo 2 — figuras mixtas

```text
[8:RLRL] [16:RLRL] [16:RLRL] |
```

El primer grupo utiliza corcheas y los siguientes semicorcheas.

## Ejemplo 3 — tresillos

```text
(3:RLR) (3:LRL) |
```

Dos grupos de tresillos.

## Ejemplo 4 — quintillo

```text
(5:RLRLR) |
```

## Ejemplo 5 — grupo irregular con relación temporal explícita

```text
(3/4:RLR) |
```

Tres ataques ocupando el espacio temporal de cuatro unidades equivalentes.

## Ejemplo 6 — flam

```text
[lR R L rR] |
```

## Ejemplo 7 — ghost note y acento

```text
[R! L° R L!] |
```

## Ejemplo 8 — ligadura de duración

```text
[R^R L R] |
```

La segunda `R` no constituye un nuevo ataque.

## Ejemplo 9 — roll

```text
{roll:RLRL} |
```

## Ejemplo 10 — final alternativo

```text
||: [RLRL] [RLRL] | {1st: [R!L!RL]} :||
{final: [R!L!RL] R} |
```

---

# Checklist antes de dar una transcripción por terminada

* [ ] ¿Cada ataque tiene correctamente indicado `R` o `L`?
* [ ] ¿Todas las posiciones silenciosas están representadas?
* [ ] ¿Cada grupo tiene el valor rítmico correcto?
* [ ] ¿Los grupos con valor distinto de semicorchea llevan `4:`, `8:`, `16:`, `32:` o el valor correspondiente?
* [ ] ¿Las figuras con puntillo están indicadas correctamente?
* [ ] ¿Todos los tresillos están marcados con `(3:...)`?
* [ ] ¿Los quintillos, seisillos, septillos y otros grupos irregulares están identificados?
* [ ] ¿Los silencios tienen la duración correcta?
* [ ] ¿Los acentos están marcados individualmente con `!`?
* [ ] ¿Las ghost notes están marcadas con `°`?
* [ ] ¿Los grace notes/flams indican correctamente la mano del adorno?
* [ ] ¿Los rolls o buzz están representados como articulaciones y no únicamente como secuencias de golpes?
* [ ] ¿Las ligaduras de duración utilizan `^`?
* [ ] ¿Las ligaduras de fraseo utilizan `~`?
* [ ] ¿Cada compás termina con `|`?
* [ ] ¿Los compases completamente silenciosos están identificados?
* [ ] ¿Los primeros finales y finales definitivos están correctamente diferenciados?
* [ ] ¿Las repeticiones estructurales están representadas?
* [ ] ¿Las indicaciones D.C., D.S., Coda y Fine, si existen, están conservadas?
* [ ] ¿La suma temporal de todos los eventos de cada compás coincide con la duración musical del compás?

Si la respuesta a alguna de estas preguntas es **no**, la transcripción está incompleta o necesita revisión.
