import pyper3
from operator import sub
from math import sqrt

TAG = "demo"
pyper3.Pipe.setup_logging(TAG)

result = (
    pyper3.Pipe
    .push([2, 3, 1, 5, 4])
    .pipe(pyper3.THIS[:4])()
    .pipe(pyper3.THIS.sort, inplace=True)(reverse=True)
    .pipe(print, inplace=True)()
    .pipe(len)()
    .pipe(str)()
    .pipe(len)()
    .pipe(pyper3.Pipe
          .open("pipe_inside_a_pipe")
          .pipe(sub, inplace=True)(4, pyper3.THIS)
          .close()
          )()
    .pop()
)
print("Result:", result)

rms_max_10 = (
    pyper3.Pipe
    .open()
    .pipe(sorted)(reverse=True)
    .pipe(pyper3.THIS[:10])()
    .pipe(map)(lambda x: x ** 2, pyper3.THIS)
    .pipe(sum)()
    .pipe(sqrt)()
    .close()
)

print("Result:", rms_max_10(range(-10, 10)))