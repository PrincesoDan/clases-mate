# Guía de divisiones — dificultad progresiva

**20 ejercicios · sin calculadora**

Los ejercicios están ordenados de menor a mayor dificultad y agrupados en 5 bloques de 4.
No saltes bloques: cada uno prepara el siguiente.

**Instrucciones:**
1. Resuelve con el algoritmo de la división, escribiendo todos los pasos.
2. Cuando la división no sea exacta, escribe el **cociente** y el **resto**.
3. **Verifica siempre** al terminar: `cociente × divisor + resto = dividendo`. Si no calza, hay un error.

---

## Bloque 1 — Dos dígitos ÷ un dígito (exactas)

*Calentamiento. Todas dan resto 0.*

| # | Ejercicio | Cociente | Resto |
|---|---|---|---|
| 1 | 48 : 2 | | |
| 2 | 96 : 3 | | |
| 3 | 84 : 4 | | |
| 4 | 91 : 7 | | |

---

## Bloque 2 — Dos dígitos ÷ un dígito (con resto)

*Aparece el resto. Ojo: el resto siempre debe ser **menor** que el divisor. Si te da igual o mayor, el cociente quedó chico.*

| # | Ejercicio | Cociente | Resto |
|---|---|---|---|
| 5 | 47 : 2 | | |
| 6 | 59 : 4 | | |
| 7 | 86 : 5 | | |
| 8 | 73 : 6 | | |

---

## Bloque 3 — Tres dígitos ÷ un dígito

*Crece el dividendo. El ejercicio 10 tiene una trampa clásica: presta atención cuando una cifra intermedia no alcanza para dividir.*

| # | Ejercicio | Cociente | Resto |
|---|---|---|---|
| 9 | 246 : 3 | | |
| 10 | 618 : 3 | | |
| 11 | 735 : 5 | | |
| 12 | 869 : 7 | | |

---

## Bloque 4 — Tres dígitos ÷ dos dígitos (exactas)

*El salto real de dificultad. Ahora hay que **estimar** cuántas veces cabe el divisor.*

**Estrategia:** redondea el divisor a la decena más cercana para tantear.
Ejemplo: en `156 : 12`, piensa "12 es casi 10, y 10 cabe unas 15 veces en 156" → prueba con 13. Multiplica y ajusta.

| # | Ejercicio | Cociente | Resto |
|---|---|---|---|
| 13 | 156 : 12 | | |
| 14 | 322 : 14 | | |
| 15 | 525 : 21 | | |
| 16 | 672 : 24 | | |

---

## Bloque 5 — Tres dígitos ÷ dos dígitos (con resto)

*Nivel final: estimación + resto. Los divisores son menos "amables".*

| # | Ejercicio | Cociente | Resto |
|---|---|---|---|
| 17 | 187 : 15 | | |
| 18 | 425 : 18 | | |
| 19 | 638 : 27 | | |
| 20 | 947 : 36 | | |

---

## Errores más frecuentes

- **Resto mayor o igual que el divisor.** Significa que el cociente quedó corto. Ejemplo: si en `59 : 4` te dio 13 con resto 7, el 7 todavía contiene un 4 más → el cociente era 14 y el resto 3.
- **Olvidar el cero en el cociente.** Cuando bajas una cifra y el número resultante es menor que el divisor, va un **0** en el cociente y bajas la siguiente cifra. Saltarse ese cero es el error más común de todos (ver ejercicio 10).
- **Restar mal en un paso intermedio.** Un error de resta arrastra toda la división. Por eso conviene verificar al final.
- **Estimar de más y no ajustar.** Si al multiplicar te pasas del número que tienes arriba, baja el tanteo en 1 y prueba de nuevo. Tantear es parte del método, no un error.

---

# Solucionario

| # | Ejercicio | Cociente | Resto | Verificación |
|---|---|---|---|---|
| 1 | 48 : 2 | **24** | 0 | 24 × 2 = 48 |
| 2 | 96 : 3 | **32** | 0 | 32 × 3 = 96 |
| 3 | 84 : 4 | **21** | 0 | 21 × 4 = 84 |
| 4 | 91 : 7 | **13** | 0 | 13 × 7 = 91 |
| 5 | 47 : 2 | **23** | **1** | 23 × 2 + 1 = 47 |
| 6 | 59 : 4 | **14** | **3** | 14 × 4 + 3 = 59 |
| 7 | 86 : 5 | **17** | **1** | 17 × 5 + 1 = 86 |
| 8 | 73 : 6 | **12** | **1** | 12 × 6 + 1 = 73 |
| 9 | 246 : 3 | **82** | 0 | 82 × 3 = 246 |
| 10 | 618 : 3 | **206** | 0 | 206 × 3 = 618 |
| 11 | 735 : 5 | **147** | 0 | 147 × 5 = 735 |
| 12 | 869 : 7 | **124** | **1** | 124 × 7 + 1 = 869 |
| 13 | 156 : 12 | **13** | 0 | 13 × 12 = 156 |
| 14 | 322 : 14 | **23** | 0 | 23 × 14 = 322 |
| 15 | 525 : 21 | **25** | 0 | 25 × 21 = 525 |
| 16 | 672 : 24 | **28** | 0 | 28 × 24 = 672 |
| 17 | 187 : 15 | **12** | **7** | 12 × 15 + 7 = 187 |
| 18 | 425 : 18 | **23** | **11** | 23 × 18 + 11 = 425 |
| 19 | 638 : 27 | **23** | **17** | 23 × 27 + 17 = 638 |
| 20 | 947 : 36 | **26** | **11** | 26 × 36 + 11 = 947 |

---

## Nota para la clase

Esta guía conecta directo con **fracciones** (Semanas 2 y 3 de la planificación): la fracción `a/b` **es** la división `a : b`. Los ejercicios con resto son los que más sirven para eso.

Ejemplo con el ejercicio 6: `59 : 4 = 14` con resto `3`, entonces

$$\frac{59}{4} = 14 + \frac{3}{4} = 14\frac{3}{4} = 14{,}75$$

Vale la pena hacer esa traducción en voz alta con dos o tres ejercicios del Bloque 2 y del Bloque 5, para que el resto deje de ser "lo que sobra" y pase a ser **la parte fraccionaria del resultado**. Ese es exactamente el sentido de fracción que suele faltar.
