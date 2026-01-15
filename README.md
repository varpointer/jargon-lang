# JargonLang
Version 0.21.0 (2025/1/15) 

File extension: .jgl

Contains a lexer and a parser 

types: int, float, str, char, array ( [type] )
# Types
## `int`
An integer type. Just write the integer
## `float`
Floating point type. Any number with a decimal point is a `float`
## `str`
A string of characters surrounded by double-quotes
## `char`
A singular character surrounded by single-quotes
## array `[type]`
A list of elements separatedby commas, surrounded by brackets (`[]`) \
ex:
```
var x: [int] = [2, 5, 8] 
```
# Operations: 
## Addition `a+b`
Adds `a` and `b`
## Subtraction `a-b`
Subtracts `b` from `a`
## Comparisons `a>b`, `a<b`, `a<=b`, `a>=b`
Compares `a` and `b` and returns a result depending on the larger value
## Equality `a==b`
Sees if `a` and `b` have the same value
## Inequality `a!=b`
Sees if `a` and `b` do not have the same value
## Subtraction `a-b`
Subtracts `b` from `a`
## Negation `-a`
Returns the additive inverse of `a`
## Assignment `a=b`
Assigns the value `b` to variable `a`
## Code blocks `{}`
Creates a block of multiple statements separated by semicolons. 
## Function calls `a(b, c)`
Used to call function `a` with arguments in parentheses
# Keywords
## `var`
```
var x: int = 5
```
```
var x: float
```
Used to declare a variable. The type is mandatory, but you dont have to assign a value.
## `func`
```
func f(a: int, b: str) -> int { var x = 5; }
Used to declare a function. You must specify the name, return type and the types of the arguments, but you dont have to add arguments.
## `return`
```
return x;
```
Used to return a value from a function.
## `if`
```if (cond) { code; }```
Used for conditional statements.\ If `cond` is true, `code` is executed
## `elseif`
``` 
if (cond1) { code1; }
elseif (con2) { code2; }
If all previous conditions are false, and `cond2` is true, `code2` is executed
```while (cond) { code; }```
Used for conditional loops.\ `code` gets repeated as long as `cond` is true
## `else` 
```
if (cond1) {code; }
elseif (cond2) {code; }
else {code2}
```
Executes code2 if all previous conditions are false
## `continue`
``` while (cond) continue;```
Control statement used in loops to skip the code after and enter the next iteration of the loop
## `break`
```while (cond) break;```
Control statement used to end a loop
## ```for (init; cond; iter) { code; }```
Used for 3-part loops.\ 
`init` gets executed, then `iter` followed by `code` get repeated as long as `cond` is true\
If `init` or `iter` are omitted, they will be skipped. If `cond` is omitted, it will allways evaluate to true.
# Misc
## Parentheses `(a)`
https://study.com/learn/lesson/parentheses-math-rules-examples.html
## Bitwise OR `a|b`
Performs a bitwise OR operation on `a` and `b`
TODO
## Comment `//text`
Ignores text until the end of the line
## Multiline comment `/*a*/`
Ignores text until the end of the file or `*/`
# Order of operations
Highest priority first
- Assignment (=) 
- Function calls (f())
- Unary operations (-, !, ~)
- Multiplication and division (*, /)
- Binary bitwise operations (|, &, ^)
- Addition and subtraction (+, -)
- Comparisons(>, <, >=, <=)
- Binary logical operations (||, &&)
- Equality and inequality (==, !=)
