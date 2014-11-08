# The *record_history* decorator
---
The `record_history` decorator is a stripped-down version of `log_calls` which
records calls to a decorated function but writes no messages. You can think
of it as `log_calls` with the `record_history` and `log_call_numbers` settings
always true, and without any of the message-logging apparatus.

Just as the settings of `log_calls` for a decorated function are accessible
dynamically through the `log_calls_settings` attribute, the settings of
`record_history` are exposed via a `record_history_settings` attribute.
`record_history_settings` is an object of the same type as `log_calls_settings`,
so it has the same methods and behaviors described in the [`log_calls_settings`
section](./log_calls.html#Dynamic-control-log_calls_settings) of the `log_calls`
documentation.

Functions decorated by `record_history` have a full-featured `stats` attribute,
as described in the [Call history and statistics](./log_calls.html#call-history-and-statistics)
section of the `log_calls` documentation.

## [Usage](id:usage)
Import `record_history` just as you would `log_calls`:

    >>> from log_calls import record_history

We'll use the following function in our examples:

    >>> @record_history()
    ... def record_me(a, b, x):
    ...     return a * x + b

## [Keyword Parameters](id:parameters)
`record_history` has only three keyword parameters:

Keyword parameter | Default value | Description
----------------: | :------------ | :------------------
       `enabled`    | `True`          | When true, call history will be recorded
       `prefix`     | ``              | A `str` to prefix the function name with in call records
       `max_history`    | 0           | An `int`. *value* > 0 --> store at most *value*-many records, oldest records overwritten; *value* ≤ 0 --> store unboundedly many records.

Setting `enabled` to true in `record_history` is like setting both `enabled`
and `record_history` to true in `log_calls`.

You can supply an [*indirect value*](./log_calls.html#Indirect-values) for the `enabled` parameter, as described
in the log_calls documentation.

## [The *record_history_settings* attribute](id:record_history_settings-attribute)
These settings are accessible dynamically through the `record_history_settings`
attribute of a decorated function.

    >>> len(record_me.record_history_settings)
    3
    >>> list(record_me.record_history_settings)
    ['enabled', 'prefix', 'max_history']
    >>> list(record_me.record_history_settings.items())
    [('enabled', True), ('prefix', ''), ('max_history', 0)]
    >>> record_me.record_history_settings.as_OrderedDict()  # doctest: +NORMALIZE_WHITESPACE
    OrderedDict([('enabled', True), ('prefix', ''), ('max_history', 0)])

Let's finally call the function defined above:

    >>> for x in range(15):
    ...     _ = record_me(3, 5, x)      # "_ = " for doctest

    >>> import pprint
    >>> len(record_me.stats.history)
    15

The tallies:

    >>> record_me.stats.num_calls_logged
    15
    >>> record_me.stats.num_calls_total
    15
    >>> record_me.stats.elapsed_secs_logged          # doctest: +SKIP
    2.2172927856445312e-05

Call history in CSV format, with ellipses for 'elapsed_secs' and 'timestamp' columns:

    >>> print(record_me.stats.history_as_csv)         # doctest: +ELLIPSIS
    call_num|a|b|x|retval|elapsed_secs|timestamp|prefixed_fname|caller_chain
    1|3|5|0|5|...|...|'record_me'|['<module>']
    2|3|5|1|8|...|...|'record_me'|['<module>']
    3|3|5|2|11|...|...|'record_me'|['<module>']
    4|3|5|3|14|...|...|'record_me'|['<module>']
    5|3|5|4|17|...|...|'record_me'|['<module>']
    6|3|5|5|20|...|...|'record_me'|['<module>']
    7|3|5|6|23|...|...|'record_me'|['<module>']
    8|3|5|7|26|...|...|'record_me'|['<module>']
    9|3|5|8|29|...|...|'record_me'|['<module>']
    10|3|5|9|32|...|...|'record_me'|['<module>']
    11|3|5|10|35|...|...|'record_me'|['<module>']
    12|3|5|11|38|...|...|'record_me'|['<module>']
    13|3|5|12|41|...|...|'record_me'|['<module>']
    14|3|5|13|44|...|...|'record_me'|['<module>']
    15|3|5|14|47|...|...|'record_me'|['<module>']
    <BLANKLINE>

Disable recording, call the function again:

    >>> record_me.record_history_settings.enabled = False
    >>> _ = record_me(583, 298, 1000)

Call numbers of last 2 calls to `record_me`:

    >>> list(map(lambda rec: rec.call_num, record_me.stats.history[-2:]))
    [14, 15]

and here are the call counters:

    >>> record_me.stats.num_calls_logged
    15
    >>> record_me.stats.num_calls_total
    16

Re-enable recording and call the function again:

    >>> record_me.record_history_settings.enabled = True
    >>> _ = record_me(1900, 2000, 20)

Here are the last 3 lines of the CSV call history:

    >>> lines = record_me.stats.history_as_csv.strip().split('\\n')
    >>> # Have to skip next test in .md
    >>> #  because doctest doesn't split it at all: len(lines) == 1
    >>> for line in lines[-3:]:                   # doctest: +ELLIPSIS, +SKIP
    ...     print(line)
    14|3|5|13|44|...|...|'record_me'|['<module>']
    15|3|5|14|47|...|...|'record_me'|['<module>']
    16|1900|2000|20|40000|...|...|'record_me'|['<module>']

and here are the call updated counters:

    >>> record_me.stats.num_calls_logged
    16
    >>> record_me.stats.num_calls_total
    17

Finally, let's call `stats.clear_history`, setting `max_history` to 3,
and examine the call history again:

    >>> record_me.stats.clear_history(max_history=3)
    >>> for x in range(15):
    ...     _ = record_me(3, 5, x)
    >>> print(record_me.stats.history_as_csv)      # doctest: +ELLIPSIS
    call_num|a|b|x|retval|elapsed_secs|timestamp|prefixed_fname|caller_chain
    13|3|5|12|41|...|...|'record_me'|['<module>']
    14|3|5|13|44|...|...|'record_me'|['<module>']
    15|3|5|14|47|...|...|'record_me'|['<module>']
    <BLANKLINE>

## [Call history and call chains](id:Call-history-and-call-chains)
An example showing a longer call chain, and call numbers of a decorated
caller appearing in the call chain:

    >>> record_me.stats.clear_history()

    >>> class Base():
    ...     def call_record_me(self, a, b, n):
    ...         nth = 2**n
    ...         for k in range(nth, 2 * nth):
    ...             record_me(a, b, k)
    >>> class Even(Base):
    ...     @record_history(prefix='Even.')
    ...     def call_it(self, n):
    ...         self.call_record_me(2*n + 1, 3*n + 1, n)
    >>> class Odd(Base):
    ...     @record_history(prefix='Odd.')
    ...     def call_it(self, n):
    ...         self.call_record_me(5*n + 1, 7*n + 1, n)
    >>> even = Even()
    >>> odd = Odd()
    >>> for i in range(3):
    ...     (even, odd)[i%2].call_it(i)

    >>> even.call_it.stats.num_calls_logged, odd.call_it.stats.num_calls_logged
    (2, 1)
    >>> record_me.stats.num_calls_logged
    7

    >>> print(even.call_it.stats.history_as_csv)        # doctest: +ELLIPSIS
    call_num|self|n|retval|elapsed_secs|timestamp|prefixed_fname|caller_chain
    1|<__main__.Even object at ...>|0|None|...|...|'Even.call_it'|['<module>']
    2|<__main__.Even object at ...>|2|None|...|...|'Even.call_it'|['<module>']
    <BLANKLINE>

    >>> print(odd.call_it.stats.history_as_csv)        # doctest: +ELLIPSIS
    call_num|self|n|retval|elapsed_secs|timestamp|prefixed_fname|caller_chain
    1|<__main__.Odd object at ...>|1|None|...|...|'Odd.call_it'|['<module>']
    <BLANKLINE>

    >>> print(record_me.stats.history_as_csv)     # doctest: +ELLIPSIS
    call_num|a|b|x|retval|elapsed_secs|timestamp|prefixed_fname|caller_chain
    1|1|1|1|2|...|...|'record_me'|['call_record_me', 'Even.call_it [1]']
    2|6|8|2|20|...|...|'record_me'|['call_record_me', 'Odd.call_it [1]']
    3|6|8|3|26|...|...|'record_me'|['call_record_me', 'Odd.call_it [1]']
    4|5|7|4|27|...|...|'record_me'|['call_record_me', 'Even.call_it [2]']
    5|5|7|5|32|...|...|'record_me'|['call_record_me', 'Even.call_it [2]']
    6|5|7|6|37|...|...|'record_me'|['call_record_me', 'Even.call_it [2]']
    7|5|7|7|42|...|...|'record_me'|['call_record_me', 'Even.call_it [2]']
    <BLANKLINE>

##[*stats.elapsed_secs_logged* == sum of *elapsed_secs* column of call history](id:elapsed_secs_logged-equal-sum-etc)
Equal "to within an epsilon", anyway, allowing for some very small
numerical inaccuracy:

    >>> @record_history()
    ... def slow(n):
    ...     val = []
    ...     for i in range(n):
    ...         val.append("a" * i)
    >>> for i in range(100):
    ...     slow(i)
    >>> elapsed_col = list(map(lambda rec: getattr(rec, 'elapsed_secs'),
    ...                        slow.stats.history))
    >>> abs(sum(elapsed_col) - slow.stats.elapsed_secs_logged) < 1.0e-15
    True

##[Example of the *history_as_DataFrame* attribute](id:stats.history_as_DataFrame)
The `stats.history_as_DataFrame` attribute returns the history of a decorated
function as a [Pandas](http://pandas.pydata.org) [DataFrame](http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe), 
if the Pandas library is installed. 

Here's an example of its use, though not a doctest, as we don't require `Pandas` or `numpy`. Some setup code:

    from log_calls import record_history

    import numpy as np
    import pandas as pd

    @record_history()
    def f(freq, t):
        return np.sin(freq * 2 * np.pi * t)

    ran_t = np.arange(0.0, 1.0, 1/44100)

`ran_t` is a `numpy` array of size 44100:

    array([  0.00000000e+00,   2.26757370e-05,   4.53514739e-05, ...,
             9.99931973e-01,   9.99954649e-01,   9.99977324e-01])
         
Now call `f`, and examine its call history as a `DataFrame`:
     
    for t in ran_t:
        f(7, t)

    df = f.stats.history_as_DataFrame
    df[:5]

You should see something like this (though probably in two chunks):

              freq         t    retval  elapsed_secs                 timestamp prefixed_fname  caller_chain     
    call_num                                                                                                 
    1            7  0.000000  0.000000      0.000023  11/07/14 16:22:06.778364            'f'  ['<module>']  
    2            7  0.000023  0.000997      0.000009  11/07/14 16:22:06.778650            'f'  ['<module>']  
    3            7  0.000045  0.001995      0.000008  11/07/14 16:22:06.778873            'f'  ['<module>']  
    4            7  0.000068  0.002992      0.000007  11/07/14 16:22:06.779092            'f'  ['<module>']  
    5            7  0.000091  0.003989      0.000012  11/07/14 16:22:06.779306            'f'  ['<module>']  

or, in an IPython notebook:

<div class="output_html rendered_html output_subarea output_pyout">
<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>freq</th>
      <th>t</th>
      <th>retval</th>
      <th>elapsed_secs</th>
      <th>timestamp</th>
      <th>prefixed_fname</th>
      <th>caller_chain</th>
    </tr>
    <tr>
      <th>call_num</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td> 7</td>
      <td> 0.000000</td>
      <td> 0.000000</td>
      <td> 0.000041</td>
      <td> 11/07/14 20:01:55.301521</td>
      <td> 'f'</td>
      <td> ['&lt;module&gt;']</td>
    </tr>
    <tr>
      <th>2</th>
      <td> 7</td>
      <td> 0.000023</td>
      <td> 0.000997</td>
      <td> 0.000016</td>
      <td> 11/07/14 20:01:55.301794</td>
      <td> 'f'</td>
      <td> ['&lt;module&gt;']</td>
    </tr>
    <tr>
      <th>3</th>
      <td> 7</td>
      <td> 0.000045</td>
      <td> 0.001995</td>
      <td> 0.000014</td>
      <td> 11/07/14 20:01:55.302004</td>
      <td> 'f'</td>
      <td> ['&lt;module&gt;']</td>
    </tr>
    <tr>
      <th>4</th>
      <td> 7</td>
      <td> 0.000068</td>
      <td> 0.002992</td>
      <td> 0.000014</td>
      <td> 11/07/14 20:01:55.302211</td>
      <td> 'f'</td>
      <td> ['&lt;module&gt;']</td>
    </tr>
    <tr>
      <th>5</th>
      <td> 7</td>
      <td> 0.000091</td>
      <td> 0.003989</td>
      <td> 0.000014</td>
      <td> 11/07/14 20:01:55.302416</td>
      <td> 'f'</td>
      <td> ['&lt;module&gt;']</td>
    </tr>
  </tbody>
</table>
</div>
</div>


<div class="cell border-box-sizing code_cell rendered">
<div class="input">
<div class="prompt input_prompt">
In&nbsp;[280]:
</div>
<div class="inner_cell">
    <div class="input_area">
<div class="highlight"><pre><span class="n">df</span><span class="p">[[</span><span class="s">&#39;t&#39;</span><span class="p">,</span> <span class="s">&#39;retval&#39;</span><span class="p">]]</span><span class="o">.</span><span class="n">head</span><span class="p">()</span>
</pre></div>

</div>
</div>
</div>


<div class="output_area"><div class="prompt output_prompt">
    Out[280]:</div>

<div class="output_html rendered_html output_subarea output_pyout">
<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>t</th>
      <th>retval</th>
    </tr>
    <tr>
      <th>call_num</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td> 0.000000</td>
      <td> 0.000000</td>
    </tr>
    <tr>
      <th>2</th>
      <td> 0.000023</td>
      <td> 0.000997</td>
    </tr>
    <tr>
      <th>3</th>
      <td> 0.000045</td>
      <td> 0.001995</td>
    </tr>
    <tr>
      <th>4</th>
      <td> 0.000068</td>
      <td> 0.002992</td>
    </tr>
    <tr>
      <th>5</th>
      <td> 0.000091</td>
      <td> 0.003989</td>
    </tr>
  </tbody>
</table>
</div>
</div>

<div class="cell border-box-sizing code_cell rendered">
<div class="input">
<div class="prompt input_prompt">
In&nbsp;[281]:
</div>
<div class="inner_cell">
    <div class="input_area">
<div class="highlight"><pre><span class="n">plt</span><span class="o">.</span><span class="n">plot</span><span class="p">(</span><span class="n">df</span><span class="o">.</span><span class="n">t</span><span class="p">,</span> <span class="n">df</span><span class="o">.</span><span class="n">retval</span><span class="p">);</span>
</pre></div>

</div>
</div>
</div>

<div class="output_wrapper">
<div class="output">


<div class="output_area"><div class="prompt"></div>


<div class="output_png output_subarea ">
<img src="data:image/png;base64,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
"
>
</div>

</div>

</div>
</div>

</div>
    </div>
  </div>

---

This example is actually quite artificial, because in practice you'd *never* call this function `f` in a loop like the one shown. Instead, you'd take advantage of `numpy`'s 
ability to vectorize, and simply call:

    Hz_7 = f(7, ran_t)
    
because that's dramatically faster[^1]. You would then make a `DataFrame` directly from the `numpy` arrays `ran_t` and `Hz_7`, without using the call history of `f` at all because it's not that useful: the vectorized call shows up in `f`'s history as a single record, 
with argnames = ('freq', 't'), argvals = (7, ran_t), and retval = Hz_7. 

`Hz_7` is also a `numpy` array of size 44100:

    array([ 0.        ,  0.00242209,  0.00484416, ..., 
           -0.0072662 , -0.00484416, -0.00242209])
 
[^1]: How much faster is the vectorized call? Without using any decorator, it's 2 orders of magnitude faster (about 150 times faster). Using `record_history`, the vectorized call is 3 orders of magnitude faster (2000+ times faster) with the decorator disabled, and 4 orders of magnitude faster (8000+ times faster) with the decorator enabled. No additional time is spent inside the function `f` when it's decorated. But these numbers show that `log_calls` and `record_history` have significant overhead, and they may not be your best bets for acquiring large amounts of data – tens of thousands of calls, say, or more. The performance numbers are from the IPython notebook `./history_to_pandas.ipynb` which you can browse as [`./history_to_pandas.html`](./history_to_pandas.html). 
