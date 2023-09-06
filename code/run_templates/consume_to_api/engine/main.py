import csm.engine as ce

import json
import os
import cosmotech_api
from azure.identity import DefaultAzureCredential

from cosmotech_api.api import scenariorunresult_api
from cosmotech_api.model.scenario_run_result import ScenarioRunResult

from cosmotech_api.api import organization_api
from cosmotech_api.model.organization import Organization


class ApiConsumer(ce.Consumer):
    resultsApi: scenariorunresult_api.ScenariorunresultApi = None
    simulation_id: str = None

    def Consume(self, p_data):
        tmp = json.loads(ce.StarProbeOutput.Cast(p_data).GetJSON())
        probe_name = tmp['probe']['name']
        common_data = dict()
        common_data.update(tmp['simulation'])
        common_data.update(tmp['probe'])
        common_data.update(tmp['facts_common'])
        for data in tmp['facts']:
            new_row = dict()
            new_row.update(common_data)
            new_row.update(data)

        self.resultsApi.send_scenario_run_result(os.getenv('CSM_ORGANIZATION_ID'), os.getenv('CSM_WORKSPACE_ID'), os.getenv('CSM_SCENARIO_ID'), self.simulation_id, probe_name, new_row)


def main():
    sim = ce.LoadSimulator(os.environ["CSM_SIMULATION"])

    default_cred = DefaultAzureCredential()
    configuration = cosmotech_api.Configuration(host=os.getenv('CSM_API_URL'),
                                                discard_unknown_keys=True,
                                                access_token=default_cred.get_token(
                                                    os.getenv('CSM_API_SCOPE')).token)

    with cosmotech_api.ApiClient(configuration) as api_client:
        consumer = ApiConsumer("ApiConsumer")
        consumer.resultsApi = scenariorunresult_api.ScenariorunresultApi(api_client)
        consumer.simulation_id = os.environ["CSM_SIMULATION_ID"]

        for probe in sim.GetProbes():
            consumer.Connect(probe)

        sim.Run()


if __name__ == '__main__':
    main()
