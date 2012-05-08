#! /usr/bin/env python
"""
@author: Gautham Ganapathy
@organization: Textensor (http://textensor.com)
@contact: gautham@textensor.com, gautham@lisphacker.org
"""

import sys
from pylems.base.errors import ParseError,ModelError,SimBuildError,SimError
from pylems.parser.lems import LEMSParser
from pylems.sim.build import SimulationBuilder

#from pylems.parser.expr import ExprParser

#print ExprParser('1').parse()
#print ExprParser('1 + 2').parse()
#print ExprParser('v .gt. threshold').parse()
#print ExprParser('1-95*v_t/100').parse()
#sys.exit(0)

if len(sys.argv) not in [2,3]:
    print 'Usage: runlems [-nogui] <model-file>'
    sys.exit(-1)

nogui = False
if len(sys.argv) == 2:
    model_file = sys.argv[1]
else:
    if sys.argv[1] == '-nogui':
        nogui = True
    model_file = sys.argv[2]
try:
    print 'Parsing model file'
    parser = LEMSParser()
    parser.init_parser()
    parser.parse_file(model_file)
    model = parser.get_model()
    
    print 'Resolving model'
    print model
    model.resolve_model()
    print model
    sys.exit(0)

    print 'Building simulation'
    sim = SimulationBuilder(model).build()

    print 'Running simulation'
    sim.run()

    if not nogui:
        import matplotlib.pyplot as plt
        import numpy

        print 'Plotting graphs'
        for rn in sim.runnables:
            runnable = sim.runnables[rn]
            if runnable.recorded_variables:
                for variable in runnable.recorded_variables:
                    values = runnable.recorded_variables[variable]
                    x = numpy.empty(len(values))
                    y = numpy.empty(len(values))
                    i = 0
                    for (xv, yv) in values:
                        x[i] = xv
                        y[i] = yv
                        i = i + 1

                    p = plt.subplot(111)
                    p.plot(x, y)
        plt.show()


except ParseError as e:
    print 'Caught ParseError - ' + str(e)
except ModelError as e:
    print 'Caught ModelError - ' + str(e)
except SimBuildError as e:
    print 'Caught SimBuildError - ' + str(e)
except SimError as e:
    print 'Caught SimError - ' + str(e)
