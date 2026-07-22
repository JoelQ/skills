# References

Blog posts that inform the principles in this skill. Use these to support a
recommendation when the user asks "why."

## Decomposition

- [Structuring Conditionals in a Wizard](https://thoughtbot.com/blog/structuring-conditionals-in-a-wizard) — Demonstrates separating branching from doing and pushing conditionals up the decision tree in a multi-step form.

## Conditional structure

- [Triangle of Separation](https://thoughtbot.com/blog/triangle-of-separation) — The separation of branching and doing, and why conditionals should be flat dispatchers, not nested implementers.
- [Structuring Conditionals in a Wizard](https://thoughtbot.com/blog/structuring-conditionals-in-a-wizard) — Applying these ideas to a wizard-style controller.

## Boolean simplification

- [Back to Basics: Booleans](https://thoughtbot.com/blog/back-to-basics-booleans) — Recognizing when if/else chains are just identity, negation, `&&`, or `||` in disguise, plus truth tables for complex cases.

## Unnecessary machinery

- [Ruby Memoization and Alternatives](https://thoughtbot.com/blog/ruby-memoization-and-alternatives) — Separating caching from calculation and recognizing when memoization hides the real problem.
- [Iteration as an Anti-Pattern](https://thoughtbot.com/blog/iteration-as-an-anti-pattern) — Why building collections iteratively reimplements standard operations.
- [Avoid Putting Logic in Map Blocks](https://thoughtbot.com/blog/avoid-putting-logic-in-map-blocks) — Pushing block logic to iterated objects to fix feature envy and build richer domain models.
- [Special Cases](https://thoughtbot.com/blog/special-cases) — Eliminating nil-checks and conditional branches through null objects, empty collections, and polymorphism.
