from __future__ import annotations

# ruff: noqa: E402
import logging
from pathlib import Path
from typing import Any, cast

import hydra
import rootutils
import torch.distributed as dist
from omegaconf import DictConfig, OmegaConf

rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True, dotenv=True)

from adapters.vlmeval_adapter import VLMEvalAdapter
from methods.base_method import BaseMethod
from models.base import BaseMLLMWrapper
from utils import dist_utils
from utils.experiment_logger import NullExperimentLogger, create_experiment_logger
from utils.instantiate import instantiate_from_config
from utils.logging import setup_logging
from utils.task_utils import prepare_task, seed_everything

log = logging.getLogger(__name__)
build_dataset: Any | None = None
infer_data_job: Any | None = None
get_pred_file_path: Any | None = None


def _load_vlmeval_api() -> tuple[Any, Any, Any]:
    global build_dataset, infer_data_job, get_pred_file_path
    if build_dataset is not None and infer_data_job is not None and get_pred_file_path is not None:
        return build_dataset, infer_data_job, get_pred_file_path
    try:
        from vlmeval.dataset import build_dataset as vlmeval_build_dataset
        from vlmeval.inference import infer_data_job as vlmeval_infer_data_job
        from vlmeval.smp import get_pred_file_path as vlmeval_get_pred_file_path
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "VLMEvalKit is required for src/eval.py. Install the PyPI distribution "
            "`ms-vlmeval` in an evaluation environment; see README dependency notes."
        ) from exc
    build_dataset = vlmeval_build_dataset
    infer_data_job = vlmeval_infer_data_job
    get_pred_file_path = vlmeval_get_pred_file_path
    return build_dataset, infer_data_job, get_pred_file_path


def _extract_metric(metrics: Any, metric_name: str | None) -> float | None:
    if not metric_name:
        return None
    if not isinstance(metrics, dict) or metric_name not in metrics:
        raise KeyError(f"optimized_metric={metric_name!r} not found in evaluation results.")
    value = metrics[metric_name]
    if hasattr(value, "item"):
        value = value.item()
    return float(value)


def _to_plain_dict(config: object) -> dict[str, Any]:
    if config is None:
        return {}
    value = OmegaConf.to_container(config, resolve=True) if OmegaConf.is_config(config) else config
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise TypeError(f"Expected mapping config, got {type(value).__name__}.")
    return dict(value)


def evaluate_once(cfg: DictConfig) -> float | None:
    seed = None if cfg.get("seed") is None else int(cfg.seed)
    seed_everything(seed)
    dist_utils.init_distributed(cfg.env)
    setup_logging()
    prepare_task(cfg)
    device = dist_utils.get_device()
    world_size = dist_utils.get_world_size()
    experiment_logger = NullExperimentLogger()
    optimized_metric = None if cfg.get("optimized_metric") is None else str(cfg.optimized_metric)
    metric_value: float | None = None

    try:
        experiment_logger = create_experiment_logger(cfg)
        experiment_logger.log_hyperparams(
            {
                "task_name": cfg.get("task_name"),
                "tags": cfg.get("tags"),
                "seed": cfg.get("seed"),
                "model": cfg.get("model"),
                "method": cfg.get("method"),
                "env": cfg.get("env"),
                "eval_tasks": cfg.get("eval_tasks"),
            }
        )

        model: BaseMLLMWrapper = instantiate_from_config(cfg.model)
        method: BaseMethod = instantiate_from_config(cfg.method)
        model.setup(device)
        method.setup(model, device)
        adapter = VLMEvalAdapter(model_wrapper=model, method=method, device=device)

        output_dir = Path(str(cfg.paths.eval_output_dir))
        output_dir.mkdir(parents=True, exist_ok=True)
        model_name = str(cfg.model_name)
        dataset_kwargs = _to_plain_dict(cfg.eval_tasks.get("dataset_kwargs"))
        judge_kwargs = _to_plain_dict(cfg.eval_tasks.get("judge"))
        (
            vlmeval_build_dataset,
            vlmeval_infer_data_job,
            vlmeval_get_pred_file_path,
        ) = _load_vlmeval_api()

        for dataset_name in cfg.eval_tasks.datasets:
            dataset_name = str(dataset_name)
            if dist_utils.is_main_process():
                log.info(
                    "Evaluating %s with model_name=%s world_size=%d.",
                    dataset_name,
                    model_name,
                    world_size,
                )

            dataset = vlmeval_build_dataset(dataset_name, **dataset_kwargs)
            if dataset is None:
                raise ValueError(f"VLMEvalKit could not build dataset: {dataset_name}")

            vlmeval_infer_data_job(
                model=adapter,
                work_dir=str(output_dir),
                model_name=model_name,
                dataset=dataset,
                verbose=bool(cfg.verbose),
                api_nproc=int(cfg.api_nproc),
                retry_failed=bool(cfg.retry_failed),
            )

            if dist.is_available() and dist.is_initialized():
                dist.barrier()

            if str(cfg.mode) == "infer":
                continue

            if dist_utils.is_main_process():
                result_file = vlmeval_get_pred_file_path(
                    str(output_dir),
                    model_name,
                    dataset_name,
                    use_env_format=True,
                )
                eval_results = dataset.evaluate(result_file, **judge_kwargs)
                if isinstance(eval_results, dict):
                    experiment_logger.log_metrics(cast(dict[str, Any], eval_results))
                    extracted_metric = _extract_metric(eval_results, optimized_metric)
                    if extracted_metric is not None:
                        metric_value = extracted_metric
                log.info(
                    "Finished %s. result_file=%s eval_results=%s",
                    dataset_name,
                    result_file,
                    eval_results,
                )

            if dist.is_available() and dist.is_initialized():
                dist.barrier()
        return metric_value
    finally:
        experiment_logger.finish()
        dist_utils.cleanup_distributed()


@hydra.main(version_base="1.3", config_path="../configs", config_name="eval")
def main(cfg: DictConfig) -> float | None:
    return evaluate_once(cfg)


if __name__ == "__main__":
    main()
