# Manifiesto de Transcripción de Partituras de Caja

**Versión:** 2
**Estado:** Draft

---

Este documento define el sistema de notación textual que usaremos para transcribir partituras de caja (snare drum) a texto plano, de forma que cualquier persona pueda reconstruir mentalmente la partitura original únicamente a partir del texto, sin ambigüedad.

**v2** — añade reglas para finales alternativos (1st ending / final) y duración de silencios, detectadas al transcribir la hoja "Accented Eighths".

---

# 1. Principios generales

* Cada símbolo debe representar una sola cosa. No reutilizamos un mismo carácter para significados distintos.
* El texto debe ser reversible. Debe poder reconstruirse la partitura (ritmo, sticking, articulación y estructura) solo leyendo el texto.
* La simplicidad no debe sacrificar precisión. Si hace falta un símbolo nuevo para representar un elemento real de la partitura, se añade; no se omite información por comodidad.
* Un compás = una unidad de texto, delimitada siempre por separadores de compás explícitos.

---

# 2. Reglas de notación

## 2.1 Sticking base

`R` = golpe con mano derecha.

`L` = golpe con mano izquierda.

Se escriben en el orden exacto en que se tocan, sin espacios entre golpes de un mismo grupo rítmico.

## 2.2 Agrupación rítmica

`[ ... ]` = agrupación de semicorcheas (subdivisión binaria normal). Ejemplo: `[RLRL]`.

`( 3: ... )` = agrupación de tresillo explícito. Ejemplo: `(3:RLR)`.

Nunca se usa `[ ]` para un tresillo. La marca `3:` es obligatoria siempre que la subdivisión sea ternaria, aunque el contexto ya lo sugiera.

## 2.3 Separador de compás

`|` = fin de compás.

Se reserva exclusivamente para este uso. No se usa para separar grupos dentro de un mismo compás (para eso están los `[ ]`, `( )` o el espacio simple).

## 2.4 Silencios y su duración

`_` = silencio de una subdivisión (por ejemplo, una corchea dentro de un grupo de semicorcheas), ocupando la posición exacta que tendría la nota omitida.

`__` (doble guion bajo) = silencio con puntillo, de duración una subdivisión y media.

Nunca se omite una letra sin sustituirla por el símbolo de silencio correspondiente. El número de caracteres/símbolos dentro de un grupo debe coincidir siempre con el número de pulsos del grupo, haya o no silencio.

Ejemplo sin puntillo: un grupo de semicorcheas con la última nota sustituida por silencio se escribe `[RLR_]`, no `[RLR]`.

Ejemplo con puntillo: si el silencio dura una corchea y media, se escribe `[RL__]` en la posición correspondiente.

## 2.5 Acentos

Mayúscula con signo de exclamación pospuesto `!` = golpe acentuado. Ejemplo: `R!`.

Sin `!` = golpe normal (dinámica estándar, no acentuado).

El acento se marca nota a nota, no por grupo completo, salvo que todo el grupo esté acentuado, en cuyo caso se marca cada nota individualmente igualmente (no se abrevia).

## 2.6 Grace notes / flams / adornos

`g` antepuesto en minúscula a la letra principal = grace note o flam inmediatamente antes de ese golpe. Ejemplo: `gR` significa "adorno + golpe principal en mano derecha".

Si el adorno se toca con la mano contraria a la nota principal (flam estándar), se indica la mano del adorno en minúscula seguida de la principal en mayúscula: `lR` (adorno de mano izquierda + golpe principal de mano derecha), `rL` (adorno de mano derecha + golpe principal de mano izquierda).

Las ligaduras de fraseo que abarcan varias notas (curvas de fraseo, no de flam) se indican con `~` entre las notas afectadas. Ejemplo: `R~L~R~L`.

## 2.7 Finales alternativos (1st ending / final)

`{1st: ... }` = primer final. Se toca durante las repeticiones previas a la última vuelta, antes de saltar de nuevo al inicio de la sección repetida.

`{final: ... }` = final definitivo. Se toca únicamente en la última repetición, sustituyendo al `{1st: ... }`.

Si la partitura indica un número de repeticiones antes del final (ej. "repeat 20 times before final ending"), se anota como comentario aparte, fuera de los corchetes de compás, ya que es una instrucción de repetición y no de sticking.

Ejemplo: `[R!L!RL] [R!L!RL] | {1st: [R!L!RL] [R!L!RL]} {final: [R!L!RL] R__} |` seguido de la nota (repetir 20+ veces antes del final).

## 2.8 Orden de aplicación de símbolos

Cuando coinciden varias marcas sobre la misma nota, el orden fijo de escritura es:

```
[grace][mano][acento]
```

Ejemplo: un flam con acento en mano derecha se escribe `lR!`.

---

# 3. Ejemplo de aplicación

Un compás con dos grupos de semicorcheas (el segundo con un silencio final) seguido de dos tresillos, con acento en las dos primeras notas del compás:

```
[R!L!RL] [RLR_] | (3:RLR) (3:LRL) |
```

Un compás con silencio punteado y final alternativo:

```
[R!L!RL] [R!L!RL] | {1st: [R!L!RL] [R!L!RL]} {final: [R!L!RL] R__} |
```

---

# 4. Checklist antes de dar una transcripción por terminada

* ¿Cada grupo tiene el número correcto de caracteres/símbolos, incluyendo silencios?
* ¿Están marcados todos los tresillos con `(3: ... )`?
* ¿Están marcados todos los acentos con `!`?
* ¿Están marcados todos los adornos/flams con `g` o con la notación de mano contraria en minúscula?
* ¿Hay un `|` en cada final de compás?
* ¿Las ligaduras de fraseo, si existen, están marcadas con `~`?
* ¿Los silencios están marcados con la duración correcta (`_` simple o `__` con puntillo)?
* ¿Si hay primer final y final definitivo, están marcados con `{1st: ... }` y `{final: ... }` respectivamente?

Si la respuesta a alguna de estas preguntas es "no", la transcripción está incompleta.
