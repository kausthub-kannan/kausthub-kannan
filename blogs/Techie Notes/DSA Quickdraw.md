A revision-focused cheatsheet covering **267 LeetCode problems**, grouped by the reusable pattern behind them. Each pattern has one **base problem**, a blueprint, the invariant that makes it work, and a checklist of related problems with only the differences that matter.

**Legend:** 🔑 invariant / key observation · ⚠️ pitfalls · ⏱ complexity of the base problem · `E / M / H` = Easy / Medium / Hard ·

---
## Roadmap

| Section                          | Patterns Covered                                                                       |
| -------------------------------- | -------------------------------------------------------------------------------------- |
| Arrays and Two Pointers          | Converging pointers, sort + converge, reader/writer                                    |
| Sliding Window                   | Longest valid, shortest valid, fixed window                                            |
| Stacks                           | Monotonic stack, greedy digit/char stack, simulation                                   |
| Binary Search                    | Boundary search, search on the answer                                                  |
| Linked Lists                     | Fast/slow, dummy-head rewiring, merge sort                                             |
| Trees                            | Return-value DFS, path backtracking, BST, level order, tree-as-graph                   |
| Heaps and Priority Queues        | Frequency + heap, k-way merge                                                          |
| Backtracking                     | Choose/skip, permutations, segmentation, buckets, grid undo, constraints               |
| Graphs                           | Traversal, flood fill, BFS variants, bipartite, topo sort, Dijkstra, DSU, bridges      |
| Dynamic Programming              | Linear, stock state machine, grid, knapsack, LIS, LCS, interval, game, partition, tree |
| SQL                              | Self-join, anti-join, ranking, conditional aggregation, windows, first-event           |
| **More patterns**                |                                                                                        |
| Hashing and Prefix Sums          | Complement lookup, prefix sum + hashmap, set-based sequences                           |
| Intervals                        | Merge, sort-by-end greedy, sweep line                                                  |
| Greedy                           | Extending frontier, running surplus, slot formulas                                     |
| Top-K and Two Heaps              | Size-k heap, median with two heaps                                                     |
| Tries                            | Basic, wildcard DFS, grid + trie                                                       |
| Matrix Manipulation              | Rotate, zero-marking, spiral                                                           |
| Classic Graph Problems           | Number of Islands, Word Ladder, Course Schedule mapped to patterns; Clone Graph        |
| Linked List Essentials           | Reversal, merging, gap pointer, random-pointer copy                                    |
| Data Structure Design            | LRU/LFU, random-access set, iterators, rate limiting                                   |
| Monotonic Deque                  | Sliding window max/min, prefix-sum deque                                               |
| Minimum Spanning Tree            | Kruskal, Prim                                                                          |
| Tree Traversal and Construction  | Path sum/diameter, BST checks, serialization                                           |
| Binary Search Variants           | Rotated array, 2D matrix, partition search                                             |
| Bit Manipulation                 | XOR, bit counting                                                                      |
| Bitmask and Digit DP             | Subset DP, TSP-style, digit DP                                                         |
| Math and Number Theory           | Fast power, sieve, GCD, modular arithmetic                                             |
| String Algorithms                | Palindromes, KMP, rolling hash, parsing                                                |
| Advanced Structures and Variants | Fenwick tree, limited-stop shortest path, reservoir sampling                           |
| Concurrency Basics               | Ordering and alternation primitives                                                    |

**Suggested revision order:** Arrays → Sliding Window → Stacks → Binary Search → Linked Lists → Trees → Heaps → Backtracking → Graphs → DP → SQL.
Natural progressions: *Binary Search → Search on Answer* · *Basic BFS → Multi-source BFS → State BFS* · *DFS on trees → Backtracking → Memoized DP* · *Kahn's topo sort → DP on DAG*.

---

## Arrays and Two Pointers

Three pointer shapes cover this whole section: pointers that **swap/place from both ends**, pointers that **converge after sorting**, and a **reader/writer** pair moving in one direction.

### AR1 Converging Pointers with Placement

> **Recognition:** Reverse/swap in place, or merge two "ends" of a sequence whose extremes sit at the ends (e.g. squares of a sorted array).

**Core idea:** `l = 0`, `r = n-1`; decide something about the two ends, act, move inward.

**Blueprint:**
1. Initialise `l`, `r` at the ends.
2. Skip or compare according to the problem's rule.
3. Swap / write the winner, move the corresponding pointer(s).

**Base problem:** [Reverse String](https://leetcode.com/problems/reverse-string/) · E

> 🔑 Every position outside `[l, r]` is already final.

⚠️ Squares: write results **from the back** (largest |value| is always at an end).
⏱ Time `O(n)` · Space `O(1)`

- [x] [Reverse String](https://leetcode.com/problems/reverse-string/) · E — Base
- [x] [Reverse Vowels of a String](https://leetcode.com/problems/reverse-vowels-of-a-string/) · E — Each pointer skips non-vowels before swapping
- [x] [Squares of a Sorted Array](https://leetcode.com/problems/squares-of-a-sorted-array/) · E — Compare `abs(a[l])` vs `abs(a[r])`, fill output from the end

### AR2 Sort Then Converge

> **Recognition:** Pairs/triples with a sum or inequality condition; order of elements doesn't matter, only values (so sorting is allowed).

**Core idea:** After sorting, a comparison of `a[l] + a[r]` against a threshold indicates which pointer to move, discarding many pairs at once.

**Blueprint:**
1. Sort.
2. `l = 0`, `r = n-1`.
3. If the pair is too small → `l++`; too big → `r--`; valid → count/record and move per the problem.

**Base problem:** [Max Number of K-Sum Pairs](https://leetcode.com/problems/max-number-of-k-sum-pairs/) · M
Sum `== k` → count, move both; `< k` → `l++`; `> k` → `r--`.

> 🔑 If `a[l] + a[r]` is too small, `a[l]` can't pair with anything `≤ a[r]`, so it is safe to drop.

⚠️ A hashmap gives `O(n)` for this base problem, but the sorted two-pointer idea is what transfers to the others.
⏱ Time `O(n log n)` · Space `O(1)`

- [x] [Max Number of K-Sum Pairs](https://leetcode.com/problems/max-number-of-k-sum-pairs/) · M — Base: exact sum
- [x] [Boats to Save People](https://leetcode.com/problems/boats-to-save-people/) · M — Greedy: heaviest always boards; lightest joins only if it fits (`a[l]+a[r] ≤ limit`)
- [x] [Valid Triangle Number](https://leetcode.com/problems/valid-triangle-number/) · M — Fix the largest side `a[i]`; if `a[l]+a[r] > a[i]` then **all** of `l..r-1` work → add `r-l`, `r--`. `O(n²)`
- [x] [Number of Subsequences That Satisfy the Given Sum Condition](https://leetcode.com/problems/number-of-subsequences-that-satisfy-the-given-sum-condition/) · M — If `a[l]+a[r] ≤ target`, `a[l]` is the min and any subset of the `r-l` elements between is allowed → add `2^(r-l)` (precompute powers, mod `1e9+7`)

### AR3 Reader/Writer Pointers

> **Recognition:** In-place filtering of a sorted array with a "keep at most k" rule, or matching one sequence against another by advancing indices.

**Core idea:** A fast reader scans; a slow writer marks the end of the valid prefix (or the matching position in the second sequence).

**Blueprint:** Write the first `k` elements unconditionally → for each later element `x`, write it only if `x != arr[w-k]` → `w++`.

**Base problem:** [Remove Duplicates from Sorted Array II](https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/) · M

> 🔑 `arr[0..w)` always satisfies the rule; comparing with `arr[w-2]` is enough because the array is sorted.

⏱ Time `O(n)` · Space `O(1)`

- [x] [Remove Duplicates from Sorted Array II](https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/) · M — Base (k = 2)
- [x] [Long Pressed Name](https://leetcode.com/problems/long-pressed-name/) · E — Two sequences: match `name[i]==typed[j]` → both advance; else allow `typed[j]==typed[j-1]` (extra press); else fail. Finish when `i == len(name)`

---

## Sliding Window

All problems here maintain a contiguous window `[l, r]` and a cheap summary of it (count, sum, frequency).

### SW1 Longest Valid Window

> **Recognition:** "Longest subarray/substring with at most k of something."

**Core idea:** Grow `r` always; shrink `l` only while the window is invalid; record the length after fixing.

**Blueprint:**
1. Add `a[r]` to the summary.
2. `while invalid: remove a[l]; l++`.
3. `ans = max(ans, r-l+1)`.

**Base problem:** [Max Consecutive Ones III](https://leetcode.com/problems/max-consecutive-ones-iii/) · M
Summary = number of zeros in window; invalid when `zeros > k`.

> 🔑 Validity is monotone: any sub-window of a valid window is valid, so `l` never needs to move backward.

⏱ Time `O(n)` · Space `O(1)`

- [x] [Max Consecutive Ones III](https://leetcode.com/problems/max-consecutive-ones-iii/) · M — Count of zeros ≤ k
- [x] [Fruit Into Baskets](https://leetcode.com/problems/fruit-into-baskets/) · M — Hashmap of counts; invalid when distinct types > 2 (delete keys at count 0)

### SW2 Shortest Valid Window

> **Recognition:** "Minimum length subarray with sum/property ≥ target", all values positive.

**Core idea:** Expand until valid, then shrink as far as possible while still valid, recording the minimum each time.

**Base problem:** [Minimum Size Subarray Sum](https://leetcode.com/problems/minimum-size-subarray-sum/) · M

> 🔑 Positive numbers make the sum monotone in window size, so the shrink loop is safe.

⚠️ Record the answer **inside** the shrink loop. With negatives this fails (needs prefix sums + monotonic deque).
⏱ Time `O(n)` · Space `O(1)`

- [x] [Minimum Size Subarray Sum](https://leetcode.com/problems/minimum-size-subarray-sum/) · M — Base; return 0 if never valid

### SW3 Fixed-Size Window with Frequency Match

> **Recognition:** Anagram / permutation of a pattern inside a larger string.

**Core idea:** Window length is fixed to `len(p)`; slide by adding the new right char and removing the char that leaves; compare frequency arrays (or track a `matches` counter to avoid the 26-compare).

**Base problem:** [Find All Anagrams in a String](https://leetcode.com/problems/find-all-anagrams-in-a-string/) · M

> 🔑 Two strings are anagrams iff their count arrays are equal; sliding updates counts in `O(1)`.

⏱ Time `O(n)` (26 compares per step) · Space `O(1)`

- [x] [Find All Anagrams in a String](https://leetcode.com/problems/find-all-anagrams-in-a-string/) · M — Base; collect start indices

---

## Stacks

### ST1 Monotonic Stack for Next Greater / Span

> **Recognition:** "Next/previous greater (or smaller) element", "how many consecutive days ≤ today".

**Core idea:** Keep a stack of candidates in monotone order; a new element resolves (pops) every candidate it beats.

**Blueprint:**
1. Stack holds indices with values in decreasing order.
2. For each element, `while stack and a[top] < x: res[pop] = x`.
3. Push the current index.

**Base problem:** [Next Greater Element II](https://leetcode.com/problems/next-greater-element-ii/) · M
Circular array → loop `i` over `0..2n-1`, use `a[i % n]`, push only when `i < n`.

> 🔑 Each element is pushed and popped once → amortised `O(1)` per element.

⏱ Time `O(n)` · Space `O(n)`

- [ ] [Next Greater Element II](https://leetcode.com/problems/next-greater-element-ii/) · M — Base (circular)
- [ ] [Online Stock Span](https://leetcode.com/problems/online-stock-span/) · M — Looks **backward** and is online: stack of `(price, span)`; pop while `top.price ≤ price`, accumulating spans

### ST2 Greedy Monotonic Stack (Lexicographic)

> **Recognition:** "Smallest number/string after removing k digits / duplicates", result must keep original order.

**Core idea:** Build the answer on a stack; if the incoming char is smaller than the top, popping the top makes the result lexicographically smaller (when allowed).

**Base problem:** [Remove K Digits](https://leetcode.com/problems/remove-k-digits/) · M
`while k>0 and top > digit: pop, k--` → push → afterwards drop `k` from the end → strip leading zeros → empty means `"0"`.

> 🔑 The stack is always non-decreasing (as far as removals allow).

⏱ Time `O(n)` · Space `O(n)`

- [ ] [Remove K Digits](https://leetcode.com/problems/remove-k-digits/) · M — Base: budget `k`
- [ ] [Remove Duplicate Letters](https://leetcode.com/problems/remove-duplicate-letters/) · M — No budget; instead pop `top` only if `top > c` **and** `top` appears again later (`last[top] > i`). Skip chars already in stack (`inStack` set)

### ST3 Stack Simulation

> **Recognition:** Nested structure or a sequence of events where the most recent item interacts first.

**Base problem:** [Decode String](https://leetcode.com/problems/decode-string/) · M
On `[` push `(currentString, k)`; on `]` pop and repeat; build multi-digit `k` while reading digits.

> 🔑 The stack saves the "outer context" while the inner one is processed.

⏱ Time `O(output length)` · Space `O(n)`

- [ ] [Decode String](https://leetcode.com/problems/decode-string/) · M — Base: nested contexts
- [ ] [Asteroid Collision](https://leetcode.com/problems/asteroid-collision/) · M — Collide only when `top > 0` and new `< 0`; compare `abs`, equal → both vanish; keep popping while the new one wins

---

## Binary Search

### BS1 Boundary Search on Indices

> **Recognition:** Sorted data, or any array where a yes/no predicate flips once (`F F F T T T`).

**Core idea:** Find the first index where the predicate is true.

**Blueprint:** `lo, hi` → `mid` → if `pred(mid)`: `hi = mid` else `lo = mid+1` → stop at `lo == hi`.

**Base problem:** [Find First and Last Position of Element in Sorted Array](https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/) · M
Run the boundary search twice: first index `≥ target`, and first index `> target` minus 1.

> 🔑 Compare against `target` with the predicate, never test equality mid-loop; that is what keeps the two boundaries distinct.

⏱ Time `O(log n)` · Space `O(1)`

- [ ] [Find First and Last Position of Element in Sorted Array](https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/) · M — Base: two boundaries
- [ ] [Find Peak Element](https://leetcode.com/problems/find-peak-element/) · M — Array isn't sorted; predicate is `nums[mid] > nums[mid+1]` ("we are on a descending slope"). A peak always exists on the uphill side

### BS2 Binary Search on the Answer

> **Recognition:** "Minimise the maximum" / "find the minimum X such that it's possible", with a greedy feasibility check.

**Core idea:** The answer lies in a numeric range; `feasible(x)` is monotone (if `x` works, larger `x` works); binary-search the smallest feasible `x`.

**Blueprint:**
1. Pick bounds: `lo` = obvious lower bound, `hi` = always-feasible value.
2. Write `feasible(x)` greedily in `O(n)`.
3. `feasible(mid)` → `hi = mid`, else `lo = mid+1`.

**Base problem:** [Capacity To Ship Packages Within D Days](https://leetcode.com/problems/capacity-to-ship-packages-within-d-days/) · M
`lo = max(weights)`, `hi = sum(weights)`; `feasible(cap)` = pack greedily, count days ≤ D.

> 🔑 A larger capacity never needs more days, which gives monotonicity.

⚠️ Bounds matter: `lo` below `max(weights)` makes the greedy check meaningless.
⏱ Time `O(n log(sum))` · Space `O(1)`

- [ ] [Capacity To Ship Packages Within D Days](https://leetcode.com/problems/capacity-to-ship-packages-within-d-days/) · M — Base
- [ ] [Minimum Number of Days to Make m Bouquets](https://leetcode.com/problems/minimum-number-of-days-to-make-m-bouquets/) · M — Answer = a day; `feasible(day)` counts runs of `k` adjacent bloomed flowers ≥ `m`. Return `-1` upfront if `m*k > n` (use `long`). Bounds `min..max(bloomDay)`

---

## Linked Lists

### LL1 Fast/Slow and Meeting Pointers

> **Recognition:** Cycle, middle node, or intersection, with `O(1)` space expected.

**Base problem:** [Linked List Cycle II](https://leetcode.com/problems/linked-list-cycle-ii/) · M
Slow moves 1, fast moves 2. When they meet, reset one pointer to head; advance both by 1 → they meet at the cycle entry.

> 🔑 Distance from head to entry equals distance from the meeting point to the entry (mod cycle length).

⏱ Time `O(n)` · Space `O(1)`

- [ ] [Linked List Cycle II](https://leetcode.com/problems/linked-list-cycle-ii/) · M — Base
- [ ] [Palindrome Linked List](https://leetcode.com/problems/palindrome-linked-list/) · E — Fast/slow finds the middle → reverse the second half → compare (optionally restore)
- [ ] [Intersection of Two Linked Lists](https://leetcode.com/problems/intersection-of-two-linked-lists/) · E — No fast/slow; pointers switch to the other head at the end, so both walk `lenA+lenB` and meet at the intersection (or both hit `null`)

### LL2 Dummy Head and Pointer Rewiring

> **Recognition:** The head may change or be deleted; relinking nodes in place.

**Core idea:** Put a `dummy` before the head; keep a `prev` pointer to the last node known to be final; rewire `prev.next`.

**Base problem:** [Remove Duplicates from Sorted List II](https://leetcode.com/problems/remove-duplicates-from-sorted-list-ii/) · M
If `cur.val == cur.next.val`, skip every node with that value and set `prev.next` to the next distinct node; otherwise `prev = cur`.

> 🔑 `prev` only advances when the next node is confirmed to stay.

⏱ Time `O(n)` · Space `O(1)`

- [ ] [Remove Duplicates from Sorted List II](https://leetcode.com/problems/remove-duplicates-from-sorted-list-ii/) · M — Base
- [ ] [Swap Nodes in Pairs](https://leetcode.com/problems/swap-nodes-in-pairs/) · M — `prev.next=b; a.next=b.next; b.next=a; prev=a` per pair
- [ ] [Odd Even Linked List](https://leetcode.com/problems/odd-even-linked-list/) · M — Two chains (odd/even) built in one pass; finally `odd.next = evenHead`

### LL3 Merge Sort on a List

> **Recognition:** Sort a linked list in `O(n log n)`.

- [ ] **Base problem:** [Sort List](https://leetcode.com/problems/sort-list/) · M
Find the middle (fast/slow), cut the list, sort each half recursively, merge two sorted lists.

> 🔑 Lists merge in `O(1)` extra space and can't be random-accessed, so merge sort beats quick sort here.

⚠️ Cut the list (`mid.next = null`) before recursing. Bottom-up merging gives `O(1)` space.
⏱ Time `O(n log n)` · Space `O(log n)` recursion

---

## Trees

### TR1 Return-Value DFS

> **Recognition:** The answer at a node is combined from answers of its children.

- [ ] **Base problem:** [Lowest Common Ancestor of a Binary Tree](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/) · M
Return the node if `root` is null/`p`/`q`. Recurse left and right. If both return non-null, `root` is the LCA; otherwise return whichever is non-null.

> 🔑 A non-null return means "p or q (or their LCA) lives below me".

⏱ Time `O(n)` · Space `O(h)`

### TR2 Root-to-Leaf Path DFS with Backtracking

- [ ] **Base problem:** [Path Sum II](https://leetcode.com/problems/path-sum-ii/) · M
Append the node, subtract from the target; at a leaf with remaining `== 0`, **copy** the path; recurse; pop on return.

> 🔑 One shared path list + undo on exit = no per-call copies.

⚠️ Copy at the leaf, otherwise every result aliases the same list.
⏱ Time `O(n²)` worst (copying paths) · Space `O(h)` besides output

### TR3 BST Navigation and Deletion

- [ ] **Base problem:** [Delete Node in a BST](https://leetcode.com/problems/delete-node-in-a-bst/) · M
Go left/right by comparison. On match: 0 or 1 child → return the other child; 2 children → replace with the in-order successor (min of right subtree) and delete that successor from the right subtree.

> 🔑 In-order successor keeps the BST ordering; recursion returns the new subtree root so parents relink automatically.

⏱ Time `O(h)` · Space `O(h)`

### TR4 In-Place Restructuring

- [ ] **Base problem:** [Flatten Binary Tree to Linked List](https://leetcode.com/problems/flatten-binary-tree-to-linked-list/) · M
For each node with a left child: find the rightmost node of the left subtree, attach `node.right` there, move `left` to `right`, null the left, step right.

> 🔑 The rightmost node of the left subtree is the pre-order predecessor of `node.right`.

⏱ Time `O(n)` · Space `O(1)`

### TR5 Level-Order BFS

> **Recognition:** Answers are organised by depth, or neighbours "in the same level".

**Core idea:** Process the queue one level at a time (`size = len(queue)`), and adapt the work done inside each level.

**Base problem:** [Binary Tree Zigzag Level Order Traversal](https://leetcode.com/problems/binary-tree-zigzag-level-order-traversal/) · M
Standard level order with a direction flag; reverse (or `appendleft`) on alternate levels.

⏱ Time `O(n)` · Space `O(w)` (max width)

- [ ] [Binary Tree Zigzag Level Order Traversal](https://leetcode.com/problems/binary-tree-zigzag-level-order-traversal/) · M — Base
- [ ] [Populating Next Right Pointers in Each Node](https://leetcode.com/problems/populating-next-right-pointers-in-each-node/) · M — Perfect tree: link `left.next = right` and `right.next = node.next.left`, using the already-built `next` of the level above → `O(1)` space
- [ ] [Vertical Order Traversal of a Binary Tree](https://leetcode.com/problems/vertical-order-traversal-of-a-binary-tree/) · H — Tag nodes `(col, row, val)` via BFS/DFS; sort by col, then row, then value (ties at the same cell sort by value). `O(n log n)`

### TR6 Tree as Graph (Parent Map + BFS)

> **Recognition:** Distances from a node in all directions, including upward.

- [ ] **Base problem:** [All Nodes Distance K in Binary Tree](https://leetcode.com/problems/all-nodes-distance-k-in-binary-tree/) · M
DFS to record `parent[node]`; BFS from `target` over `{left, right, parent}` with a visited set; collect nodes at level `K`.

> 🔑 Adding parent edges turns the tree into an undirected graph, so ordinary BFS gives distances.

⏱ Time `O(n)` · Space `O(n)`

### TR7 Exploit Complete-Tree Structure

- [ ] **Base problem:** [Count Complete Tree Nodes](https://leetcode.com/problems/count-complete-tree-nodes/) · E
Compute leftmost depth and rightmost depth. Equal → perfect tree, `2^h - 1`. Otherwise `1 + count(left) + count(right)`.

> 🔑 In a complete tree at least one child subtree is perfect, so only one side recurses deeply.

⏱ Time `O(log² n)` · Space `O(log n)`

---

## Heaps and Priority Queues

### HP1 Frequency Count + Heap

> **Recognition:** "Top k frequent", "order by frequency", "rearrange so equal items aren't adjacent".

**Core idea:** Count frequencies, then use a heap (or bucket sort) keyed by count.

**Base problem:** [Top K Frequent Words](https://leetcode.com/problems/top-k-frequent-words/) · M
Heap keyed by `(-count, word)` so ties break alphabetically; pop `k`.

⚠️ Tie-breaking order must be encoded in the key (or comparator).
⏱ Time `O(n log k)` with a size-k heap, `O(n log n)` with a full heap · Space `O(n)`

- [ ] [Top K Frequent Words](https://leetcode.com/problems/top-k-frequent-words/) · M — Base
- [ ] [Sort Characters By Frequency](https://leetcode.com/problems/sort-characters-by-frequency/) · M — Output all chars grouped by count desc; bucket by frequency gives `O(n)`
- [ ] [Reorganize String](https://leetcode.com/problems/reorganize-string/) · M — Greedy: max-heap; repeatedly take the two most frequent distinct chars (or hold the previous char out one round). Impossible if `max count > (n+1)/2`

### HP2 K-Way Merge / Kth Smallest

- [ ] **Base problem:** [Kth Smallest Element in a Sorted Matrix](https://leetcode.com/problems/kth-smallest-element-in-a-sorted-matrix/) · M
Treat each row as a sorted list. Push `(value, r, c)` for each row's first element in a min-heap; pop `k` times, pushing the right neighbour each time.

> 🔑 The heap always holds the smallest unseen element of each list.

💡 Alternative: binary search on value (BS2) with an `O(n)` staircase count of elements `≤ mid`.
⏱ Time `O(min(n,k) + k log n)` · Space `O(n)`

---

## Backtracking

All patterns share the template: **choose → recurse → undo**. They differ in *what* a choice is and *how* duplicates and dead ends are avoided.

### BT1 Choose/Skip (Index-Driven)

> **Recognition:** Subsets, combinations, or per-element binary decisions.

**Base problem:** [Combinations](https://leetcode.com/problems/combinations/) · M
`dfs(start, path)`: if `len == k` record; for `i in start..n`: add `i`, `dfs(i+1)`, pop. Prune with `i ≤ n-(k-len)+1`.

> 🔑 The `start` index enforces increasing order, which prevents duplicate combinations.

⏱ Time `O(C(n,k)·k)` · Space `O(k)`

- [ ] [Combinations](https://leetcode.com/problems/combinations/) · M — Base
- [ ] [Combination Sum III](https://leetcode.com/problems/combination-sum-iii/) · M — Numbers 1–9, exactly `k` of them, sum `n`; prune when the sum exceeds `n`
- [ ] [Letter Case Permutation](https://leetcode.com/problems/letter-case-permutation/) · M — Binary decision per character (letters: lower/upper; digits: one option); no start-index loop
- [ ] [Maximum Length of a Concatenated String with Unique Characters](https://leetcode.com/problems/maximum-length-of-a-concatenated-string-with-unique-characters/) · M — Include/skip each string; keep a bitmask of used letters, skip a string that overlaps or has internal duplicates

### BT2 Permutations (Used Set)

**Base problem:** [Permutations II](https://leetcode.com/problems/permutations-ii/) · M
Sort; `used[]`; at each depth try every unused element; **skip** `nums[i] == nums[i-1]` when `!used[i-1]`.

> 🔑 Among equal values, enforce that they're used left-to-right, so each distinct permutation appears once.

⏱ Time `O(n · n!)` · Space `O(n)`

- [ ] [Permutations II](https://leetcode.com/problems/permutations-ii/) · M — Base: dedupe
- [ ] [Beautiful Arrangement](https://leetcode.com/problems/beautiful-arrangement/) · M — Fill positions `1..n`; number `i` allowed at `pos` only if `i % pos == 0 or pos % i == 0`. Counts instead of listing; pruning does the work

### BT3 String Segmentation and Expression Building

> **Recognition:** Cut a string into pieces or insert operators between digits; each step picks the next piece length.

**Base problem:** [Restore IP Addresses](https://leetcode.com/problems/restore-ip-addresses/) · M
`dfs(idx, parts)`: try segment lengths 1–3, require value `0..255` and no leading zero; succeed when `parts == 4` and `idx == len(s)`.

⏱ Time bounded by `3^4` splits · Space `O(1)`

- [ ] [Restore IP Addresses](https://leetcode.com/problems/restore-ip-addresses/) · M — Base: fixed number of parts
- [ ] [Word Break II](https://leetcode.com/problems/word-break-ii/) · H — Try each dictionary-word prefix; **memoise** `dfs(start)` → list of sentences (otherwise exponential blow-up)
- [ ] [Expression Add Operators](https://leetcode.com/problems/expression-add-operators/) · H — Choose the next number slice and operator; track `value` and `last` operand so `*` is applied as `value - last + last*cur`. Skip numbers with leading zeros; use `long`

### BT4 Bucket Partitioning

> **Recognition:** Split items into `k` groups of equal sum.

**Base problem:** [Partition to K Equal Sum Subsets](https://leetcode.com/problems/partition-to-k-equal-sum-subsets/) · M
`target = sum/k`. Place each number (sorted descending) into a bucket that still fits.

> 🔑 Prune: if two buckets have the same current sum, trying the second one is redundant; if any item `> target`, fail immediately.

💡 Bitmask DP alternative: `dp[mask]` = leftover in the current bucket.
⏱ Time `O(k · 2^n)` with memo, worst naive `O(k^n)` · Space `O(n)`

- [ ] [Partition to K Equal Sum Subsets](https://leetcode.com/problems/partition-to-k-equal-sum-subsets/) · M — Base: general `k`
- [ ] [Matchsticks to Square](https://leetcode.com/problems/matchsticks-to-square/) · M — Same with `k = 4` (side = perimeter/4)

### BT5 Grid Path with Visit-Undo

- [ ] **Base problem:** [Path with Maximum Gold](https://leetcode.com/problems/path-with-maximum-gold/) · M
Start DFS from every non-zero cell. Mark the cell visited (set to 0), explore 4 directions, take the best, **restore** the cell.

> 🔑 Restoring on exit lets other paths reuse the cell.

⏱ Time ≈ `O(g · 3^g)` (g ≤ 25 gold cells) · Space `O(g)`

### BT6 Constraint Satisfaction

- [ ] **Base problem:** [Sudoku Solver](https://leetcode.com/problems/sudoku-solver/) · H
Keep row/column/box bitmasks. Pick an empty cell (optionally the one with fewest candidates), try digits, recurse, undo; return `true` early on success.

> 🔑 Fail fast: constraint masks make invalid placements `O(1)` to reject.

⏱ Exponential worst case, heavily pruned in practice · Space `O(1)` extra

---

## Graphs

Common ingredients: adjacency list, `visited`, queue/stack. The patterns differ in the **kind of question** (reachability, distance, ordering, connectivity) and in **what a node is** (a vertex, a grid cell, or an abstract state).

### GR1 Connectivity and Reachability

> **Recognition:** "Is there a path?", "how many components?", "can everything be reached?"; edges given or derivable.

**Core idea:** Build adjacency, traverse from a start with a `visited` set, read the answer from what was visited.

**Base problem:** [Find if Path Exists in Graph](https://leetcode.com/problems/find-if-path-exists-in-graph/) · E

> 🔑 Mark visited on **enqueue/entry**, not on pop, to avoid revisits.

⏱ Time `O(V+E)` · Space `O(V+E)`

- [ ] [Find if Path Exists in Graph](https://leetcode.com/problems/find-if-path-exists-in-graph/) · E — Base
- [ ] [Number of Provinces](https://leetcode.com/problems/number-of-provinces/) · M — Count components on an adjacency **matrix** (DSU also works)
- [ ] [Keys and Rooms](https://leetcode.com/problems/keys-and-rooms/) · M — Directed; reachable from room 0 must cover all rooms
- [ ] [Evaluate Division](https://leetcode.com/problems/evaluate-division/) · M — Edges carry weights `a/b` and reverse `b/a`; DFS/BFS **multiplies** weights along the path; unknown variable → `-1`
- [ ] [Detonate the Maximum Bombs](https://leetcode.com/problems/detonate-the-maximum-bombs/) · M — Edges are implicit: `i → j` if `dist² ≤ r_i²` (directed, use integers); DFS from every bomb, take the max reach. `O(n³)`

### GR2 Grid Flood Fill and Islands

> **Recognition:** Regions of connected land cells, with a condition about borders or another grid.

**Base problem:** [Number of Enclaves](https://leetcode.com/problems/number-of-enclaves/) · M
Flood-fill from every border land cell (mark visited/sink), then count the remaining land cells.

> 🔑 Anything reachable from the border is not enclosed, so eliminate those first and what's left is the answer.

⏱ Time `O(mn)` · Space `O(mn)` recursion worst case

- [ ] [Number of Enclaves](https://leetcode.com/problems/number-of-enclaves/) · M — Base: count remaining cells
- [ ] [Number of Closed Islands](https://leetcode.com/problems/number-of-closed-islands/) · M — Sink border-connected land first, then **count components** of what remains
- [ ] [Count Sub Islands](https://leetcode.com/problems/count-sub-islands/) · M — Island in `grid2` counts only if every cell is land in `grid1`; flag a failure while flooding (or sink `grid2` cells where `grid1 == 0` first)
- [ ] [Making A Large Island](https://leetcode.com/problems/making-a-large-island/) · H — Label each component with an id and size; for each `0`, sum sizes of **distinct** neighbouring ids `+1`; if there are no zeros the answer is `n²`

### GR3 BFS Shortest Path (Unweighted)

- [ ] **Base problem:** [Shortest Path in Binary Matrix](https://leetcode.com/problems/shortest-path-in-binary-matrix/) · M
BFS from `(0,0)` over 8 directions; distance = number of BFS levels; `-1` if start or end is blocked.

> 🔑 In an unweighted graph the first time BFS reaches a node is the shortest distance.

⏱ Time `O(mn)` · Space `O(mn)`

### GR4 Multi-Source BFS

> **Recognition:** "Distance to the nearest X" for every cell, or expand from a whole region.

**Core idea:** Put all sources in the queue with distance 0, then run BFS once.

**Base problem:** [01 Matrix](https://leetcode.com/problems/01-matrix/) · M
Enqueue every `0` with distance 0; neighbours that are `1` get `dist+1`.

> 🔑 One BFS from a virtual super-source replaces one BFS per cell.

⏱ Time `O(mn)` · Space `O(mn)`

- [ ] [01 Matrix](https://leetcode.com/problems/01-matrix/) · M — Base
- [ ] [Shortest Bridge](https://leetcode.com/problems/shortest-bridge/) · M — Two phases: DFS to find one island and enqueue **all** its cells; then multi-source BFS until reaching the other island. Answer = number of `0`s crossed

### GR5 BFS on an Implicit State Graph

> **Recognition:** "Minimum number of moves/steps" where nodes are configurations; neighbours are generated rather than read from an edge list.

**Core idea:** Define the **state**, the **neighbour function**, the **start**, and the **goal**. BFS gives the minimum number of moves.

**Base problem:** [Open the Lock](https://leetcode.com/problems/open-the-lock/) · M
State = 4-digit string. Neighbours = turn any wheel ±1 (wrap 9↔0): 8 neighbours. Dead ends are pre-marked visited; if `"0000"` is a dead end, return `-1`.

⏱ Time `O(10⁴ · 8)` · Space `O(10⁴)`

- [ ] [Open the Lock](https://leetcode.com/problems/open-the-lock/) · M — Base
- [ ] [Minimum Genetic Mutation](https://leetcode.com/problems/minimum-genetic-mutation/) · M — Neighbour = change one char to `A/C/G/T` **and** the result must be in the bank
- [ ] [Snakes and Ladders](https://leetcode.com/problems/snakes-and-ladders/) · M — State = square number; map to `(row, col)` with the zig-zag layout; neighbours `+1..+6`, then follow a snake/ladder if present
- [ ] [Shortest Path Visiting All Nodes](https://leetcode.com/problems/shortest-path-visiting-all-nodes/) · H — State = `(node, visitedMask)`; start from **every** `(i, 1<<i)`; goal `mask == full`. Nodes may be revisited with a different mask. `O(n²·2ⁿ)`

### GR6 DFS Path Enumeration in a DAG

- [ ] **Base problem:** [All Paths From Source to Target](https://leetcode.com/problems/all-paths-from-source-to-target/) · M
DFS from `0` carrying the current path; record it when it reaches `n-1`.

> 🔑 Because the graph is a DAG, no `visited` set is needed, and adding one would incorrectly cut valid paths.

⏱ Time `O(2ⁿ · n)` worst case · Space `O(n)` besides output

### GR7 Bipartite Coloring

> **Recognition:** "Split into two groups with no conflicts inside a group", "odd cycle".

**Base problem:** [Is Graph Bipartite?](https://leetcode.com/problems/is-graph-bipartite/) · M
Colour a node, give neighbours the opposite colour (BFS/DFS); a neighbour with the **same** colour means failure. Start from every uncoloured node (graph may be disconnected).

> 🔑 A graph is bipartite iff it has no odd cycle.

⏱ Time `O(V+E)` · Space `O(V)`

- [ ] [Is Graph Bipartite?](https://leetcode.com/problems/is-graph-bipartite/) · M — Base
- [ ] [Possible Bipartition](https://leetcode.com/problems/possible-bipartition/) · M — Build the graph from "dislike" pairs first, then the same check

### GR8 Topological Sort (Kahn)

> **Recognition:** Dependencies/prerequisites; "can everything be built/finished?"; cycle detection in directed graphs; peeling layer by layer.

**Core idea:** Repeatedly process nodes whose remaining in-degree is 0. Nodes never processed are in (or behind) a cycle.

**Base problem:** [Find All Possible Recipes from Given Supplies](https://leetcode.com/problems/find-all-possible-recipes-from-given-supplies/) · M
Edge `ingredient → recipe`; `indegree[recipe] = #ingredients`. Start the queue with supplies; when an item is processed, decrement the in-degree of dependent recipes and enqueue those reaching 0.

> 🔑 In-degree 0 means "all prerequisites satisfied".

⏱ Time `O(V+E)` · Space `O(V+E)`

- [ ] [Find All Possible Recipes from Given Supplies](https://leetcode.com/problems/find-all-possible-recipes-from-given-supplies/) · M — Base
- [ ] [Find Eventual Safe States](https://leetcode.com/problems/find-eventual-safe-states/) · M — **Reverse** the edges and peel from terminal nodes (out-degree 0); safe = nodes that get processed. (DFS with 3-colour cycle detection is equivalent)
- [ ] [Minimum Height Trees](https://leetcode.com/problems/minimum-height-trees/) · M — Undirected: peel **leaves** (degree 1) layer by layer until ≤ 2 nodes remain; those are the centres
- [ ] [Course Schedule IV](https://leetcode.com/problems/course-schedule-iv/) · M — Process in topological order propagating prerequisite sets (`pre[v] = pre[v] ∪ pre[u] ∪ {u}`); with `n ≤ 100`, Floyd–Warshall closure also works

### GR9 Dijkstra and Its Variants

> **Recognition:** Shortest/optimal path with non-negative weights, or a path cost that isn't a plain sum (max edge, product).

**Core idea:** Min-heap on the best known cost; pop the best node; relax neighbours with the problem's own **cost-combine rule**.

**Base problem:** [Path with Maximum Probability](https://leetcode.com/problems/path-with-maximum-probability/) · M
Max-heap on probability; relax `p' = p · edgeProb`; first pop of the target is optimal.

> 🔑 Works whenever extending a path never improves it (probabilities ≤ 1, non-negative costs, max of edges).

⏱ Time `O(E log V)` · Space `O(V+E)`

- [ ] [Path with Maximum Probability](https://leetcode.com/problems/path-with-maximum-probability/) · M — Base: maximise a product
- [ ] [Path With Minimum Effort](https://leetcode.com/problems/path-with-minimum-effort/) · M — **Minimax**: cost of a path = max — height difference — ; relax with `max(cur, diff)` and keep the min. (Binary search + BFS also works)
- [ ] [Minimum Cost to Make at Least One Valid Path in a Grid](https://leetcode.com/problems/minimum-cost-to-make-at-least-one-valid-path-in-a-grid/) · H — Edge cost is 0 if the arrow is followed, 1 if it is changed → **0-1 BFS** with a deque (0 → front, 1 → back), `O(mn)`

### GR10 All-Pairs Shortest Path (Floyd–Warshall)

- [ ] **Base problem:** [Find the City With the Smallest Number of Neighbors at a Threshold Distance](https://leetcode.com/problems/find-the-city-with-the-smallest-number-of-neighbors-at-a-threshold-distance/) · M
`dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])` for `k` outermost; count cities within threshold for each `i`; pick the smallest count, tie → **largest index**.

> 🔑 `k` is the loop-outer "allowed intermediate vertices" dimension.

⏱ Time `O(n³)` · Space `O(n²)` (fine for `n ≤ 100`)

### GR11 Union-Find

> **Recognition:** Merging groups, "are these connected?", counting components, detecting redundant edges.

**Core idea:** `find` with path compression, `union` by size/rank; the answer comes from component structure.

**Base problem:** [Satisfiability of Equality Equations](https://leetcode.com/problems/satisfiability-of-equality-equations/) · M
First union all `==` pairs; then for every `!=` pair, fail if both share a root.

> 🔑 Order matters: apply all equalities before checking any inequality.

⏱ Time `O(n α(n))` · Space `O(1)` for 26 letters

- [ ] [Satisfiability of Equality Equations](https://leetcode.com/problems/satisfiability-of-equality-equations/) · M — Base
- [ ] [Number of Operations to Make Network Connected](https://leetcode.com/problems/number-of-operations-to-make-network-connected/) · M — If `edges < n-1` → `-1`; else answer = `components - 1`
- [ ] [Accounts Merge](https://leetcode.com/problems/accounts-merge/) · M — Union accounts that share an email (map email → first account); group emails by root; sort each group
- [ ] [Most Stones Removed with Same Row or Column](https://leetcode.com/problems/most-stones-removed-with-same-row-or-column/) · M — Union **row** with **column** (offset columns); answer = `stones - components`
- [ ] [Redundant Connection II](https://leetcode.com/problems/redundant-connection-ii/) · H — **Directed**: if a node has two parents, test removing the later candidate edge for a cycle; if no node has two parents, return the edge that closes a cycle

### GR12 Bridges (Tarjan Low-Link)

- [ ] **Base problem:** [Critical Connections in a Network](https://leetcode.com/problems/critical-connections-in-a-network/) · H
DFS records `disc[u]` and `low[u]` (earliest discovery reachable via the subtree plus one back edge). Skip the edge to the parent. Edge `(u,v)` is a bridge iff `low[v] > disc[u]`.

> 🔑 If `v`'s subtree can't reach `u` or above without this edge, removing it disconnects the graph.

⚠️ Depth can reach `10⁵`; consider an iterative DFS.
⏱ Time `O(V+E)` · Space `O(V+E)`

---

## Dynamic Programming

**Every DP pattern below answers four questions:** what does the state mean, what is the transition, what are the base cases, and in what order it is filled. Related problems usually differ only in *one* of these.

### D1 Take/Skip with Lookback

> **Recognition:** Each item/day is either taken (blocking neighbours or covering a window) or skipped.

**State:** `dp[i]` = best result considering the first `i` items/days.
**Transition:** `dp[i] = max(dp[i-1], dp[i-2] + gain[i])` (house robber shape).

**Base problem:** [Delete and Earn](https://leetcode.com/problems/delete-and-earn/) · M
Bucket by value: `gain[v] = v · count(v)`. Taking `v` forbids `v-1` and `v+1`, which is exactly house robber over values.

> 🔑 Reduce the problem to "pick non-adjacent items" by re-indexing.

⏱ Time `O(n + maxVal)` · Space `O(maxVal)` (O(1) with rolling)

- [ ] [Delete and Earn](https://leetcode.com/problems/delete-and-earn/) · M — Base
- [ ] [Minimum Cost For Tickets](https://leetcode.com/problems/minimum-cost-for-tickets/) · M — `dp[d]` = min cost through day `d`; if not a travel day `dp[d] = dp[d-1]`, else min of `dp[d-1]+c1`, `dp[d-7]+c7`, `dp[d-30]+c30` (lookback instead of -2)

### D2 Min/Max over Splits (Coin-Change Style)

**State:** `dp[n]` = best answer for value `n`. **Transition:** try every first part `j` and combine with the remainder.

**Base problem:** [Perfect Squares](https://leetcode.com/problems/perfect-squares/) · M
`dp[0]=0`; `dp[n] = 1 + min(dp[n - k²])` for all `k² ≤ n`. Fill increasing.

⏱ Time `O(n√n)` · Space `O(n)`

- [ ] [Perfect Squares](https://leetcode.com/problems/perfect-squares/) · M — Base: minimise count
- [ ] [Integer Break](https://leetcode.com/problems/integer-break/) · M — Maximise product: `dp[n] = max(j·(n-j), j·dp[n-j])` (either keep a part whole or split further)

### D3 Counting by Step and State

> **Recognition:** "How many ways" after `t` steps; the next step depends on a small current state.

**State:** `dp[step][state]`. **Transition:** sum over allowed previous states. Roll the step dimension.

**Base problem:** [Knight Dialer](https://leetcode.com/problems/knight-dialer/) · M
`dp[s][digit]` = number of sequences of length `s` ending at `digit`; transition via the knight-move table; mod `1e9+7`.

⏱ Time `O(n · 10 · moves)` · Space `O(10)`

- [ ] [Knight Dialer](https://leetcode.com/problems/knight-dialer/) · M — Base
- [ ] [Number of Dice Rolls With Target Sum](https://leetcode.com/problems/number-of-dice-rolls-with-target-sum/) · M — State = `(dice used, sum)`; add `dp[d-1][s-face]` over faces
- [ ] [Domino and Tromino Tiling](https://leetcode.com/problems/domino-and-tromino-tiling/) · M — State = shape of the boundary; collapses to `f(n) = 2·f(n-1) + f(n-3)`

### D4 Subarray DP Ending at i (Kadane-Style)

**State:** `dp[i]` = best subarray **ending exactly at** `i`. **Transition:** extend the previous one or restart.

**Base problem:** [Maximum Sum Circular Subarray](https://leetcode.com/problems/maximum-sum-circular-subarray/) · M
Answer = `max(maxKadane, total - minKadane)`; if all numbers are negative (`maxKadane < 0`), return `maxKadane`.

> 🔑 A wrapping subarray is the total minus a non-wrapping minimum subarray in the middle.

⏱ Time `O(n)` · Space `O(1)`

- [ ] [Maximum Sum Circular Subarray](https://leetcode.com/problems/maximum-sum-circular-subarray/) · M — Base
- [ ] [Arithmetic Slices](https://leetcode.com/problems/arithmetic-slices/) · M — `dp[i] = dp[i-1] + 1` if `a[i]-a[i-1] == a[i-1]-a[i-2]`, else 0; answer = sum of all `dp[i]`

### D5 Multi-Pointer Generation

- [ ] **Base problem:** [Ugly Number II](https://leetcode.com/problems/ugly-number-ii/) · M
`ugly[0]=1`; pointers `p2, p3, p5`; next = min of `ugly[p2]·2`, `ugly[p3]·3`, `ugly[p5]·5`; advance **every** pointer that produced the min (handles duplicates).

⏱ Time `O(n)` · Space `O(n)`

### D6 Stock State Machine

> **Recognition:** Buy/sell with constraints (fee, transaction limit); each day is in a *state* (holding or not, transactions used).

**State:** `hold`, `sold` (or `dp[j][0/1]` for `j` transactions). **Transition:** move between states, paying fees or incrementing the transaction count when you buy.

**Base problem:** [Best Time to Buy and Sell Stock II](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/) · M
`hold = max(hold, sold - p)`, `sold = max(sold, hold + p)` (equivalently, sum every positive daily difference).

⏱ Time `O(n)` · Space `O(1)`

- [ ] [Best Time to Buy and Sell Stock II](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/) · M — Base: unlimited transactions
- [ ] [Best Time to Buy and Sell Stock with Transaction Fee](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/) · M — Subtract the fee when selling (or buying)
- [ ] [Best Time to Buy and Sell Stock III](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/) · H — At most 2 transactions: four states `buy1, sell1, buy2, sell2`
- [ ] [Best Time to Buy and Sell Stock IV](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iv/) · H — General `k`: `buy[j], sell[j]` arrays; if `k ≥ n/2`, it degenerates to Stock II. `O(nk)`

### D7 Grid Path DP

**State:** `dp[i][j]` = best/count to reach `(i,j)`. **Transition:** from top and/or left. **Order:** row-major. **Base:** first row/col.

**Base problem:** [Minimum Path Sum](https://leetcode.com/problems/minimum-path-sum/) · M
`dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])`.

⏱ Time `O(mn)` · Space `O(n)` with a rolling row

- [ ] [Minimum Path Sum](https://leetcode.com/problems/minimum-path-sum/) · M — Base
- [ ] [Unique Paths II](https://leetcode.com/problems/unique-paths-ii/) · M — Count paths; obstacle cell → `dp = 0`
- [ ] [Triangle](https://leetcode.com/problems/triangle/) · M — Parents are `(i-1, j-1)` and `(i-1, j)`; or go bottom-up in place
- [ ] [Minimum Falling Path Sum](https://leetcode.com/problems/minimum-falling-path-sum/) · M — Three parents in the previous row: `j-1, j, j+1` (bounds check)
- [ ] [Dungeon Game](https://leetcode.com/problems/dungeon-game/) · H — **Backward** DP from the bottom-right: `need[i][j] = max(1, min(need[i+1][j], need[i][j+1]) - cell)`. Forward DP fails because the future decides how much HP is needed now

### D8 Square Submatrix DP

**State:** `dp[i][j]` = side of the largest all-ones square whose **bottom-right corner** is `(i,j)`.
**Transition:** if cell is 1: `1 + min(top, left, top-left)`, else 0.

**Base problem:** [Maximal Square](https://leetcode.com/problems/maximal-square/) · M
Answer = `max(dp)²`.

- [ ] [Maximal Square](https://leetcode.com/problems/maximal-square/) · M — Base: answer = max side²
- [ ] [Count Square Submatrices with All Ones](https://leetcode.com/problems/count-square-submatrices-with-all-ones/) · M — `dp[i][j]` also equals the **number** of squares ending at that corner → answer = sum of all `dp`

⏱ Time `O(mn)` · Space `O(n)`

### D9 Layered Multi-Dimensional State

> **Recognition:** A time/step dimension plus positions; the state is bigger than one cell.

**Base problem:** [Cherry Pickup II](https://leetcode.com/problems/cherry-pickup-ii/) · H
Two robots move down the same rows simultaneously: `dp[r][c1][c2]` = best total at row `r`. Each of 9 move combinations; add cherries once if `c1 == c2`.

> 🔑 Processing both robots in lock-step by row makes their order irrelevant.

⏱ Time `O(R · C² · 9)` · Space `O(C²)` rolling

- [ ] [Cherry Pickup II](https://leetcode.com/problems/cherry-pickup-ii/) · H — Base
- [ ] [Out of Boundary Paths](https://leetcode.com/problems/out-of-boundary-paths/) · M — `dp[moves][r][c]` counts paths; going off-grid adds 1 to the count; mod `1e9+7`

### D10 0/1 Knapsack / Subset Sum

> **Recognition:** Each item used at most once; a capacity (or two) constrains choices.

**State:** `dp[cap]` = reachable / best value at capacity `cap`. **Transition:** `dp[c] = max(dp[c], dp[c-w] + v)`. **Order:** iterate capacity **backward** to avoid reusing an item.

**Base problem:** [Last Stone Weight II](https://leetcode.com/problems/last-stone-weight-ii/) · M
Split the stones into two groups with the smallest difference → find the achievable subset sum closest to `total/2`.

> 🔑 Smashing stones is equivalent to assigning each stone a `+` or `-` sign.

⏱ Time `O(n · total/2)` · Space `O(total/2)`

- [ ] [Last Stone Weight II](https://leetcode.com/problems/last-stone-weight-ii/) · M — Base: boolean subset sum
- [ ] [Ones and Zeroes](https://leetcode.com/problems/ones-and-zeroes/) · M — **Two** capacities (zeros, ones): `dp[m][n]`, both dimensions backward; maximise count
- [ ] [Profitable Schemes](https://leetcode.com/problems/profitable-schemes/) · H — Count schemes: `dp[members][profit]` with profit **capped** at `minProfit`; mod `1e9+7`

### D11 Unbounded Knapsack (Counting Orderings)

- [ ] **Base problem:** [Combination Sum IV](https://leetcode.com/problems/combination-sum-iv/) · M
`dp[t] = Σ dp[t - num]`, `dp[0] = 1`. The **target is the outer loop** and the items the inner loop, so different orders count as different sequences.

> 🔑 Loop order decides combinations vs permutations: items outer = combinations; target outer = permutations.

⏱ Time `O(target · n)` · Space `O(target)`

### D12 LIS-Style Chain DP

> **Recognition:** Longest chain where each element can follow a previous one under a pairwise rule.

**State:** `dp[i]` = longest chain ending at `i`. **Transition:** `max(dp[j] + 1)` over `j < i` that can precede `i`. Sort first if the order isn't given.

**Base problem:** [Largest Divisible Subset](https://leetcode.com/problems/largest-divisible-subset/) · M
Sort; `dp[i] = 1 + max dp[j]` where `a[i] % a[j] == 0`; keep `prev[i]` to rebuild the subset.

> 🔑 In a sorted array, divisibility is transitive, so checking against the chain's last element suffices.

⏱ Time `O(n²)` · Space `O(n)`

- [ ] [Largest Divisible Subset](https://leetcode.com/problems/largest-divisible-subset/) · M — Base: reconstruct the chain
- [ ] [Longest String Chain](https://leetcode.com/problems/longest-string-chain/) · M — Sort by length; for each word try deleting each char and look up that predecessor in a hashmap
- [ ] [Number of Longest Increasing Subsequence](https://leetcode.com/problems/number-of-longest-increasing-subsequence/) · M — Track `len[i]` **and** `cnt[i]`; when a longer chain is found, reset the count; when equal, add
- [ ] [Longest Arithmetic Subsequence](https://leetcode.com/problems/longest-arithmetic-subsequence/) · M — State gains a dimension: `dp[i][diff]` = length ending at `i` with common difference `diff` (hashmap per index)
- [ ] [Maximum Length of Pair Chain](https://leetcode.com/problems/maximum-length-of-pair-chain/) · M — Same DP after sorting, but greedy is better: sort by **end** and take whenever `start > lastEnd` (`O(n log n)`)

### D13 LIS via Sort + Binary Search

- [ ] **Base problem:** [Russian Doll Envelopes](https://leetcode.com/problems/russian-doll-envelopes/) · H
Sort by width **ascending**, and for equal widths by height **descending**; then find the LIS of heights using the `tails` array with binary search.

> 🔑 Descending heights on ties prevent two envelopes with the same width from chaining.

⏱ Time `O(n log n)` · Space `O(n)`

### D14 LCS Family

> **Recognition:** Two strings/arrays, the answer relates to what they have in common.

**State:** `dp[i][j]` = answer for prefixes `a[:i]`, `b[:j]`.
**Transition:** `a[i-1]==b[j-1]` → `dp[i-1][j-1]+1`; else `max(dp[i-1][j], dp[i][j-1])`.
**Base:** row/column 0 = 0. **Order:** row-major.

**Base problem:** [Uncrossed Lines](https://leetcode.com/problems/uncrossed-lines/) · M (it **is** LCS on two arrays)

⏱ Time `O(mn)` · Space `O(min(m,n))` with rolling (full table needed for reconstruction)

- [ ] [Uncrossed Lines](https://leetcode.com/problems/uncrossed-lines/) · M — Base
- [ ] [Delete Operation for Two Strings](https://leetcode.com/problems/delete-operation-for-two-strings/) · M — Answer = `m + n - 2·LCS`
- [ ] [Minimum ASCII Delete Sum for Two Strings](https://leetcode.com/problems/minimum-ascii-delete-sum-for-two-strings/) · M — Weighted version: minimise the ASCII sum of deleted chars (or `total - 2·maxCommonAsciiSum`)
- [ ] [Shortest Common Supersequence](https://leetcode.com/problems/shortest-common-supersequence/) · H — Build the LCS table, then **reconstruct** by walking back: emit matching chars once, and the non-matching ones from whichever side the step comes from
- [ ] [Maximum Length of Repeated Subarray](https://leetcode.com/problems/maximum-length-of-repeated-subarray/) · M — **Contiguous** version: on mismatch `dp = 0` (reset), answer = `max(dp)`

### D15 Palindromic Subsequence (Interval)

**State:** `dp[i][j]` = answer for substring `s[i..j]`. **Transition:** `s[i]==s[j]` → `2 + dp[i+1][j-1]`; else `max(dp[i+1][j], dp[i][j-1])`. **Order:** by increasing length (or `i` descending).

**Base problem:** [Longest Palindromic Subsequence](https://leetcode.com/problems/longest-palindromic-subsequence/) · M
(equivalently `LCS(s, reverse(s))`).

⏱ Time `O(n²)` · Space `O(n²)`

- [ ] [Longest Palindromic Subsequence](https://leetcode.com/problems/longest-palindromic-subsequence/) · M — Base
- [ ] [Minimum Insertion Steps to Make a String Palindrome](https://leetcode.com/problems/minimum-insertion-steps-to-make-a-string-palindrome/) · H — Answer = `n - LPS` (characters outside the LPS need a mirror)

### D16 Palindrome Partition and Pattern Matching

Two distinct string DPs that don't fit the families above.

- [ ] [Palindrome Partitioning II](https://leetcode.com/problems/palindrome-partitioning-ii/) · H — Precompute `isPal[i][j]` (`O(n²)`), then `cuts[i] = min(cuts[j-1] + 1)` over `j` with `isPal[j][i]`; `cuts[i]=0` if the whole prefix is a palindrome. (This is also D19 on top of a palindrome table)
- [ ] [Wildcard Matching](https://leetcode.com/problems/wildcard-matching/) · H — `dp[i][j]` = `s[:i]` matches `p[:j]`. `?` or equal char → `dp[i-1][j-1]`; `*` → `dp[i][j-1]` (empty) **or** `dp[i-1][j]` (consume one more char). Base: `dp[0][0]=true`; leading `*`s match empty. `O(mn)`

### D17 Interval DP (Split Point)

> **Recognition:** The answer for a range `[l, r]` is built by choosing a split/last/first element `k` inside it.

**State:** `dp[l][r]`. **Transition:** `min/max/sum over k` of `dp[l][k] + dp[k][r] + cost`. **Order:** by increasing interval length.

**Base problem:** [Minimum Cost to Cut a Stick](https://leetcode.com/problems/minimum-cost-to-cut-a-stick/) · H
Sort cuts, add `0` and `n` as endpoints; `dp[i][j] = min over k in (i,j) (dp[i][k] + dp[k][j]) + (cuts[j] - cuts[i])`.

> 🔑 Think of `k` as the **last** operation on the range; the two sides then become independent.

⏱ Time `O(n³)` · Space `O(n²)`

- [ ] [Minimum Cost to Cut a Stick](https://leetcode.com/problems/minimum-cost-to-cut-a-stick/) · H — Base
- [ ] [Minimum Score Triangulation of Polygon](https://leetcode.com/problems/minimum-score-triangulation-of-polygon/) · M — `k` = third vertex of the triangle on edge `(i,j)`; cost `v[i]·v[k]·v[j]`
- [ ] [Guess Number Higher or Lower II](https://leetcode.com/problems/guess-number-higher-or-lower-ii/) · M — `k` = first guess; `k + max(dp[l][k-1], dp[k+1][r])` minimised (worst-case minimax)
- [ ] [Strange Printer](https://leetcode.com/problems/strange-printer/) · H — `dp[i][j] = dp[i+1][j] + 1`, or merge with any `k` where `s[k]==s[i]`: `dp[i+1][k-1] + dp[k][j]`
- [ ] [Unique Binary Search Trees](https://leetcode.com/problems/unique-binary-search-trees/) · M — `k` = root; `dp[n] = Σ dp[k-1]·dp[n-k]` (Catalan numbers, `O(n²)`)

### D18 Game DP (Minimax)

> **Recognition:** Two players alternate with optimal play; answer is "can first player win" or a score difference.

**Core idea:** Define `dp[state]` = best score **difference** (current player minus opponent) from that state; the opponent's turn becomes a subtraction.

**Base problem:** [Predict the Winner](https://leetcode.com/problems/predict-the-winner/) · M
`dp[i][j] = max(a[i] - dp[i+1][j], a[j] - dp[i][j-1])`; first player wins iff `dp[0][n-1] ≥ 0`.

⏱ Time `O(n²)` · Space `O(n)` rolling

- [ ] [Predict the Winner](https://leetcode.com/problems/predict-the-winner/) · M — Base: pick from either end
- [ ] [Stone Game II](https://leetcode.com/problems/stone-game-ii/) · M — State `(i, M)` = suffix start and current limit; take `X ≤ 2M` piles; use suffix sums: `best = suffix[i] - min over X dp(i+X, max(M,X))`
- [ ] [Can I Win](https://leetcode.com/problems/can-i-win/) · M — State = **bitmask** of used numbers (the remaining total is derived from the mask); memoise win/lose; handle `desiredTotal ≤ 0` and `sum(1..max) < desired` upfront

### D19 Partition DP (Last Segment)

> **Recognition:** Split an array into consecutive segments, each with a cost/score determined by its contents.

**State:** `dp[i]` = best answer for the first `i` items. **Transition:** choose the length of the last segment: `dp[i] = best over j (dp[j] + cost(j+1..i))`.

**Base problem:** [Partition Array for Maximum Sum](https://leetcode.com/problems/partition-array-for-maximum-sum/) · M
Segments of length ≤ k; value of a segment = `max · length`. Keep a running max while extending the segment backward.

⏱ Time `O(nk)` · Space `O(n)`

- [ ] [Partition Array for Maximum Sum](https://leetcode.com/problems/partition-array-for-maximum-sum/) · M — Base
- [ ] [Filling Bookcase Shelves](https://leetcode.com/problems/filling-bookcase-shelves/) · M — Segment = shelf; width must fit; shelf height = max height; **minimise** total height
- [ ] [Minimum Difficulty of a Job Schedule](https://leetcode.com/problems/minimum-difficulty-of-a-job-schedule/) · H — Extra dimension: exactly `d` days → `dp[day][i]`; day cost = max in segment. Return `-1` if `n < d`

### D20 Tree DP

**State:** values returned by the post-order DFS at each node, describing the subtree in a few *states*.

**Base problem:** [House Robber III](https://leetcode.com/problems/house-robber-iii/) · M
Return a pair `(rob, skip)` per node: `rob = val + left.skip + right.skip`; `skip = max(left) + max(right)`.

⏱ Time `O(n)` · Space `O(h)`

- [ ] [House Robber III](https://leetcode.com/problems/house-robber-iii/) · M — Base: 2 states
- [ ] [Binary Tree Cameras](https://leetcode.com/problems/binary-tree-cameras/) · H — 3 states: *has camera / covered without camera / not covered*. Greedy equivalent: put a camera on the parent of an uncovered node; treat `null` as covered

---

## SQL

These aren't algorithms with complexity, but the same logic applies: recognise the shape, then reuse the template.

### SQ1 Self-Join for Row Relationships

> **Recognition:** Compare a row with another row of the same table (manager, previous day, duplicate).

**Base problem:** [Employees Earning More Than Their Managers](https://leetcode.com/problems/employees-earning-more-than-their-managers/) · E
`FROM Employee e JOIN Employee m ON e.managerId = m.id WHERE e.salary > m.salary`.

- [ ] [Employees Earning More Than Their Managers](https://leetcode.com/problems/employees-earning-more-than-their-managers/) · E — Base
- [ ] [Rising Temperature](https://leetcode.com/problems/rising-temperature/) · E — Join on dates one day apart (`DATEDIFF = 1`, or `LAG`)
- [ ] [Delete Duplicate Emails](https://leetcode.com/problems/delete-duplicate-emails/) · E — `DELETE` with a self-join keeping the smaller `id`

### SQ2 Anti-Join (Absence)

- [ ] **Base problem:** [Customers Who Never Order](https://leetcode.com/problems/customers-who-never-order/) · E
`LEFT JOIN Orders ... WHERE Orders.id IS NULL` (or `NOT EXISTS`). ⚠️ `NOT IN` breaks if the subquery returns `NULL`.

### SQ3 Group-Level Filtering

> **Recognition:** Keep rows/groups depending on an aggregate property.

**Base problem:** [Duplicate Emails](https://leetcode.com/problems/duplicate-emails/) · E
`GROUP BY email HAVING COUNT(*) > 1`.

- [ ] [Duplicate Emails](https://leetcode.com/problems/duplicate-emails/) · E — Base
- [ ] [Managers with at Least 5 Direct Reports](https://leetcode.com/problems/managers-with-at-least-5-direct-reports/) · M — Group by `managerId`, `HAVING COUNT ≥ 5`, then join back to get the name
- [ ] [Investments in 2016](https://leetcode.com/problems/investments-in-2016/) · M — Row-level result depends on two group counts: `COUNT(*) OVER (PARTITION BY tiv_2015) > 1` and `COUNT(*) OVER (PARTITION BY lat, lon) = 1`

### SQ4 Ranking and Top-N per Group

> **Recognition:** "Nth highest", "top 3 per department", "rank with ties".

**Base problem:** [Department Highest Salary](https://leetcode.com/problems/department-highest-salary/) · M
`DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC)` in a subquery; filter `rank = 1`.

> 🔑 Use `DENSE_RANK` when ties should share a rank without leaving gaps.

- [ ] [Department Highest Salary](https://leetcode.com/problems/department-highest-salary/) · M — Base
- [ ] [Department Top Three Salaries](https://leetcode.com/problems/department-top-three-salaries/) · H — Filter `rank ≤ 3` (ties count once)
- [ ] [Rank Scores](https://leetcode.com/problems/rank-scores/) · M — `DENSE_RANK()` with no partition
- [ ] [Second Highest Salary](https://leetcode.com/problems/second-highest-salary/) · M — Must return `NULL` if absent → wrap in a subquery/`MAX` or `IFNULL`
- [ ] [Nth Highest Salary](https://leetcode.com/problems/nth-highest-salary/) · M — Function with a parameter: `DENSE_RANK` or `DISTINCT ... LIMIT 1 OFFSET N-1`; compute `N-1` outside the `LIMIT` in MySQL

### SQ5 Conditional Aggregation and CASE Labelling

**Base problem:** [Capital Gain/Loss](https://leetcode.com/problems/capital-gainloss/) · M
`SUM(CASE WHEN operation='Buy' THEN -price ELSE price END)` grouped by stock.

- [ ] [Capital Gain/Loss](https://leetcode.com/problems/capital-gainloss/) · M — Base
- [ ] [Count Salary Categories](https://leetcode.com/problems/count-salary-categories/) · M — Categories with **zero** rows must still appear → `UNION ALL` of three counts (or a category table + `LEFT JOIN`)
- [ ] [Tree Node](https://leetcode.com/problems/tree-node/) · M — `CASE`: `p_id IS NULL` → Root; `id IN (SELECT p_id ...)` → Inner; else Leaf
- [ ] [Trips and Users](https://leetcode.com/problems/trips-and-users/) · H — Filter trips whose client **and** driver are both unbanned; cancellation rate = `AVG(status != 'completed')` (or `SUM(CASE)/COUNT`) per day; round to 2 decimals

### SQ6 Running Totals and Sequences (Window Functions)

**Base problem:** [Last Person to Fit in the Bus](https://leetcode.com/problems/last-person-to-fit-in-the-bus/) · M
`SUM(weight) OVER (ORDER BY turn)` as running total; keep rows `≤ 1000`; take the last by `turn`.

- [ ] [Last Person to Fit in the Bus](https://leetcode.com/problems/last-person-to-fit-in-the-bus/) · M — Base
- [ ] [Restaurant Growth](https://leetcode.com/problems/restaurant-growth/) · M — Sliding 7-day window: aggregate per day first, then `SUM(...) OVER (ORDER BY day ROWS 6 PRECEDING)`; drop the first 6 rows
- [ ] [Consecutive Numbers](https://leetcode.com/problems/consecutive-numbers/) · M — Three equal values in consecutive ids: `LAG`/`LEAD`, or three self-joins on `id`, `id+1`, `id+2`

### SQ7 First Event / Latest Before a Date

> **Recognition:** Per entity, the earliest (or latest-as-of) record, then something related to it.

**Base problem:** [Product Sales Analysis III](https://leetcode.com/problems/product-sales-analysis-iii/) · M
Per product find `MIN(year)`, then join (or `IN`) back to get that year's `quantity` and `price`.

- [ ] [Product Sales Analysis III](https://leetcode.com/problems/product-sales-analysis-iii/) · M — Base
- [ ] [Immediate Food Delivery II](https://leetcode.com/problems/immediate-food-delivery-ii/) · M — First order per customer (`MIN(order_date)`), then % where `order_date = customer_pref_delivery_date`
- [ ] [Game Play Analysis IV](https://leetcode.com/problems/game-play-analysis-iv/) · M — First login per player, then check a login exactly the next day; fraction of players
- [ ] [Product Price at a Given Date](https://leetcode.com/problems/product-price-at-a-given-date/) · M — Latest change `≤ cutoff` per product; products with no change by then default to price `10` (`UNION` or `LEFT JOIN` with `COALESCE`)

### SQ8 UNION-Based Reshaping

**Base problem:** [Friend Requests II: Who Has the Most Friends](https://leetcode.com/problems/friend-requests-ii-who-has-the-most-friends/) · M
Stack `requester_id` and `accepter_id` with `UNION ALL` so each friendship counts for both sides; `GROUP BY id`, `ORDER BY COUNT DESC LIMIT 1`.

- [ ] [Friend Requests II: Who Has the Most Friends](https://leetcode.com/problems/friend-requests-ii-who-has-the-most-friends/) · M — Base
- [ ] [Movie Rating](https://leetcode.com/problems/movie-rating/) · M — Two independent "top 1" queries (most ratings by user; best average rating in Feb 2020 per movie), each with deterministic **lexicographic** tie-breaks, combined with `UNION ALL`

---

# More Patterns for Revision

The sections below cover additional patterns that recur frequently across practice sets. `(P)` marks LeetCode Premium problems.

---

## Hashing and Prefix Sums

### HS1 Complement Lookup

> **Recognition:** "Find two items with a relationship", or "group items that are equivalent".

**Core idea:** Store what has been seen in a map; for each new item, look up what it needs (or its canonical key).

**Base problem:** [Two Sum](https://leetcode.com/problems/two-sum/) · E
For each `x`, check `target - x` in the map, **then** insert `x` (so an element isn't paired with itself).

⏱ Time `O(n)` · Space `O(n)`

- [ ] [Two Sum](https://leetcode.com/problems/two-sum/) · E — Base
- [ ] [Group Anagrams](https://leetcode.com/problems/group-anagrams/) · M — Canonical key = sorted string or a 26-count tuple; group by key

### HS2 Prefix Sum with Hashmap

> **Recognition:** "Number/length of subarrays with sum (or property) equal to / divisible by k", especially with **negative numbers** (sliding window fails).

**Core idea:** Subarray `(i, j]` has sum `k` iff `prefix[j] - prefix[i] = k`. Track how many times each prefix value has occurred.

**Blueprint:**
1. `count = {0: 1}`, `prefix = 0`.
2. For each `x`: `prefix += x`; `ans += count[prefix - k]`; `count[prefix] += 1`.

**Base problem:** [Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) · M

> 🔑 Seed `count[0] = 1`, so subarrays starting at index 0 are counted.

⏱ Time `O(n)` · Space `O(n)`

- [ ] [Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) · M — Base: count
- [ ] [Contiguous Array](https://leetcode.com/problems/contiguous-array/) · M — Map `0 → -1`, `1 → +1`; **longest** subarray with sum 0 → store the **first** index of each prefix, answer = `i - first[prefix]`
- [ ] [Subarray Sums Divisible by K](https://leetcode.com/problems/subarray-sums-divisible-by-k/) · M — Key = prefix `mod k`, normalised `((p % k) + k) % k`; equal remainders pair up

### HS3 Set-Based Sequence Start

- [ ] **Base problem:** [Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/) · M
Put everything in a set. Only start counting from `x` where `x - 1` is **not** in the set, then extend upward.

> 🔑 Each sequence is walked exactly once (from its start), so the total work is `O(n)` despite the inner loop.

⏱ Time `O(n)` · Space `O(n)`

### HS4 Prefix and Suffix Products

- [ ] **Base problem:** [Product of Array Except Self](https://leetcode.com/problems/product-of-array-except-self/) · M
Pass 1 left→right: `res[i] = product of everything to the left`. Pass 2 right→left: multiply by a running product of everything to the right. No division, so zeros are fine.

⏱ Time `O(n)` · Space `O(1)` extra

---

## Intervals

### IV1 Sort by Start and Merge

> **Recognition:** Combine overlapping ranges, or insert a range into an existing set.

**Base problem:** [Merge Intervals](https://leetcode.com/problems/merge-intervals/) · M
Sort by start; if `cur.start ≤ last.end`, set `last.end = max(last.end, cur.end)`; else append.

> 🔑 After sorting by start, an interval can only overlap the **last** merged one.

⏱ Time `O(n log n)` · Space `O(n)`

- [ ] [Merge Intervals](https://leetcode.com/problems/merge-intervals/) · M — Base
- [ ] [Insert Interval](https://leetcode.com/problems/insert-interval/) · M — Already sorted → no sort: copy all intervals ending before the new one, merge all overlapping ones into it, copy the rest. `O(n)`

### IV2 Sort by End and Keep Greedily

> **Recognition:** "Maximum number of non-overlapping intervals" / "minimum removals" / "minimum arrows".

**Core idea:** Sort by **end**; always keep the interval that finishes earliest, since it leaves the most room.

**Base problem:** [Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/) · M
Keep an interval if `start ≥ lastEnd`, updating `lastEnd`; answer = `n - kept`.

⚠️ Sorting by start gives a wrong greedy here.
⏱ Time `O(n log n)` · Space `O(1)` extra

- [ ] [Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/) · M — Base
- [ ] [Minimum Number of Arrows to Burst Balloons](https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/) · M — Shoot at the first balloon's **end**; start a new arrow when `start > lastEnd` (touching counts as overlapping, so `>` not `≥`)

### IV3 Sweep Line for Overlap Counts

> **Recognition:** "Maximum simultaneous X": rooms, passengers, active events.

**Core idea:** Turn intervals into `+1` at start and `-1` at end events; sort and sweep, tracking the running count. Or sort by start and keep a min-heap of end times.

**Base problem:** [Meeting Rooms II](https://leetcode.com/problems/meeting-rooms-ii/) (P) · M
Sort by start; pop heap tops with `end ≤ start` (room freed); push the new end; answer = max heap size.

⏱ Time `O(n log n)` · Space `O(n)`

- [ ] [Meeting Rooms II](https://leetcode.com/problems/meeting-rooms-ii/) (P) · M — Base
- [ ] [Car Pooling](https://leetcode.com/problems/car-pooling/) · M — Difference array over stops (`+passengers` at pickup, `-passengers` at drop-off); check no prefix exceeds capacity

---

## Greedy

### GD1 Extending the Frontier

> **Recognition:** "Can I reach the end?", "minimum jumps", "split into the fewest segments"; each element extends how far you can go.

**Core idea:** Track the farthest reachable position; on reaching the end of the current region, commit to the next one.

**Base problem:** [Jump Game](https://leetcode.com/problems/jump-game/) · M
`maxReach = max(maxReach, i + nums[i])`; if `i > maxReach` at any point → unreachable.

⏱ Time `O(n)` · Space `O(1)`

- [ ] [Jump Game](https://leetcode.com/problems/jump-game/) · M — Base: feasibility
- [ ] [Jump Game II](https://leetcode.com/problems/jump-game-ii/) · M — BFS in disguise: `curEnd` = end of current level, `farthest` = best next; when `i == curEnd` → `jumps++`, `curEnd = farthest`
- [ ] [Partition Labels](https://leetcode.com/problems/partition-labels/) · M — `end = max(last[c])` over chars in the current segment; cut when `i == end`

### GD2 Running Surplus with Reset

- [ ] **Base problem:** [Gas Station](https://leetcode.com/problems/gas-station/) · M
If `total gas < total cost` → `-1`. Otherwise run a tank balance; when it goes negative at `i`, restart from `i + 1`.

> 🔑 If starting at `s` fails at `k`, no station between `s` and `k` can succeed (they'd arrive with even less fuel), so skip them all.

⏱ Time `O(n)` · Space `O(1)`

### GD3 Slot Counting Formula

- [ ] **Base problem:** [Task Scheduler](https://leetcode.com/problems/task-scheduler/) · M
Let `f` = max task frequency, `m` = number of tasks with that frequency. Time = `max(len(tasks), (f - 1) · (n + 1) + m)`.

> 🔑 The most frequent task defines `f-1` gaps of width `n+1`; every other task fits inside those gaps, or the answer is simply the task count.

⏱ Time `O(len)` · Space `O(1)`

### GD4 Two-Pass Constraints

- [ ] **Base problem:** [Candy](https://leetcode.com/problems/candy/) · H
Pass left→right to satisfy "higher than left neighbour", pass right→left with `max` to satisfy "higher than right neighbour". Sum.

> 🔑 Two independent one-sided constraints can be satisfied separately and combined with `max`.

⏱ Time `O(n)` · Space `O(n)`

---

## Top-K and Two Heaps

### TH1 Size-K Heap

**Core idea:** To keep the k largest, use a **min**-heap of size k (evict the smallest). To keep the k smallest, use a max-heap of size k.

**Base problem:** [Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/) · M
Push each element; pop when size exceeds `k`; the top is the answer. Quickselect gives average `O(n)`.

⏱ Time `O(n log k)` · Space `O(k)`

- [ ] [Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/) · M — Base
- [ ] [K Closest Points to Origin](https://leetcode.com/problems/k-closest-points-to-origin/) · M — Max-heap of size `k` on squared distance (no sqrt needed)

### TH2 Two Heaps for Median

> **Recognition:** Median or "middle element" of a changing collection.

**Base problem:** [Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/) · H
Max-heap `lo` (lower half) and min-heap `hi` (upper half). Add to `lo`, move `lo`'s top to `hi`, then rebalance so `len(lo) ≥ len(hi)` and differ by ≤ 1. Median = `lo.top` or the average of both tops.

> 🔑 Every element in `lo` ≤ every element in `hi`, and sizes differ by at most 1.

⏱ Time `O(log n)` add, `O(1)` median · Space `O(n)`

- [ ] [Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/) · H — Base
- [ ] [Sliding Window Median](https://leetcode.com/problems/sliding-window-median/) · H — Elements leave the window → needs lazy deletion (hash of pending removals) or an ordered multiset

---

## Tries

### TE1 Basic Trie

> **Recognition:** Many prefix queries, autocomplete, "shortest/longest prefix that is a word".

**Base problem:** [Implement Trie (Prefix Tree)](https://leetcode.com/problems/implement-trie-prefix-tree/) · M
Node = `children[26]` + `isWord`. `insert`/`search`/`startsWith` walk one char per step.

⏱ Time `O(L)` per operation · Space `O(total chars)`

- [ ] [Implement Trie (Prefix Tree)](https://leetcode.com/problems/implement-trie-prefix-tree/) · M — Base
- [ ] [Replace Words](https://leetcode.com/problems/replace-words/) · M — For each word, walk the trie and stop at the first `isWord` node (shortest root)

### TE2 Trie with Wildcard DFS

- [ ] **Base problem:** [Design Add and Search Words Data Structure](https://leetcode.com/problems/design-add-and-search-words-data-structure/) · M
Search recursively; a `.` branches into **all** children, a letter follows one child.

⚠️ Worst case with many wildcards is exponential in the wildcard count; typical inputs are small.

### TE3 Trie plus Grid DFS

> **Recognition:** Find many dictionary words in a grid (running Word Search once per word is too slow).

- [ ] **Base problem:** [Word Search II](https://leetcode.com/problems/word-search-ii/) · H
Build a trie of all words. DFS from each cell while walking the trie; stop when the current prefix isn't in the trie. At a node with a stored word, record it and clear it (avoids duplicates). Prune empty trie branches.

> 🔑 The trie shares prefixes, so one DFS searches for all words at once.

⏱ Time `O(mn · 4 · 3^(L-1))` worst case · Space `O(total chars)`

---

## Matrix Manipulation

### MX1 In-Place Matrix Transforms

**Base problem:** [Rotate Image](https://leetcode.com/problems/rotate-image/) · M
Clockwise 90°: **transpose**, then **reverse each row**. (Counter-clockwise: transpose, then reverse each column.)

⏱ Time `O(n²)` · Space `O(1)`

- [ ] [Rotate Image](https://leetcode.com/problems/rotate-image/) · M — Base
- [ ] [Set Matrix Zeroes](https://leetcode.com/problems/set-matrix-zeroes/) · M — Use the first row and first column as marker storage; track separately whether the first row/column themselves had a zero. `O(1)` space

### MX2 Boundary Traversal

- [ ] **Base problem:** [Spiral Matrix](https://leetcode.com/problems/spiral-matrix/) · M
Maintain `top, bottom, left, right`; walk the four edges, shrinking after each.

⚠️ Re-check `top ≤ bottom` and `left ≤ right` before the third and fourth legs, or single-row/column matrices duplicate elements.
⏱ Time `O(mn)` · Space `O(1)` besides output

---

## Classic Graph Problems

These are frequently practised classics. Most map to patterns covered earlier; only one needs a new pattern.

### Classic Problems Mapped to Existing Patterns

- [ ] [Number of Islands](https://leetcode.com/problems/number-of-islands/) · M — GR2 — Count flood-fill starts
- [ ] [Rotting Oranges](https://leetcode.com/problems/rotting-oranges/) · M — GR4 — Multi-source BFS, one level = one minute; return `-1` if fresh oranges remain
- [ ] [Course Schedule](https://leetcode.com/problems/course-schedule/) · M — GR8 — Cycle check: processed count `== n`
- [ ] [Course Schedule II](https://leetcode.com/problems/course-schedule-ii/) · M — GR8 — Return the Kahn processing order (empty if a cycle)
- [ ] [Word Ladder](https://leetcode.com/problems/word-ladder/) · H — GR5 — Bucket words by wildcard pattern (`h*t`) to generate neighbours fast; bidirectional BFS optimises
- [ ] [Pacific Atlantic Water Flow](https://leetcode.com/problems/pacific-atlantic-water-flow/) · M — GR2 — Flood **inward** (uphill) from each ocean's border, intersect the two reachable sets

### GR13 Clone Graph with Copy Map

- [ ] **Base problem:** [Clone Graph](https://leetcode.com/problems/clone-graph/) · M
DFS/BFS with `map: old → new`. On first visit create the clone and **register it in the map before recursing** into neighbours; later visits just return `map[node]`.

> 🔑 The map is both the visited set and the way to wire cycles correctly.

⏱ Time `O(V+E)` · Space `O(V)`

---

## Linked List Essentials

### LE1 Reversal Patterns

**Base problem:** [Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/) · E
`prev = null`; loop: `next = cur.next; cur.next = prev; prev = cur; cur = next`.

⏱ Time `O(n)` · Space `O(1)`

- [ ] [Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/) · E — Base
- [ ] [Reorder List](https://leetcode.com/problems/reorder-list/) · M — Middle (LL1) → reverse second half → interleave
- [ ] [Reverse Nodes in k-Group](https://leetcode.com/problems/reverse-nodes-in-k-group/) · H — Check `k` nodes exist; reverse that block; reconnect to the previous tail and next block; leave a short tail untouched

### LE2 Merging Lists

**Base problem:** [Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/) · E
Dummy head + tail pointer; attach the smaller head each step; append the leftover list.

- [ ] [Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/) · E — Base. `O(m+n)`
- [ ] [Merge k Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) · H — Min-heap of the `k` heads, or divide-and-conquer pairwise merging. `O(N log k)`

### LE3 Gap Pointer

- [ ] **Base problem:** [Remove Nth Node From End of List](https://leetcode.com/problems/remove-nth-node-from-end-of-list/) · M
Dummy head; advance `fast` by `n + 1`; move `fast` and `slow` together until `fast` is null; `slow.next = slow.next.next`.

> 🔑 Keeping a fixed gap of `n` turns "from the end" into "from the front".

⏱ Time `O(n)` · Space `O(1)`

### LE4 Copy with Random Pointer

- [ ] **Base problem:** [Copy List with Random Pointer](https://leetcode.com/problems/copy-list-with-random-pointer/) · M
Hashmap `old → new` in two passes (create nodes, then set `next`/`random`). `O(1)` space version: interleave copies after each original, set `copy.random = orig.random.next`, then split the lists.

⏱ Time `O(n)` · Space `O(n)` (or `O(1)` interleaved)

---

## Data Structure Design

### DS1 Hashmap plus Linked List

> **Recognition:** `O(1)` get/put **and** an ordering (recency, frequency).

**Base problem:** [LRU Cache](https://leetcode.com/problems/lru-cache/) · M
Hashmap `key → node` + doubly linked list ordered by recency (dummy head and tail). `get`: move node to front. `put`: update/insert at front; evict the tail's predecessor when over capacity.

> 🔑 The map gives `O(1)` lookup; the list gives `O(1)` reorder and eviction.

⏱ `O(1)` per operation · Space `O(capacity)`

- [ ] [LRU Cache](https://leetcode.com/problems/lru-cache/) · M — Base
- [ ] [LFU Cache](https://leetcode.com/problems/lfu-cache/) · H — `key → (value, freq)`, `freq → ordered list of keys`, plus `minFreq`; when the `minFreq` bucket empties after a touch, `minFreq++`. New key resets `minFreq = 1`

### DS2 Hashmap plus Array for Random Access

- [ ] **Base problem:** [Insert Delete GetRandom O(1)](https://leetcode.com/problems/insert-delete-getrandom-o1/) · M
Array of values + map `value → index`. Delete: swap the target with the last element, update that element's index, pop.

> 🔑 Swap-with-last makes array deletion `O(1)`.

### DS3 Smaller Design Patterns

- [ ] [Min Stack](https://leetcode.com/problems/min-stack/) · M — Store `(value, minSoFar)` on each push
- [ ] [Time Based Key-Value Store](https://leetcode.com/problems/time-based-key-value-store/) · M — Per key: list of `(timestamp, value)` (timestamps arrive increasing) → binary search for the last timestamp `≤ t`
- [ ] [Binary Search Tree Iterator](https://leetcode.com/problems/binary-search-tree-iterator/) · M — Controlled in-order with a stack of left spine; amortised `O(1)` `next`, `O(h)` space
- [ ] [Flatten Nested List Iterator](https://leetcode.com/problems/flatten-nested-list-iterator/) · M — Stack of iterators (or reversed list); in `hasNext`, unwrap until an integer is on top
- [ ] [Logger Rate Limiter](https://leetcode.com/problems/logger-rate-limiter/) (P) · E — Map `message → next allowed timestamp`. Real rate limiters generalise to sliding window log, token bucket, or fixed window counters

---

## Monotonic Deque

### MD1 Sliding Window Extremum

> **Recognition:** Max/min over every window, or a window condition involving max − min, or subarray sums with **negatives**.

**Core idea:** Keep a deque of indices whose values are monotone; the front is always the current extreme.

**Blueprint:**
1. Pop front if its index left the window.
2. Pop back while `a[back]` is worse than the new value.
3. Push the new index; read the front.

**Base problem:** [Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/) · H

> 🔑 An element that is both older and smaller than a newcomer can never be the max again.

⏱ Time `O(n)` · Space `O(k)`

- [ ] [Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/) · H — Base
- [ ] [Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit](https://leetcode.com/problems/longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit/) · M — Two deques (max and min); shrink `l` while `max - min > limit`
- [ ] [Shortest Subarray with Sum at Least K](https://leetcode.com/problems/shortest-subarray-with-sum-at-least-k/) · H — Deque over **prefix sums** (increasing). Pop front while `prefix[i] - prefix[front] ≥ k` (record length); pop back while `prefix[back] ≥ prefix[i]`. Handles negatives, unlike SW2

---

## Minimum Spanning Tree

### MS1 Kruskal and Prim

> **Recognition:** "Connect all nodes at minimum total cost."

**Core idea (Kruskal):** Sort edges by weight; add an edge if it joins two different components (Union-Find, GR11); stop at `n - 1` edges. **Prim:** grow one tree, always adding the cheapest edge leaving it (heap).

**Base problem:** [Min Cost to Connect All Points](https://leetcode.com/problems/min-cost-to-connect-all-points/) · M
Complete graph with Manhattan distances. Dense graph → Prim in `O(n²)` without a heap, or Kruskal over all `n²` edges.

> 🔑 Cut property: the cheapest edge crossing any cut belongs to some MST.

⏱ Kruskal `O(E log E)` · Prim (dense) `O(n²)`

- [ ] [Min Cost to Connect All Points](https://leetcode.com/problems/min-cost-to-connect-all-points/) · M — Base
- [ ] [Connecting Cities With Minimum Cost](https://leetcode.com/problems/connecting-cities-with-minimum-cost/) (P) · M — Explicit edges; return `-1` if fewer than `n - 1` edges were used (disconnected)

---

## Tree Traversal and Construction

### TC1 Through-Node Answer with Upward Gain

> **Recognition:** The best path may bend at any node, but a parent can only extend **one** branch.

**Core idea:** DFS returns the best **one-sided** value to the parent, while a global variable records the best **two-sided** value through the current node.

**Base problem:** [Diameter of Binary Tree](https://leetcode.com/problems/diameter-of-binary-tree/) · E
Return `1 + max(l, r)` (height); update `ans = max(ans, l + r)`.

⏱ Time `O(n)` · Space `O(h)`

- [ ] [Diameter of Binary Tree](https://leetcode.com/problems/diameter-of-binary-tree/) · E — Base
- [ ] [Binary Tree Maximum Path Sum](https://leetcode.com/problems/binary-tree-maximum-path-sum/) · H — Child gain = `max(0, dfs(child))` (drop negative branches); `ans = val + l + r`; return `val + max(l, r)`. Initialise `ans` to `-∞` for all-negative trees

### TC2 BST Validation and Inorder Tricks

> 🔑 In-order traversal of a BST is strictly increasing.

- [ ] [Validate Binary Search Tree](https://leetcode.com/problems/validate-binary-search-tree/) · M — Pass `(low, high)` bounds down (comparing only with the parent is a classic bug), or check the in-order sequence is strictly increasing
- [ ] [Kth Smallest Element in a BST](https://leetcode.com/problems/kth-smallest-element-in-a-bst/) · M — Iterative in-order, stop at the `k`-th pop. For repeated queries, augment nodes with subtree sizes
- [ ] [Binary Tree Inorder Traversal](https://leetcode.com/problems/binary-tree-inorder-traversal/) · E — Iterative: push the left spine, pop, visit, go right. **Morris** traversal gets `O(1)` space by temporarily threading predecessors' right pointers

### TC3 Construction and Serialization

**Base problem:** [Construct Binary Tree from Preorder and Inorder Traversal](https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/) · M
Preorder's next element is the root; its position in inorder splits left/right subtrees. Precompute `value → inorder index` for `O(1)` splits.

⏱ Time `O(n)` · Space `O(n)`

- [ ] [Construct Binary Tree from Preorder and Inorder Traversal](https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/) · M — Base
- [ ] [Serialize and Deserialize Binary Tree](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/) · H — Pre-order with explicit `null` markers; deserialize by consuming tokens recursively (or BFS level-order encoding). Markers remove the need for a second traversal

---

## Binary Search Variants

### BV1 Rotated Array

> **Recognition:** Sorted array rotated at an unknown pivot.

**Core idea:** At every `mid`, **at least one half is sorted**. Decide which, then check whether the target lies in the sorted half.

**Base problem:** [Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/) · M

⚠️ With duplicates, worst case degrades to `O(n)`.
⏱ Time `O(log n)` · Space `O(1)`

- [ ] [Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/) · M — Base
- [ ] [Find Minimum in Rotated Sorted Array](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/) · M — Compare `a[mid]` with `a[hi]`: `>` → `lo = mid + 1`; else `hi = mid`

### BV2 Matrix as Flattened Array

- [ ] **Base problem:** [Search a 2D Matrix](https://leetcode.com/problems/search-a-2d-matrix/) · M
Rows sorted and each row starts above the previous row's last element → binary search over `0..mn-1`, mapping `idx → (idx / n, idx % n)`.

⏱ Time `O(log(mn))` · Space `O(1)`

### BV3 Partition Search

- [ ] **Base problem:** [Median of Two Sorted Arrays](https://leetcode.com/problems/median-of-two-sorted-arrays/) · H
Binary-search a cut `i` in the **shorter** array; the cut in the longer array is `j = (m + n + 1)/2 - i`. Valid when `maxLeft(A) ≤ minRight(B)` and `maxLeft(B) ≤ minRight(A)`. Median comes from the boundary values.

> 🔑 The search is for the correct partition, not an element.

⏱ Time `O(log min(m, n))` · Space `O(1)`

- [ ] [Koko Eating Bananas](https://leetcode.com/problems/koko-eating-bananas/) · M — textbook example of BS2: `feasible(speed)` = `Σ ceil(pile / speed) ≤ h`, with `lo = 1`, `hi = max(piles)`

---

## Bit Manipulation

### BM1 XOR Cancellation

> 🔑 `x ^ x = 0` and `x ^ 0 = x`; XOR is commutative and associative, so pairs cancel.

- [ ] [Single Number](https://leetcode.com/problems/single-number/) · E — XOR everything; only the unpaired value survives. `O(n)` / `O(1)`
- [ ] [Missing Number](https://leetcode.com/problems/missing-number/) · E — XOR all indices `0..n` with all values (or use `n(n+1)/2 - sum`)

### BM2 Bit Counting Tricks

> 🔑 `n & (n - 1)` clears the lowest set bit; `n & -n` isolates it.

- [ ] [Number of 1 Bits](https://leetcode.com/problems/number-of-1-bits/) · E — Loop `n &= n - 1`, counting iterations
- [ ] [Counting Bits](https://leetcode.com/problems/counting-bits/) · E — `dp[i] = dp[i >> 1] + (i & 1)` (or `dp[i & (i-1)] + 1`)

---

## Bitmask and Digit DP

### BD1 Bitmask DP over Subsets

> **Recognition:** `n ≤ ~20`, "assign/visit/partition a set of items optimally".

**State:** `dp[mask]` (or `dp[mask][last]`) = best result having already handled the items in `mask`. **Transition:** add one item not in the mask. **Order:** increasing mask.

**Base problem:** [Minimum Number of Work Sessions to Finish the Tasks](https://leetcode.com/problems/minimum-number-of-work-sessions-to-finish-the-tasks/) · M
`dp[mask] = (sessions, timeUsedInLastSession)` minimised lexicographically; add task `i`: if it fits, same session; otherwise open a new one.

⏱ Time `O(2ⁿ · n)` · Space `O(2ⁿ)`

- [ ] [Minimum Number of Work Sessions to Finish the Tasks](https://leetcode.com/problems/minimum-number-of-work-sessions-to-finish-the-tasks/) · M — Base
- [ ] [Find the Shortest Superstring](https://leetcode.com/problems/find-the-shortest-superstring/) · H — TSP-style `dp[mask][last]` with precomputed pairwise overlaps; reconstruct the order. `O(2ⁿ · n²)`

### BD2 Digit DP

> **Recognition:** "Count numbers in `[0, N]` with a digit property."

**State:** `dp(pos, mask-or-property, tight, started)`. Walk digits from most significant; `tight` = prefix equals `N`'s prefix so far (digit limited); `started` = leading zeros have ended.

- [ ] **Base problem:** [Count Special Integers](https://leetcode.com/problems/count-special-integers/) · H
Count numbers `≤ N` with all distinct digits; `mask` = digits already used.

⚠️ Memoise only the non-tight, started states; handle leading zeros with `started`.
⏱ Time `O(len · 2¹⁰ · 10)` · Space `O(len · 2¹⁰)`

---

## Math and Number Theory

### MT1 Fast Exponentiation

- [ ] **Base problem:** [Pow(x, n)](https://leetcode.com/problems/powx-n/) · M
Square-and-multiply: if `n` is odd multiply result by `x`; `x *= x`; `n >>= 1`. For negative `n`, invert `x` and negate `n`.

⚠️ Convert `n` to a 64-bit integer first; `-INT_MIN` overflows.
⏱ Time `O(log n)` · Space `O(1)`

### MT2 Sieve of Eratosthenes

- [ ] **Base problem:** [Count Primes](https://leetcode.com/problems/count-primes/) · M
Boolean array; for `i` from 2 while `i·i < n`: if prime, mark multiples starting at `i·i`.

⏱ Time `O(n log log n)` · Space `O(n)`

### MT3 GCD and Modular Arithmetic

> 🔑 `gcd(a, b) = gcd(b, a % b)`, `O(log min(a,b))`. For modular answers, reduce after **every** multiply and use 64-bit intermediates; modular inverse for a prime modulus is `a^(p-2)`.

- [ ] [Find Greatest Common Divisor of Array](https://leetcode.com/problems/find-greatest-common-divisor-of-array/) · E — `gcd(min, max)`
- [ ] [Greatest Common Divisor of Strings](https://leetcode.com/problems/greatest-common-divisor-of-strings/) · E — If `s1 + s2 != s2 + s1` → `""`; else prefix of length `gcd(len1, len2)`

---

## String Algorithms

### SA1 Expand Around Center

**Base problem:** [Longest Palindromic Substring](https://leetcode.com/problems/longest-palindromic-substring/) · M
For each index, expand for odd (`i, i`) and even (`i, i+1`) centers while chars match; track the best.

⏱ Time `O(n²)` (Manacher `O(n)`) · Space `O(1)`

- [ ] [Longest Palindromic Substring](https://leetcode.com/problems/longest-palindromic-substring/) · M — Base
- [ ] [Palindromic Substrings](https://leetcode.com/problems/palindromic-substrings/) · M — Count every successful expansion instead of tracking the longest

### SA2 KMP Prefix Function

> **Recognition:** Substring search without re-scanning, or "longest proper prefix that is also a suffix".

**Core idea:** `lps[i]` = length of the longest proper prefix of `s[0..i]` that is also a suffix. On mismatch, fall back to `lps[j-1]` instead of restarting.

**Base problem:** [Find the Index of the First Occurrence in a String](https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/) · E

⏱ Time `O(n + m)` · Space `O(m)`

- [ ] [Find the Index of the First Occurrence in a String](https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/) · E — Base
- [ ] [Longest Happy Prefix](https://leetcode.com/problems/longest-happy-prefix/) · H — Answer = `s[:lps[n-1]]`
- [ ] [Repeated Substring Pattern](https://leetcode.com/problems/repeated-substring-pattern/) · E — Repeats iff `lps[n-1] > 0` and `n % (n - lps[n-1]) == 0` (or `s` occurs in `(s+s)[1:-1]`)

### SA3 Rolling Hash

**Base problem:** [Longest Duplicate Substring](https://leetcode.com/problems/longest-duplicate-substring/) · H
Binary search the **length** `L` (BS2: if a duplicate of length `L` exists, so does one of length `L-1`); check each `L` with a Rabin–Karp rolling hash in `O(n)`; verify matches to rule out collisions.

> 🔑 Rolling hash updates in `O(1)`: remove the leading char, shift, add the new char (mod a large prime).

⏱ Time `O(n log n)` expected · Space `O(n)`

- [ ] [Longest Duplicate Substring](https://leetcode.com/problems/longest-duplicate-substring/) · H — Base
- [ ] [Repeated DNA Sequences](https://leetcode.com/problems/repeated-dna-sequences/) · M — Fixed length 10; a set of substrings is enough (or a 2-bit-per-char integer encoding)

### SA4 Expression and String Parsing

- [ ] [Basic Calculator II](https://leetcode.com/problems/basic-calculator-ii/) · M — Read number, apply the **previous** operator: `+`/`-` push `±num`; `*`/`/` modify the stack top; answer = stack sum. `O(n)`
- [ ] [String to Integer (atoi)](https://leetcode.com/problems/string-to-integer-atoi/) · M — Skip spaces → sign → digits → clamp to 32-bit **before** overflowing

---

## Advanced Data Structures and Graph Variants

Less frequent patterns that are still worth knowing.

### AD1 Fenwick Tree

> **Recognition:** Point updates with range-sum queries, or counting "how many smaller/larger elements so far".

**Base problem:** [Range Sum Query - Mutable](https://leetcode.com/problems/range-sum-query-mutable/) · M
Fenwick: `update(i, delta)` walks `i += i & -i`; `query(i)` walks `i -= i & -i`; range sum = `query(r) - query(l-1)`.

⏱ Time `O(log n)` per op · Space `O(n)`

- [ ] [Range Sum Query - Mutable](https://leetcode.com/problems/range-sum-query-mutable/) · M — Base (segment tree also works, and extends to range min/max)
- [ ] [Count of Smaller Numbers After Self](https://leetcode.com/problems/count-of-smaller-numbers-after-self/) · H — Coordinate-compress values; scan **right to left**, query the count of smaller values already inserted, then insert. (Merge sort counting also works)

### AD2 Shortest Path with Limits

- [ ] [Network Delay Time](https://leetcode.com/problems/network-delay-time/) · M — Plain Dijkstra (GR9); answer = max distance, or `-1` if any node is unreachable
- [ ] [Cheapest Flights Within K Stops](https://leetcode.com/problems/cheapest-flights-within-k-stops/) · M — **Bellman-Ford** limited to `k+1` rounds, relaxing from a *copy* of the previous round's distances; or Dijkstra/BFS with state `(node, stops)`

⚠️ Pruning Dijkstra by node alone is wrong when there's a stop limit; a costlier path with fewer stops may still be needed.

### AD3 Random Sampling

- [ ] [Linked List Random Node](https://leetcode.com/problems/linked-list-random-node/) · M — **Reservoir sampling** (k = 1): replace the kept node with the `i`-th node with probability `1/i`
- [ ] [Random Pick with Weight](https://leetcode.com/problems/random-pick-with-weight/) · M — Prefix sums of weights; pick a random integer in `[1, total]` and binary search the first prefix `≥` it

---

## Concurrency Basics

> **Recognition:** Threads must run in a fixed order, alternate, or form groups.

**Core idea:** Use primitives to encode *"B may not start until A finishes"*: semaphores, mutex + condition variable, events, or barriers.

- [ ] [Print in Order](https://leetcode.com/problems/print-in-order/) · E — Two semaphores/events: `second` waits for `first`, `third` waits for `second`
- [ ] [Print FooBar Alternately](https://leetcode.com/problems/print-foobar-alternately/) · M — Two semaphores handing the turn back and forth
- [ ] [Building H2O](https://leetcode.com/problems/building-h2o/) · M — Semaphore of 2 for hydrogen, 1 for oxygen, plus a barrier of 3 so each molecule releases together

⚠️ Concurrency problems are language-specific and are usually practised separately from standard DSA.

---

## Coverage Check

| Section                                  | Questions |
| ---------------------------------------- | --------- |
| Arrays and Two Pointers                  | 9         |
| Sliding Window                           | 4         |
| Stacks                                   | 6         |
| Binary Search                            | 4         |
| Linked Lists                             | 7         |
| Trees                                    | 9         |
| Heaps                                    | 4         |
| Backtracking                             | 13        |
| Graphs                                   | 33        |
| Dynamic Programming                      | 55        |
| SQL                                      | 25        |
| More Patterns for Revision (19 sections) | 98        |
| **Total**                                | **267**   |