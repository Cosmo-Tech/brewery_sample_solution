import comets as co
import os


def main():

    simulator = co.CosmoInterface(
        simulator_path="BreweryDemoSimulationWithConnector",
        amqp_consumer_address=os.environ.get("CSM_PROBES_MEASURES_TOPIC", None),
        simulation_name=os.environ.get("CSM_SIMULATION_VAR", "Simulation"),
    )

    simulator.initialize()

    parameter = {
        "Model::{Entity}MyBar::@NbWaiters": 10,
        "Model::{Entity}MyBar::@RestockQty": 12,
    }
    simulator.set_inputs(parameter)

    simulator.run()

    simulator.terminate()


if __name__ == "__main__":
    main()
