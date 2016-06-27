import asyncio
import logging

from sphinx.plugin import BasePlugin


#from .geoflow import Geoflow_Solver

def run_geoflow(atoms):
    '''Start the geoflow process.
    We have to instantiate the solver, and then run 'process_molecule' in the
    same process.  There isn't much point in making this a method of the
    plugin class.  At least not that I can see now.  There may however be a
    better way to do this in the future.
    '''
    # TODO: All of the following belong in a configuration file.  I like the
    # idea of a geoflow config building module.  It would assist the user
    # with the meaning of the various values, as well as tracking, naming and
    # locating the configs the user has created.
    solver = Geoflow_Solver(pres_i=0.008, gama_i=0.0001, npiter=1,
            ngiter=1, tauval=1.40, prob=0.0, ffmodel=1, sigmas=1.5828,
            epsilonw=0.1554, vdwdispersion=0, extvalue=1.90, iadi=0,
            alpha=0.50, tol=1e-4, tottf=3.5, dcel=0.25, maxstep=20,
            epsilons=80.00, epsilonp=1.5, radexp=1, crevalue=0.01,
            density=0.03346)

    result = solver.process_molecule(atoms)

    del solver
    return result


class GeoflowTest(BasePlugin):
    '''Plugin for running geometric flow
    '''
    def __init__(self, **kwargs):
        self._atoms = []

        super().__init__(**kwargs)
        _log.info("Geoflow plug-in initialized.")


    @classmethod
    def script_name(cls):
        return "geoflow_test"


    @classmethod
    def sinks(cls):
        return ['apbs_atom']


    @classmethod
    def sources(cls):
        return ['text']


    @asyncio.coroutine
    def run(self):
        try:
            # Collect all of the atoms that are available.
            while True:
                data = yield from self.read_data()
                if data:
                    value = data['apbs_atom']
                    self._atoms.append({
                        'pos': (
                            value['Cartn_x'],
                            value['Cartn_y'],
                            value['Cartn_z']
                        ),
                        'radius': value['radius'],
                        'charge': value['charge']
                    })
                else:
                    break

            # Run Geoflow in a separate process
            result = yield from self.runner.run_as_process(run_geoflow,
                    {'atoms': self._atoms})

            yield from self.publish(self._tm.new_text(lines=[str(result)]))

            yield from self.done()
        except Exception as e:
            _log.exception('Unhandled exception:')


    def xform_data(self, data, to_type):
        return data
