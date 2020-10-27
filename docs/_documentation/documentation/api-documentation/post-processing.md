---
layout: default
title: Post Processing
nav_order: 1
permalink: /documentation/api-documentation/post-processing
parent: API Documentation
grand_parent: Documentation
has_children: true
---

# dame_flame.utils.post_processing
{: .no_toc }
 
The treatment effect estimates and other utilities

<div class="code-example" markdown="1">
```python
import dame_flame.utils.post_processing

# The main matched group of a unit or list of units
MG(matching_object, unit_ids)

# The conditional average treatment effect for a unit or list of units
CATE(matching_object, unit_ids)

# The average treatment effect for the matching data
ATE(matching_object)

# The average treatment effect on the treated for the matching data
ATT(matching_object)

```
</div>



### Parameters 

**matching_object**: Class DAME or Class FLAME, required (no default).

**unit_id**: int, list, required (no default): This is the unit or list of units for which the main matched group or treatment effect is being calculated