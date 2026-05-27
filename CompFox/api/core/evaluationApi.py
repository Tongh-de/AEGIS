import logging
from typing import Optional, List

from fastapi import APIRouter, Query, Body
from pydantic import BaseModel, Field

from Base.RicUtils.httpUtils import HttpResponse
from CompFox.services.evaluationService import get_evaluation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compfox/evaluation")


# --- Request models ---

class EvalRetrievalRequest(BaseModel):
    dataset_name: str = Field(..., description="数据集名称（不含 .json 后缀）")
    k_values: Optional[List[int]] = Field(None, description="k 值列表，默认用数据集的")
    granularity: str = Field("document", description="评测粒度：document 或 chunk")
    source_type: Optional[str] = Field(None, description="按来源类型过滤")
    tags: Optional[str] = Field(None, description="按标签过滤")
    save_snapshot: bool = Field(True, description="是否保存结果快照")
    snapshot_label: Optional[str] = Field(None, description="快照标签")


class CompareSnapshotsRequest(BaseModel):
    snapshot_paths: List[str] = Field(..., description="快照文件路径列表")
    k_values: Optional[List[int]] = Field(None, description="关注的 k 值")


class EvalGenerationRequest(BaseModel):
    dataset_name: str = Field(..., description="数据集名称（不含 .json 后缀）")


# --- Endpoints ---

@router.get("/datasets")
def list_datasets():
    """列出可用评测数据集"""
    try:
        svc = get_evaluation_service()
        datasets = svc.list_datasets()
        return HttpResponse.ok(datasets)
    except Exception as e:
        logger.error(f"列出数据集失败：{e}")
        return HttpResponse.error(str(e))


@router.post("/retrieval")
def eval_retrieval(req: EvalRetrievalRequest):
    """运行检索评测"""
    try:
        svc = get_evaluation_service()
        result = svc.evaluate_retrieval(
            dataset_name=req.dataset_name,
            k_values=req.k_values,
            granularity=req.granularity,
            source_type=req.source_type,
            tags=req.tags,
            save_snapshot=req.save_snapshot,
            snapshot_label=req.snapshot_label,
        )
        return HttpResponse.ok(result)
    except FileNotFoundError as e:
        return HttpResponse.error(str(e))
    except ValueError as e:
        return HttpResponse.error(str(e))
    except Exception as e:
        logger.error(f"检索评测失败：{e}")
        return HttpResponse.error(str(e))


@router.get("/snapshots")
def list_snapshots(dataset_name: Optional[str] = Query(None, description="按数据集名称过滤")):
    """列出评测结果快照"""
    try:
        svc = get_evaluation_service()
        snapshots = svc.list_snapshots(dataset_name)
        return HttpResponse.ok(snapshots)
    except Exception as e:
        logger.error(f"列出快照失败：{e}")
        return HttpResponse.error(str(e))


@router.post("/compare")
def compare_snapshots(req: CompareSnapshotsRequest):
    """对比多个评测结果快照"""
    try:
        svc = get_evaluation_service()
        result = svc.compare_snapshots(
            snapshot_paths=req.snapshot_paths,
            k_values=req.k_values,
        )
        return HttpResponse.ok(result)
    except ValueError as e:
        return HttpResponse.error(str(e))
    except Exception as e:
        logger.error(f"快照对比失败：{e}")
        return HttpResponse.error(str(e))


@router.post("/generation")
def eval_generation(req: EvalGenerationRequest):
    """LLM-as-Judge 生成评测"""
    try:
        svc = get_evaluation_service()
        result = svc.evaluate_generation(dataset_name=req.dataset_name)
        return HttpResponse.ok(result)
    except FileNotFoundError as e:
        return HttpResponse.error(str(e))
    except Exception as e:
        logger.error(f"生成评测失败：{e}")
        return HttpResponse.error(str(e))
