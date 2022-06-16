import pathlib
import optuna
from lightning import LightningFlow, CloudCompute, LightningApp
from lightning_hpo import BaseObjectiveWork, OptunaPythonScript
from lightning.app.storage.path import Path

class MyCustomObjective(BaseObjectiveWork):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.best_model_path = None

    def on_after_run(self, script_globals):
        self.best_model_score = float(script_globals["cli"].trainer.checkpoint_callback.best_model_score)
        self.best_model_path = Path(script_globals["cli"].trainer.checkpoint_callback.best_model_path)

    @staticmethod
    def distributions():
        return {"model.lr": optuna.distributions.LogUniformDistribution(0.0001, 0.1)}


class RootFlow(LightningFlow):

    def __init__(self):
        super().__init__()
        self.hpo_train = OptunaPythonScript(
            script_path=str(pathlib.Path(__file__).parent / "scripts/train.py"),
            total_trials=4,
            objective_work_cls=MyCustomObjective,
            script_args=[
                "--trainer.max_epochs=5",
                "--trainer.limit_train_batches=4",
                "--trainer.limit_val_batches=4",
                "--trainer.callbacks=ModelCheckpoint",
                "--trainer.callbacks.monitor=val_acc",
            ],
            cloud_compute=CloudCompute("default"),
        )

    def run(self):
        self.hpo_train.run()

        if self.hpo_train.best_model_path:
            pass

    def configure_layout(self):
        return [{"name": "HiPlot", "content": self.hpo_train.hi_plot}]

app = LightningApp(RootFlow())
