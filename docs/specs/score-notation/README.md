# Manifiesto de Transcripción de Partituras de Caja

**v5** — formaliza la duración de los grupos irregulares y distingue explícitamente los tresillos de corcheas de los tresillos de semicorcheas. Amplía la v4 manteniendo la sintaxis compacta utilizada para las transcripciones anteriores.

Este documento define un sistema de notación textual para transcribir partituras de caja (snare drum) a texto plano, de forma que una persona pueda reconstruir la partitura original —ritmo, sticking, silencios, articulaciones y estructura— únicamente a partir del texto, sin ambigüedad.

## Principios generales

1. **Cada símbolo debe representar una sola cosa.** No reutilizamos un mismo carácter para significados distintos.
2. **El texto debe ser reversible.** Debe poder reconstruirse la partitura original a partir de la transcripción.
3. **La simplicidad no debe sacrificar precisión.** Si hace falta un símbolo para representar información musical real, se añade.
4. **Un compás = una unidad de texto**, delimitada siempre por `|`.
5. **La notación representa ataques y eventos musicales**, no únicamente letras de sticking.
6. **La información temporal debe ser inequívoca.**
7. **Las articulaciones, las duraciones y el fraseo son conceptos independientes.**
8. **Los grupos irregulares deben indicar su relación temporal cuando no pueda deducirse inequívocamente.**

---

# 1. Sticking base

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

# 2. Agrupación rítmica

## 2.1. Grupos regulares

`[ ... ]` = grupo de notas o eventos que comparten la misma unidad rítmica.

Por defecto, la unidad es la **semicorchea**.

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

---

# 3. Valor de figura explícito

Cuando sea necesario, el valor se indica mediante un prefijo numérico:

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

`16:` puede omitirse cuando el grupo utilice semicorcheas.

Cuando dentro de un mismo compás convivan valores diferentes, se recomienda indicar el valor explícitamente en todos los grupos:

```text
[8:RLRL] [16:RLRL] [16:RLRL]
```

Esto evita depender del contexto.

---

# 4. Figuras con puntillo

Los valores con puntillo utilizan `.` después del valor:

```text
[4.:R]
[8.:RL]
[16.:RLR]
[32.:RLRL]
```

El punto forma parte del valor temporal y no representa una articulación.

---

# 5. Silencios

`_` = silencio de una unidad temporal equivalente al valor indicado por el contexto o el grupo.

Ejemplos:

```text
[16:RLR_]
[8:R_]
```

representan respectivamente una semicorchea de silencio y una corchea de silencio.

El silencio ocupa tiempo real y nunca se omite simplemente una posición silenciosa.

## 5.1. Silencio con puntillo

`_.` = silencio con puntillo.

Ejemplo:

```text
[8:R _.]
```

Cuando sea necesario evitar cualquier ambigüedad, puede indicarse el valor explícitamente:

```text
[8:R 8.:_]
```

---

# 6. Tresillos

Un tresillo es un grupo de **tres ataques que ocupa el espacio temporal de dos unidades equivalentes**.

La forma compacta:

```text
(3:RLR)
```

se utilizará para un **tresillo estándar**, cuando la unidad temporal del tresillo pueda determinarse inequívocamente por el contexto.

Por ejemplo, en un contexto de corcheas:

```text
(3:RLR)
```

= tres corcheas de tresillo ocupando el espacio de dos corcheas.

## 6.1. Tresillos de semicorcheas

Cuando las tres notas ocupen el espacio de **dos semicorcheas**, se utilizará:

```text
(3/2:RLR)
```

Ejemplo:

```text
[16:RLRL] (3/2:RLR) (3/2:LRL) |
```

Aquí cada `(3/2:...)` contiene tres ataques distribuidos sobre el espacio temporal de dos semicorcheas.

Esta distinción es obligatoria cuando un tresillo de semicorcheas pueda confundirse con un tresillo de corcheas.

---

# 7. Forma totalmente explícita de los grupos irregulares

Cuando sea necesario especificar de forma completamente inequívoca tanto el número de ataques como la unidad temporal, puede utilizarse:

```text
(N/M:contenido)
```

donde:

* `N` = número de ataques reales.
* `M` = número de unidades temporales equivalentes que ocupa el grupo.

Ejemplos:

```text
(3/2:RLR)
```

= 3 ataques en el espacio temporal de 2 unidades.

```text
(5/4:RLRLR)
```

= 5 ataques en el espacio temporal de 4 unidades.

```text
(7/4:RLRLRLR)
```

= 7 ataques en el espacio temporal de 4 unidades.

La unidad concreta —corchea, semicorchea, etc.— se determina por el contexto o por una indicación de valor explícita.

---

# 8. Otros grupos irregulares

Además de los tresillos pueden aparecer:

```text
(5/4:RLRLR)
(6/4:RLRLRL)
(7/4:RLRLRLR)
```

para quintillos, seisillos y septillos.

La misma regla se aplica a cualquier otro número de ataques.

---

# 9. Figuras mixtas dentro de un mismo grupo

Cuando dentro de una misma agrupación existan eventos con valores temporales diferentes, cada uno puede especificar su propio valor:

```text
[8:R 16:L 16:R]
```

representa una corchea seguida de dos semicorcheas.

Esta forma se utilizará únicamente cuando sea necesario representar duraciones diferentes dentro del mismo grupo.

---

# 10. Ligaduras de duración

`^` = ligadura de duración.

Ejemplo:

```text
R^R
```

significa que la segunda representación no constituye un nuevo ataque, sino la prolongación de la primera nota.

La ligadura puede atravesar grupos o compases.

Una nota ligada **no debe interpretarse como un segundo golpe**.

---

# 11. Acentos

`!` después de la mano = golpe acentuado.

Ejemplos:

```text
R!
L!
```

Los acentos se indican nota a nota:

```text
[R!L!RL]
```

---

# 12. Ghost notes

`°` después de la mano = ghost note.

Ejemplos:

```text
R°
L°
```

Ejemplo dentro de un grupo:

```text
[R L° R L]
```

---

# 13. Grace notes y flams

Las grace notes se escriben en minúscula.

Cuando se conoce la mano:

```text
lR
rL
```

significa respectivamente:

* grace de izquierda + golpe principal de derecha.
* grace de derecha + golpe principal de izquierda.

La mano principal aparece siempre en mayúscula.

`gR` se reserva para un grace note cuya mano no esté especificada o no pueda determinarse.

---

# 14. Rolls, buzz y tremolo

Los rolls o redobles indicados expresamente en la partitura deben conservar su articulación.

Forma general:

```text
{roll:contenido}
```

Tipos específicos:

```text
{single:contenido}
{double:contenido}
{buzz:contenido}
```

Ejemplo:

```text
{buzz:RLRL}
```

La indicación de roll no se sustituye simplemente por una secuencia de golpes, porque la articulación es información musical independiente.

---

# 15. Ligaduras de fraseo

`~` = ligadura o arco de fraseo.

Ejemplo:

```text
R~L~R~L
```

`~` nunca representa una ligadura de duración.

Para ligaduras de duración se utiliza exclusivamente `^`.

---

# 16. Articulaciones adicionales

Cuando aparezca una articulación que no disponga de símbolo específico:

```text
{art:tipo}
```

Ejemplos:

```text
R{art:marcato}
L{art:tenuto}
```

Esto permite ampliar la notación sin reutilizar símbolos existentes.

---

# 17. Orden de aplicación de símbolos

Cuando varias marcas afectan al mismo ataque, se mantiene este orden:

```text
[grace][mano][articulación dinámica][otras marcas]
```

Ejemplos:

```text
lR!
rL°
```

Las relaciones de duración y fraseo se expresan aparte mediante `^` y `~`.

---

# 18. Separador de compás

`|` = final de compás.

Está reservado exclusivamente para este uso.

Ejemplo:

```text
[RLRL] [RLRL] |
```

Nunca se utiliza `|` para separar grupos dentro del mismo compás.

---

# 19. Compases completamente silenciosos

Un compás completamente silencioso se representa mediante:

```text
REST |
```

Para varios compases consecutivos:

```text
REST x4
```

---

# 20. Repeticiones

Las secciones repetidas se representan mediante:

```text
||: ... :||
```

Ejemplo:

```text
||: [RLRL] [RLRL] :||
```

Cuando exista un número explícito de repeticiones:

```text
||: [RLRL] [RLRL] :|| x4
```

---

# 21. Primer final y final definitivo

Primer final:

```text
{1st: ...}
```

Final definitivo:

```text
{final: ...}
```

Ejemplo:

```text
||: [RLRL] [RLRL] | {1st: [RLRL]} :||
{final: [RLRL] R} |
```

---

# 22. Repetición de compases

Cuando la partitura indique la repetición de uno o varios compases:

```text
{repeat:1}
```

o:

```text
{repeat:2}
```

La repetición estructural no forma parte del sticking.

---

# 23. Estructuras de navegación

Las indicaciones estructurales se representan explícitamente:

```text
{DC}
{DS}
{Coda}
{ToCoda}
{Fine}
```

Estas marcas no forman parte del ritmo ni del sticking.

---

# 24. Modelo temporal

La interpretación temporal sigue estas reglas:

1. Cada ataque representa un evento situado en una posición temporal.
2. El valor de figura determina la duración temporal correspondiente.
3. Los grupos consecutivos se interpretan de izquierda a derecha.
4. Los espacios entre grupos no añaden tiempo.
5. Los silencios ocupan tiempo real.
6. `^` prolonga una nota y no crea un nuevo ataque.
7. Un grupo irregular `(N/M:...)` distribuye sus `N` ataques dentro del espacio temporal correspondiente a `M` unidades equivalentes.
8. Los tresillos de semicorcheas se representan específicamente como `(3/2:...)`.
9. Las repeticiones y finales modifican la estructura de ejecución, pero no la duración interna de los compases.
10. La suma temporal de todos los eventos de un compás debe coincidir exactamente con la duración musical del compás.

---

# 25. Ejemplos

## Semicorcheas normales

```text
[RLRL] [LRLR] |
```

## Corcheas

```text
[8:RLRL] |
```

## Mezcla de corcheas y semicorcheas

```text
[8:RLRL] [16:RLRL] [16:RLRL] |
```

## Tresillos de corchea

```text
(3:RLR) (3:LRL) |
```

## Tresillos de semicorchea

```text
(3/2:RLR) (3/2:LRL) |
```

## Compás mixto con semicorcheas y tresillos de semicorchea

```text
[RLRL] (3/2:RLR) (3/2:LRL) |
```

## Quintillo

```text
(5/4:RLRLR) |
```

## Acentos

```text
[R!L!RL] |
```

## Ghost notes

```text
[R L° R L] |
```

## Flam

```text
[lR R L rL] |
```

## Ligadura

```text
[R^R L R] |
```

---

# Checklist antes de dar una transcripción por terminada

* [ ] ¿Cada ataque tiene correctamente indicado `R` o `L`?
* [ ] ¿Todas las posiciones silenciosas están representadas?
* [ ] ¿Cada grupo tiene el valor rítmico correcto?
* [ ] ¿Las figuras distintas de semicorchea llevan su valor explícito cuando sea necesario?
* [ ] ¿Las figuras con puntillo están indicadas correctamente?
* [ ] ¿Todos los tresillos normales están marcados con `(3:...)`?
* [ ] ¿Los tresillos de semicorchea están marcados con `(3/2:...)`?
* [ ] ¿Los quintillos, seisillos, septillos y demás grupos irregulares indican su relación temporal?
* [ ] ¿Los silencios tienen la duración correcta?
* [ ] ¿Los acentos están marcados con `!`?
* [ ] ¿Las ghost notes están marcadas con `°`?
* [ ] ¿Los grace notes/flams indican correctamente la mano del adorno?
* [ ] ¿Los rolls y buzz están representados como articulaciones?
* [ ] ¿Las ligaduras de duración utilizan `^`?
* [ ] ¿Las ligaduras de fraseo utilizan `~`?
* [ ] ¿Cada compás termina con `|`?
* [ ] ¿Los compases completamente silenciosos están identificados?
* [ ] ¿Los primeros finales y finales definitivos están correctamente diferenciados?
* [ ] ¿Las repeticiones estructurales están representadas?
* [ ] ¿Las indicaciones D.C., D.S., Coda y Fine están conservadas cuando aparecen?
* [ ] ¿La suma temporal de cada compás coincide con su duración musical?

Si alguna respuesta es **no**, la transcripción está incompleta o necesita revisión.
