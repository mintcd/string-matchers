## Simple case
There is only one bucket. All patterns have length 8. Super-characters are of length 8 i.e. no super-characters at all.
Each step, 8 positions are or-ed. Each position is or-ed 8 times.
Let the text be $T$ of length $n$ i.e. $T\sim U(\{0,1\}^{8n})$.
Let $X^1,\ldots,X^p\sim U(\{0,1\}^{64})$ be the patterns. We have $X^i\ne X^j$, a.s. for every $1\le i < j \le 8$.

$$\text{cost} = O(n)\times [\text{cost at a position}].$$

Let $Y$ be the length-$8$ sub-text that ends at a position. Then $Y\sim U(\{0,1\}^{64})$.

Define the events
-  $A$: there is a match
-  $B$: there is a positive

We have $A\sub B$.

Define the costs

- $c_1$: cost to find out if there is a positive (constant)
- $c_2=O(p)$: cost to confirm a true positive
- $c_3=O(p)$: cost to reject a false positive

$$\text{cost} = O(n)\times\left(c_1 + \mathbb{P}(A)\times c_2 + \mathbb{P}(A^c, B)\times c_3 + \mathbb{P}(A^c, B^c)\times 0 \right).$$

$$\text{cost} = O(n)\times\left(c_1 + \mathbb{P}(A)\times c_2 + \mathbb{P}(A^c, B)\times c_3 + \mathbb{P}(A^c, B^c)\times 0 \right).$$

$$\text{cost} = O(n)\times\left(c_1 + (\mathbb{P}(A)+\mathbb{P}(A^c, B))\times O(p)\right).$$

$\mathbb{P}(A) = \mathbb{P}(Y=X^1\cup \ldots\cup Y=X^p) = p\times \mathbb{P}(Y=X^1) = \dfrac{p}{2^{64}}$. This is ignorable.

$\mathbb{P}(A^c, B) = \mathbb{P}(B) - \mathbb{P}(A)$
