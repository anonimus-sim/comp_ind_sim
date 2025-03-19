from copy import copy
from datetime import datetime, timedelta
import simpy
from typing import Dict, List

from data_models.shipcall_info import ShipcallInfo
from data_models.simulation_model import ModelLogSimulation
from interventions.custom_resource import CustomResource


def execute_activity(env: simpy.Environment, trans_label: str, model_resources: Dict[str, CustomResource],
                     modellogsimul: ModelLogSimulation, trace_id: int, waiting_activity: str, sh: ShipcallInfo,
                     date_to_plan: datetime, results_log: List[List[str]], arrival_or_departure: int):
    initial_date = copy(date_to_plan) if arrival_or_departure == 0 else copy(sh.last_timestamp_recorded)
    start_timestamp = initial_date + timedelta(minutes=env.now)
    print(
        f'Traza {trace_id}: Tiempo {env.now}: Iniciando actividad {trans_label}. Start timestamp {start_timestamp}. Duración estimada {modellogsimul.activities_duration[trans_label]}')

    if trans_label == waiting_activity:
        yield env.timeout(max(0,
                              sh.new_planner_entry_time if arrival_or_departure == 0 else sh.new_planner_departure_time))

    activity_resource_name = modellogsimul.resources_distribution.get(trans_label)
    if activity_resource_name:
        activity_resource = model_resources[activity_resource_name]
        activity_resource.print_usage()

        try:
            with activity_resource.request() as req:
                yield req
                print(f'Traza {trace_id}: Recurso {activity_resource_name} adquirido para actividad {trans_label}.')
        finally:
            print(f'Traza {trace_id}: Liberando recurso {activity_resource_name} al completar actividad {trans_label}.')
            activity_resource.print_usage()

    yield env.timeout(modellogsimul.activities_duration[trans_label])
    end_timestamp = initial_date + timedelta(minutes=env.now)
    print(f'Traza {trace_id}: Tiempo {env.now}: Completando actividad {trans_label}. End timestamp {end_timestamp}')
    results_log.append([trace_id, trans_label, str(start_timestamp), str(end_timestamp)])

    if arrival_or_departure == 0:
        sh.last_timestamp_recorded = end_timestamp
