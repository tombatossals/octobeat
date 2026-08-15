# Manifiesto de Transcripción de Partituras de Caja

**v7** — incorpora articulaciones directamente dentro de los grupos rítmicos y formaliza una sintaxis única para representar simultáneamente estructura temporal, densidad, sticking y articulación. Esta versión mantiene el modelo relativo de la v6 y añade una representación más limpia para rolls y otras articulaciones asociadas a un grupo completo.

---

# 1. Principios generales

1. **Cada símbolo debe representar una sola cosa.**
2. **El texto debe ser reversible.** Debe poder reconstruirse la partitura original a partir de la transcripción.
3. **La simplicidad no debe sacrificar precisión.**
4. **Todos los grupos rítmicos utilizan `[ ]`.**
5. **La duración se expresa preferentemente de forma relativa.**
6. **Los grupos irregulares utilizan la misma sintaxis que los grupos normales.**
7. **La articulación puede aplicarse a un ataque individual o a un grupo completo.**
8. **Duración, sticking, articulación y fraseo son conceptos independientes.**
9. **Un compás termina siempre con `|`.**

---

# 2. Sticking base

* `R` = golpe/ataque con mano derecha.
* `L` = golpe/ataque con mano izquierda.

Los ataques se escriben en el orden exacto en que se ejecutan.

No se insertan espacios entre golpes pertenecientes al mismo grupo.

Ejemplo:

```text
RLRL
```

---

# 3. Grupos rítmicos

`[ ... ]` representa un grupo de eventos rítmicos consecutivos.

Ejemplo:

```text
[RLRL]
```

representa cuatro ataques utilizando la unidad temporal base.

Los espacios entre grupos no representan tiempo adicional.

Ejemplo:

```text
[RLRL] [RLRL]
```

representa dos grupos consecutivos.

---

# 4. Unidad temporal base

Todo ejercicio o fragmento de partitura tiene una **unidad temporal base**.

Un grupo sin prefijo:

```text
[RLRL]
```

utiliza esa unidad base.

La unidad base no necesita corresponder obligatoriamente a una figura musical absoluta como negra, corchea o semicorchea.

Esto permite transcribir directamente la estructura rítmica de la partitura sin tener que traducirla previamente a nombres de figuras.

---

# 5. Densidad temporal relativa

La sintaxis:

```text
[N:contenido]
```

indica que el grupo ocupa `1/N` del tiempo que ocuparía el mismo contenido sin prefijo.

Ejemplos:

```text
[LRLR]
[2:LRLR]
[4:LRLR]
```

Significan respectivamente:

* densidad normal;
* doble densidad;
* cuatro veces la densidad normal.

Por ejemplo:

```text
[LRLR] [2:LRLR] [2:LRLR]
```

representa cuatro ataques a velocidad normal seguidos de dos grupos de cuatro ataques al doble de velocidad.

---

# 6. Grupos irregulares

La sintaxis:

```text
[N/M:contenido]
```

representa `N` ataques distribuidos dentro del espacio temporal de `M` unidades normales.

Ejemplos:

```text
[3/2:RLR]
[5/4:RLRLR]
[7/4:RLRLRLR]
```

representan respectivamente:

* tresillo;
* quintillo;
* septillo.

Esta sintaxis describe directamente la relación temporal entre ataques y espacio ocupado.

---

# 7. Tresillos

Un tresillo estándar se representa como:

```text
[3/2:RLR]
```

Es decir:

> tres ataques ocupando el espacio temporal de dos unidades normales.

Todos los tresillos utilizan `[ ]`.

Nunca se utilizan paréntesis para representar tresillos.

Ejemplo:

```text
[3/2:RLR] [3/2:LRL]
```

---

# 8. Densidad frente a grupo irregular

No deben confundirse:

```text
[2:RLRL]
```

con:

```text
[3/2:RLR]
```

El primero representa cuatro ataques comprimidos temporalmente al doble.

El segundo representa tres ataques distribuidos irregularmente en el espacio temporal de dos unidades.

---

# 9. Articulación aplicada a un grupo

Una articulación que afecta al grupo completo se coloca después de la especificación temporal y antes del contenido:

```text
[art:N/M:contenido]
```

donde `art` identifica la articulación.

La forma general es:

```text
[art:contenido]
```

o, cuando existe una relación temporal explícita:

```text
[art:N/M:contenido]
```

Ejemplos:

```text
[roll:9/4:RRLLRRLLR]
[roll:7/4:RRLLRRL]
```

Esto significa respectivamente:

* roll de 9 ataques ocupando el espacio de 4 unidades;
* roll de 7 ataques ocupando el espacio de 4 unidades.

La articulación `roll` forma parte del grupo y no necesita una estructura externa.

---

# 10. Tipos de roll

Cuando la partitura especifica el tipo de roll, se conserva:

```text
[single:contenido]
[double:contenido]
[buzz:contenido]
[openroll:contenido]
```

Para un roll abierto:

```text
[openroll:9/4:RRLLRRLLR]
```

La forma `openroll` se utilizará cuando la fuente indique explícitamente un **open roll**.

Si la partitura indica simplemente un roll:

```text
[roll:9/4:RRLLRRLLR]
```

---

# 11. Rolls y sticking

El contenido de un roll debe conservar el sticking cuando este pueda determinarse.

Por ejemplo:

```text
[openroll:9/4:RRLLRRLLR]
```

No debe simplificarse a:

```text
[openroll]
```

si la secuencia de manos aparece explícitamente en la partitura.

La articulación y el sticking son información independiente.

---

# 12. Articulación individual

Cuando la articulación afecta únicamente a un ataque, se escribe después de la mano:

```text
R!
L°
R{art:marcato}
```

Ejemplos:

```text
R!
L°
```

---

# 13. Acentos

`!` después de la mano = acento.

Ejemplos:

```text
R!
L!
```

En un grupo:

```text
[R!LRL]
```

Los acentos se indican nota por nota.

---

# 14. Ghost notes

`°` después de la mano = ghost note.

Ejemplo:

```text
[R L° R L]
```

---

# 15. Grace notes y flams

Las grace notes utilizan letras minúsculas.

```text
lR
rL
```

significa:

* grace izquierda + ataque principal derecha;
* grace derecha + ataque principal izquierda.

`gR` se reserva para un grace note cuya mano no pueda determinarse.

---

# 16. Ligaduras de duración

`^` = ligadura de duración.

Ejemplo:

```text
R^R
```

La segunda representación no es un nuevo ataque.

---

# 17. Ligaduras de fraseo

`~` = fraseo.

Ejemplo:

```text
R~L~R~L
```

`~` nunca representa prolongación temporal.

---

# 18. Articulaciones adicionales

Cuando la partitura utilice una articulación que no tenga una notación específica:

```text
R{art:tipo}
```

o, para un grupo completo:

```text
[art:contenido]
```

Ejemplo:

```text
[marcato:RLRL]
```

---

# 19. Silencios

`_` = silencio de una posición temporal correspondiente al contexto.

Ejemplo:

```text
[RLR_]
```

Nunca se omite una posición silenciosa sin representarla.

---

# 20. Silencios dentro de grupos comprimidos

Los silencios conservan la densidad temporal del grupo.

Ejemplo:

```text
[2:R_LR]
```

representa un silencio dentro de un grupo ejecutado al doble de densidad.

Cuando el silencio tenga una duración que no pueda determinarse inequívocamente por posición, podrá utilizarse una duración explícita.

---

# 21. Figuras y valores absolutos

Cuando sea necesario conservar el nombre exacto de una figura musical, se permite especificarlo:

```text
[4:R]
[8:R]
[16:R]
[32:R]
```

Esta notación es secundaria.

Para ejercicios basados en relaciones de densidad se recomienda la forma relativa:

```text
[LRLR] [2:LRLR]
```

---

# 22. Figuras con puntillo

Las figuras con puntillo pueden representarse mediante notación absoluta:

```text
[8.:R]
[16.:RL]
```

La notación relativa tendrá prioridad cuando permita representar inequívocamente la estructura temporal.

---

# 23. Separador de compás

`|` = final de compás.

Ejemplo:

```text
[RLRL] [2:RLRL] |
```

---

# 24. Compases completamente silenciosos

```text
REST |
```

Varios compases:

```text
REST x4
```

---

# 25. Repeticiones

```text
||: ... :||
```

Ejemplo:

```text
||: [RLRL] [2:RLRL] :||
```

Con número de repeticiones:

```text
||: [RLRL] [2:RLRL] :|| x4
```

---

# 26. Primer final y final definitivo

```text
{1st: ...}
{final: ...}
```

---

# 27. Repetición de compases

```text
{repeat:1}
{repeat:2}
```

---

# 28. Navegación estructural

```text
{DC}
{DS}
{Coda}
{ToCoda}
{Fine}
```

---

# 29. Modelo temporal

1. Cada grupo ocupa una cantidad concreta de tiempo.
2. Un grupo sin prefijo utiliza la unidad base.
3. `[N:...]` comprime el grupo por un factor `N`.
4. `[N/M:...]` distribuye `N` ataques sobre `M` unidades normales.
5. Los grupos se ejecutan de izquierda a derecha.
6. Los espacios no añaden tiempo.
7. Los silencios ocupan tiempo real.
8. `^` prolonga una nota y no crea un nuevo ataque.
9. `~` representa únicamente fraseo.
10. Una articulación asociada a un grupo no altera su duración salvo que la propia articulación indique lo contrario.
11. La suma temporal de todos los grupos debe coincidir con la duración del compás.

---

# 30. Ejemplos fundamentales

## Grupo normal

```text
[RLRL]
```

## Doble densidad

```text
[2:RLRL]
```

## Tresillo

```text
[3/2:RLR]
```

## Quintillo

```text
[5/4:RLRLR]
```

## Roll abierto de nueve golpes

```text
[openroll:9/4:RRLLRRLLR]
```

## Roll abierto de siete golpes

```text
[openroll:7/4:RRLLRRL]
```

## Grupo con acento

```text
[R!LRL]
```

## Ghost note

```text
[R L° R L]
```

## Flam

```text
[lR R L rL]
```

## Ligadura

```text
[R^R L R]
```

---

# 31. Aplicación a Short Roll Combinations

Un roll abierto de nueve golpes como el de los ejercicios 1–12 se representa:

```text
[openroll:9/4:RRLLRRLLR]
```

Un roll abierto de siete golpes como el de los ejercicios 13–24:

```text
[openroll:7/4:RRLLRRL]
```

La estructura del ejercicio 1, por ejemplo:

```text
[RLRL] [openroll:9/4:RRLLRRLLR] |
```

---

# Checklist antes de dar una transcripción por terminada

* [ ] ¿Cada ataque tiene correctamente `R` o `L`?
* [ ] ¿Todos los silencios están representados?
* [ ] ¿Cada grupo tiene la densidad temporal correcta?
* [ ] ¿Los cambios de densidad utilizan correctamente `N:`?
* [ ] ¿Los tresillos utilizan `[3/2:...]`?
* [ ] ¿Los grupos irregulares utilizan `[N/M:...]`?
* [ ] ¿Las articulaciones de grupo están integradas en `[ ]`?
* [ ] ¿Los rolls indican su tipo cuando la fuente lo especifica?
* [ ] ¿El contenido de los rolls conserva el sticking?
* [ ] ¿Los acentos llevan `!`?
* [ ] ¿Las ghost notes llevan `°`?
* [ ] ¿Los grace notes/flams indican correctamente la mano?
* [ ] ¿Las ligaduras de duración utilizan `^`?
* [ ] ¿Las ligaduras de fraseo utilizan `~`?
* [ ] ¿Las figuras con puntillo están correctamente representadas?
* [ ] ¿Cada compás termina con `|`?
* [ ] ¿Las repeticiones y finales alternativos están representados?
* [ ] ¿La suma temporal de cada compás es correcta?

Si alguna respuesta es **no**, la transcripción está incompleta o necesita revisión.
