import csm.engine as ce

import redis
import json
import os


class RedisConsumer(ce.Consumer):
    client: redis.Redis = None
    simulation_id: str = None
    existing_probes: list = []

    def Consume(self, p_data):
        tmp = json.loads(ce.StarProbeOutput.Cast(p_data).GetJSON())
        probe_name = tmp['probe']['name']
        if probe_name not in self.existing_probes:
            self.client.json().set(self.simulation_id, probe_name, [])

            self.existing_probes.append(probe_name)
        common_data = dict()
        common_data.update(tmp['simulation'])
        common_data.update(tmp['probe'])
        common_data.update(tmp['facts_common'])
        for data in tmp['facts']:
            new_row = dict()
            new_row.update(common_data)
            new_row.update(data)
            self.client.json().arrappend(self.simulation_id, probe_name, new_row)


def main():
    sim = ce.LoadSimulator(os.environ["CSM_SIMULATION"])

    consumer = RedisConsumer("RedisConsumer")
    redis_host = os.environ['REDIS_HOST']
    redis_port = os.environ['REDIS_PORT']
    redis_password = os.environ['REDIS_PASSWORD']
    consumer.client = redis.Redis(host=redis_host, port=redis_port, db=0, password=redis_password)

    consumer.simulation_id = os.environ["CSM_SIMULATION_ID"]
    consumer.client.json().set(consumer.simulation_id, "$", {})
    for probe in sim.GetProbes():
        consumer.Connect(probe)

    sim.Run()


if __name__ == '__main__':
    main()
