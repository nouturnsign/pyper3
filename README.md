# pyper3

Junky pipe implementation

## Motivation

It seemed potentially fun.

## Syntax

Begin pipes with `Pipe`, using `.push` to input a specific value and `.open` to start a pipe without a specific input, optionally naming the pipe. Then, use `.pipe` followed by the function, then calling the piped function with the remaining arguments. If `THIS` is not explicitly given, then it is inferred to be the first positional argument. Otherwise, the function will substitute `THIS` for the value. `.pipe` can then be chained. To end the pipe, the methods `.pop` and `.close` are given for `.push` and `.open`, respectively. 

`THIS` can also be used in the context of pipes to get attributes, methods, and items from the object through the dot operator and slicing. Note that complex members that require multiple dots are not currently supported, and are better defined using a pipe: e.g. for a pandas DataFrame `df`, the method `df.plot.scatter` could be written as `df_plot_scatter = Pipe.open("THIS.plot.scatter").pipe(getattr)("plot").pipe(getattr)("scatter").close()`.

`.pipe` allows for the boolean argument `inplace` that determines whether the original value should be returned. Note that the function is applied first, then the object is returned, so mutable objects will be modifed. If this is not desired, pipe a copy function first.

`.setup_logging` allows for logging. Pass the name of the logger along with additional optional arguments to customize the logger. The logger can also be directly modified as `Pipe._logger`. If passed into `.pipe`, functions created by `Pipe.open(name).close()` will be logged with their name, but outside of pipes, these functions will not be logged.

## Future goals

-   smarter type hinting
-   complex members