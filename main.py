import os
import sys
from dotenv import load_dotenv

from data_models.data_reader import ShipcallManager
from data_models.simulation_model import ModelLogSimulation
from gui.load_env_files_gui import get_gui
from interventions.external_agent.planner import get_vessels_schedule
from simulation.simulation import simulate

load_dotenv()

if __name__ == '__main__':
    arrivals_modellogsimul = ModelLogSimulation(os.getenv('PROCESS_MODEL'), os.getenv('ACTIVITIES_DURATION'),
                                                os.getenv('ACTIVITIES_RESOURCES'),
                                                os.getenv('ACTIVITIES_GATEWAYS_PERCENTAGES'))

    gui_app = get_gui(arrivals_modellogsimul)

    #date_to_plan = '06/17/2021 00:00:00'
    #dates_to_simulate = [date_to_plan]

    unfinished_shipcalls = []

    sh_manager = ShipcallManager()
    dates_to_simulate = sh_manager.get_all_shipcalls_dates()
    dates_to_simulate = [d.strftime('%m/%d/%Y %H:%M:%S') for d in dates_to_simulate]

    for date_to_plan in dates_to_simulate:
        arrivals_sh_to_simulate = sh_manager.get_shipcalls_for_date(date_to_plan)
        print(get_vessels_schedule(arrivals_sh_to_simulate))

        simulate(arrivals_sh_to_simulate, arrivals_modellogsimul, os.getenv('WAITING_ACTIVITY'), date_to_plan)
        unfinished_shipcalls.extend(arrivals_sh_to_simulate)

        departures_sh_to_simulate = sh_manager.get_departure_shipcalls_for_date(date_to_plan, unfinished_shipcalls)
        departures_modellogsimul = ModelLogSimulation(os.getenv('PROCESS_MODEL_DEPARTURES'),
                                                      os.getenv('ACTIVITIES_DURATION_DEPARTURES'),
                                                      os.getenv('ACTIVITIES_RESOURCES_DEPARTURES'),
                                                      os.getenv('ACTIVITIES_GATEWAYS_PERCENTAGES_DEPARTURE'))

        simulate(departures_sh_to_simulate, departures_modellogsimul, os.getenv('WAITING_ACTIVITY_DEPARTURE'),
                 date_to_plan,
                 1)

    sys.exit()
