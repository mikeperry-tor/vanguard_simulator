import logging
import time

#import grapher
import topology
import guard
import adversary

# TODO: Time left to rotate G1 when compromise G2

class StatsCache(object):
    """
    This object collects stats from multiple simulation runs for the purpose of
    calculating stats and outputing useful graphs.
    """
    def __init__(self, topology, sybil_model, pwnage_model):
        self.experiment_descr = "%s_%s_%s" % (topology, sybil_model, pwnage_model)
        self.simulation_runs = []

    def register_run(self, run_state):
        self.simulation_runs.append(run_state)
        logging.warn("Registered %d run" % len(self.simulation_runs))

    def finalize_experiment(self):
        """
        We just finished all the simulation runs. Finalize the experiment by
        running various calculations accross simulation runs (e.g. average
        times to deanonymization, etc.)
        """
        guard_rotations_all = [x.total_guard_rotations for x in self.simulation_runs]
        guard_rotations_all = filter(None, guard_rotations_all) # remove any Nones out of there
        self.avg_guard_rotations = sum(guard_rotations_all) / len(guard_rotations_all)

        time_to_g1_all = [x.time_to_g1 for x in self.simulation_runs]
        time_to_g1_all = filter(None, time_to_g1_all) # remove any Nones out of there
        self.avg_secs_to_deanon = sum(time_to_g1_all) / len(time_to_g1_all)

        time_to_g2_all = [x.time_to_g2 for x in self.simulation_runs]
        time_to_g2_all = filter(None, time_to_g2_all) # remove any Nones out of there
        self.avg_secs_to_guard_discovery = sum(time_to_g2_all) / len(time_to_g2_all)

        time_to_g3_all = [x.time_to_g3 for x in self.simulation_runs]
        time_to_g3_all = filter(None, time_to_g3_all) # remove any Nones out of there
        self.avg_secs_to_g3 = sum(time_to_g3_all) / len(time_to_g3_all)

    def dump_experiment_parameters(self):
        """Dump the various parameters of our experiment"""
        timestr = time.strftime("%Y-%m-%d %H:%M:%S")

        # First finalize this experiment
        self.finalize_experiment()

        # Now format the global experiment parameters, and put them in a
        # variable so that it's used by the graphing func too
        self.experiment_params = "Experiment parameters:\n"
        self.experiment_params += "="*60 + "\n"
        self.experiment_params += "Date: %s\n" % timestr
        self.experiment_params += "Simulation rounds: %d\n" % len(self.simulation_runs)
        self.experiment_params += guard.dump_parameters()
        self.experiment_params += topology.dump_parameters()
        self.experiment_params += adversary.dump_parameters()
        self.experiment_params += "="*60 + "\n"

        # also format the average experiment times
        self.experiment_params += "Average number of node rotations: %d\n" % self.avg_guard_rotations
        self.experiment_params += "Average hours to deanonymization: %d\n" % (self.avg_secs_to_deanon / 3600)
        self.experiment_params += "Average hours to guard discovery: %d\n" % (self.avg_secs_to_guard_discovery / 3600)
        self.experiment_params += "Average hours to G3: %d\n" % (self.avg_secs_to_g3 / 3600)

        logging.warn("="*80)
        logging.warn(self.experiment_params)

    def dump_stats(self, grapher):
        logging.warn("*" * 80)
        self.graph_time_to_deanon(grapher)
        self.graph_time_to_g2(grapher)
        self.graph_time_to_g3(grapher)
#        self.graph_remaining_g2_times()

    def graph_time_to_deanon(self, grapher):
        times_list = []

        for sim in self.simulation_runs:
            if sim.time_to_g1:
                hours = sim.time_to_g1 // 3600
                times_list.append(hours)
            else:
                times_list.append(0)

        grapher.graph_time_to_guard(times_list, layer_num=1,
                                    experiment_descr=self.experiment_descr,
                                    text_info=self.experiment_params)

    def graph_time_to_g2(self, grapher):
        times_list = []

        for sim in self.simulation_runs:

            if sim.time_to_g2:
                hours = sim.time_to_g2 // 3600
                times_list.append(hours)
            else:
                times_list.append(0)

        grapher.graph_time_to_guard(times_list, layer_num=2,
                                    experiment_descr=self.experiment_descr,
                                    text_info=self.experiment_params)

    def graph_time_to_g3(self, grapher):
        times_list = []

        for sim in self.simulation_runs:

            if sim.time_to_g3:
                hours = sim.time_to_g3 // 3600
                times_list.append(hours)
            else:
                times_list.append(0)

        grapher.graph_time_to_guard(times_list, layer_num=3,
                                    experiment_descr=self.experiment_descr,
                                    text_info=self.experiment_params)

    def graph_remaining_g2_times(self, grapher):
        times_list = []

        for sim in self.simulation_runs:

            for remaining_g2_time in sim.times_left_for_g2_rotation:
                hours = remaining_g2_time // 3600
                times_list.append(hours)
            else:
                times_list.append(0)

        grapher.graph_remaining_g2_times(times_list,
                                         experiment_descr=self.experiment_descr,
                                         text_info=self.experiment_params)

if __name__ == "__main__":
  import grapher
  import cPickle as pickle
  stats = pickle.load(file("stats.pickle"))
  stats.dump_stats(grapher)
