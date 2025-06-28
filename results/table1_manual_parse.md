# Manual Parse of Table 1

## Raw text from paper:
```
Relationships
equal = condition componentpreference/greater-than > if-then possess
positive-cause + is-a strategy
negative-cause - know warrant-for
attribute location
```

## Parsing attempt 1 (by spacing):
Line 1: equal = | condition | componentpreference/greater-than > | if-then | possess
Line 2: positive-cause + | is-a | strategy
Line 3: negative-cause - | know | warrant-for
Line 4: attribute | location

This gives us: equal, condition, componentpreference/greater-than, if-then, possess, positive-cause, is-a, strategy, negative-cause, know, warrant-for, attribute, location

Wait, "componentpreference/greater-than" doesn't make sense...

## Parsing attempt 2 (by symbols and logic):
- equal =
- condition
- component
- preference/greater-than >
- if-then
- possess
- positive-cause +
- is-a
- strategy
- negative-cause -
- know
- warrant-for
- attribute
- location

This gives us 14 relationships, which matches what was extracted!

## Conclusion
The extraction correctly parsed the poorly formatted table. The original table has:
- 14 relationships (not 13)
- 50 actions

The "condition component" that looked like one item is actually two separate relationships: "condition" and "component"