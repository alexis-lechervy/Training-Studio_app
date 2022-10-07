from typing import List

from lightning.app.utilities.commands import ClientCommand
from rich.console import Console
from rich.table import Table

from lightning_hpo.commands.sweep.run import SweepConfig


def _show_experiments(sweeps: List[SweepConfig]):
    table = Table(
        "name",
        "status",
        "best_model_score",
        "sweep_id",
        title="Experiments",
        show_header=True,
        header_style="bold green",
    )

    for sweep in sweeps:
        trials = sweep.trials.values()
        for trial in trials:
            table.add_row(
                str(trial.name),
                str(trial.stage),
                str(round(trial.best_model_score, 2) if trial.best_model_score else None),
                None if len(trials) == 1 else sweep.sweep_id,
            )
    console = Console()
    console.print(table)


class ShowExperimentsCommand(ClientCommand):

    DESCRIPTION = "Command to show experiments"

    def run(self) -> None:
        # 1: Collect the SweepConfig
        resp = self.invoke_handler()

        # 3: Display the Sweeps or Sweep
        # TODO: Undestand why the format isn't the same
        try:
            sweeps = [SweepConfig.parse_raw(sweep) for sweep in resp]
        except Exception:
            sweeps = [SweepConfig(**sweep) for sweep in resp]

        _show_experiments(sweeps)