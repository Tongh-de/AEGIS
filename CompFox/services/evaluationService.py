import json
import logging
import math
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

import numpy as np
from pydantic import BaseModel

from CompFox.models.vdb.knowledgeDocVdb import KnowledgeDocVdb
from Base.Ai.llms.qwenLlm import get_default_qwen_llm

logger = logging.getLogger(__name__)

DATASET_DIR = Path("CompFox/data/eval_datasets")
RESULT_DIR = Path("CompFox/data/eval_results")


# ============================================================
# 数据集加载与校验
# ============================================================

def _load_dataset(name: str) -> dict:
    """加载并校验评测数据集"""
    path = DATASET_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"数据集不存在：{path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 校验
    if "queries" not in data:
        raise ValueError("数据集缺少 'queries' 字段")
    if not isinstance(data["queries"], list) or len(data["queries"]) == 0:
        raise ValueError("'queries' 必须是非空列表")

    for i, q in enumerate(data["queries"]):
        if "query_id" not in q:
            raise ValueError(f"queries[{i}] 缺少 'query_id'")
        if "query_text" not in q:
            raise ValueError(f"queries[{i}] 缺少 'query_text'")
        if "relevant_doc_ids" not in q:
            raise ValueError(f"queries[{i}] 缺少 'relevant_doc_ids'")

    return data


def list_datasets() -> List[dict]:
    """列出可用评测数据集"""
    if not DATASET_DIR.exists():
        return []
    datasets = []
    for f in sorted(DATASET_DIR.glob("*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            datasets.append({
                "name": f.stem,
                "title": data.get("name", f.stem),
                "version": data.get("version", ""),
                "description": data.get("description", ""),
                "num_queries": len(data.get("queries", [])),
                "file": str(f),
            })
        except Exception:
            datasets.append({"name": f.stem, "title": f.stem, "error": "无法解析"})
    return datasets


# ============================================================
# 指标计算（纯函数，可单测）
# ============================================================

def _compute_metrics(
    query_results: List[dict],
    relevant_ids: set,
    k_values: List[int],
    granularity: str = "document",
) -> dict:
    """
    对单个 query 的检索结果计算所有指标

    Args:
        query_results: search_knowledge 返回的 ranked list，每项含 doc_id, chunk_index 等
        relevant_ids: 标注的相关 ID 集合。document 粒度时是 doc_id 集合，
                      chunk 粒度时是 "doc_id::chunk_index" 集合
        k_values: 需要计算的 k 值列表，如 [3, 5, 10]

    Returns:
        dict: 各指标值
    """
    if not relevant_ids:
        return _empty_metrics(k_values)

    if not query_results:
        return _empty_metrics(k_values)

    # 构建 ranked hits 列表（去重，保留首次出现的最高 rank）
    if granularity == "document":
        seen = set()
        ranked = []
        for r in query_results:
            did = r.get("doc_id", "")
            if did and did not in seen:
                seen.add(did)
                ranked.append(did)
    else:  # chunk
        seen = set()
        ranked = []
        for r in query_results:
            cid = f"{r.get('doc_id', '')}::{r.get('chunk_index', '')}"
            if cid not in seen:
                seen.add(cid)
                ranked.append(cid)

    hits = [1 if item in relevant_ids else 0 for item in ranked]

    max_k = max(k_values) if k_values else 10
    metrics = {}

    # Precision@k, Recall@k, Hit@k
    num_relevant = len(relevant_ids)
    for k in k_values:
        top_hits = hits[:k]
        hit_count = sum(top_hits)
        metrics[f"precision@{k}"] = hit_count / k if k > 0 else 0.0
        metrics[f"recall@{k}"] = hit_count / num_relevant if num_relevant > 0 else 0.0
        metrics[f"hit@{k}"] = 1.0 if hit_count > 0 else 0.0

    # MRR
    mrr = 0.0
    for i, h in enumerate(hits):
        if h == 1:
            mrr = 1.0 / (i + 1)
            break
    metrics["mrr"] = mrr

    # NDCG@k
    for k in k_values:
        dcg = 0.0
        for i in range(min(k, len(hits))):
            if hits[i]:
                dcg += 1.0 / math.log2(i + 2)  # i+2 because 1-indexed
        idcg = sum(1.0 / math.log2(i + 2) for i in range(min(num_relevant, k)))
        metrics[f"ndcg@{k}"] = dcg / idcg if idcg > 0 else 0.0

    return metrics


def _empty_metrics(k_values: List[int]) -> dict:
    m = {"mrr": 0.0}
    for k in k_values:
        m[f"precision@{k}"] = 0.0
        m[f"recall@{k}"] = 0.0
        m[f"hit@{k}"] = 0.0
        m[f"ndcg@{k}"] = 0.0
    return m


def _aggregate_metrics(all_per_query: List[dict], skipped: int) -> dict:
    """macro-average 所有 query 的指标"""
    if not all_per_query:
        return {"total_queries": skipped, "skipped_queries": skipped, "metrics": {}, "error": "所有 query 被跳过（Milvus 不可用或数据集问题）"}

    metric_names = [k for k in all_per_query[0].keys() if k != "query_id"]
    aggregated = {}
    for name in metric_names:
        values = [q[name] for q in all_per_query if name in q]
        aggregated[name] = {
            "mean": round(float(np.mean(values)), 4),
            "std": round(float(np.std(values)), 4),
        }

    return {
        "total_queries": len(all_per_query) + skipped,
        "skipped_queries": skipped,
        "evaluated_queries": len(all_per_query),
        "metrics": aggregated,
    }


# ============================================================
# 评测流程
# ============================================================

def _build_relevant_set(query: dict, granularity: str) -> set:
    """根据粒度构建相关 ID 集合"""
    if granularity == "chunk" and query.get("relevant_chunks"):
        return {f"{c['doc_id']}::{c['chunk_index']}" for c in query["relevant_chunks"]}
    return set(query.get("relevant_doc_ids", []))


def evaluate_retrieval(
    dataset_name: str,
    k_values: Optional[List[int]] = None,
    granularity: str = "document",
    source_type: Optional[str] = None,
    tags: Optional[str] = None,
    save_snapshot: bool = True,
    snapshot_label: Optional[str] = None,
) -> dict:
    """
    运行检索评测

    Args:
        dataset_name: 数据集名称（不含 .json 后缀）
        k_values: 要计算的 k 值列表，默认用数据集里的 k_values
        granularity: "document" 或 "chunk"
        source_type: 按来源类型过滤检索
        tags: 按标签过滤检索
        save_snapshot: 是否保存结果快照
        snapshot_label: 快照标签（如 "chunk500_overlap80"）
    """
    data = _load_dataset(dataset_name)
    queries = data["queries"]
    k_values = k_values or data.get("k_values", [3, 5, 10])

    per_query = []
    skipped = 0

    for q in queries:
        query_id = q["query_id"]
        relevant_ids = _build_relevant_set(q, granularity)

        if not relevant_ids:
            logger.warning(f"跳过 query {query_id}：relevant_doc_ids 为空")
            skipped += 1
            continue

        try:
            results = KnowledgeDocVdb.search_knowledge(
                query=q["query_text"],
                limit=max(k_values),
                source_type=source_type or data.get("source_type"),
                tags=tags or data.get("tags"),
            )
        except Exception as e:
            logger.warning(f"检索失败 query {query_id}：{e}")
            results = []

        if not results:
            skipped += 1
            continue

        metrics = _compute_metrics(results, relevant_ids, k_values, granularity)
        metrics["query_id"] = query_id
        per_query.append(metrics)

    aggregated = _aggregate_metrics(per_query, skipped)

    result = {
        "dataset": dataset_name,
        "granularity": granularity,
        "k_values": k_values,
        "evaluated_at": datetime.now().isoformat(),
        **aggregated,
        "per_query": per_query,
    }

    if save_snapshot:
        _save_snapshot(result, dataset_name, snapshot_label)

    return result


def _save_snapshot(result: dict, dataset_name: str, label: Optional[str] = None):
    """保存评测结果快照"""
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    label_part = f"_{label}" if label else ""
    filename = f"{dataset_name}{label_part}_{ts}.json"
    path = RESULT_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info(f"评测结果已保存：{path}")


# ============================================================
# 快照对比
# ============================================================

def list_snapshots(dataset_name: Optional[str] = None) -> List[dict]:
    """列出评测结果快照"""
    if not RESULT_DIR.exists():
        return []
    snapshots = []
    pattern = f"{dataset_name}_*.json" if dataset_name else "*.json"
    for f in sorted(RESULT_DIR.glob(pattern), reverse=True):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            snapshots.append({
                "file": f.name,
                "path": str(f),
                "dataset": data.get("dataset", ""),
                "evaluated_at": data.get("evaluated_at", ""),
                "total_queries": data.get("total_queries", 0),
                "evaluated_queries": data.get("evaluated_queries", 0),
                "granularity": data.get("granularity", "document"),
            })
        except Exception:
            snapshots.append({"file": f.name, "path": str(f), "error": "无法解析"})
    return snapshots


def compare_snapshots(
    snapshot_paths: List[str],
    k_values: Optional[List[int]] = None,
) -> dict:
    """
    对比多个评测结果快照

    Args:
        snapshot_paths: 快照文件路径列表
        k_values: 关注的 k 值

    Returns:
        对比结果，含每个快照的指标 + 最优标注
    """
    if not snapshot_paths:
        raise ValueError("至少需要 2 个快照进行对比")

    k_values = k_values or [3, 5, 10]
    configs = []

    for path in snapshot_paths:
        with open(path, "r", encoding="utf-8") as f:
            snap = json.load(f)

        metrics = snap.get("metrics", {})
        row = {
            "file": os.path.basename(path),
            "dataset": snap.get("dataset", ""),
            "evaluated_at": snap.get("evaluated_at", ""),
            "evaluated_queries": snap.get("evaluated_queries", 0),
            "skipped_queries": snap.get("skipped_queries", 0),
        }
        for name, vals in metrics.items():
            if isinstance(vals, dict) and "mean" in vals:
                row[name] = vals["mean"]
            else:
                row[name] = vals
        configs.append(row)

    # 找出每个指标的最优值
    best = {}
    metric_keys = [k for k in configs[0].keys() if k not in ("file", "dataset", "evaluated_at", "evaluated_queries", "skipped_queries")]
    for key in metric_keys:
        values = [(c["file"], c.get(key, 0)) for c in configs if isinstance(c.get(key), (int, float))]
        if values:
            best[key] = max(values, key=lambda x: x[1])

    return {
        "k_values": k_values,
        "configs": configs,
        "best_by_metric": {k: {"file": v[0], "value": v[1]} for k, v in best.items()},
        "metric_keys": metric_keys,
    }


# ============================================================
# LLM 生成评测
# ============================================================

JUDGE_PROMPT = """你是一个合规知识库助手的评估专家。请根据以下信息，判断生成答案的质量。

【检索到的法规上下文】
{context}

【用户问题】
{query}

【参考答案（人工标注）】
{ground_truth}

【系统生成的答案】
{generated_answer}

请从以下三个维度打分（1-3分）：
1. 忠实度（Faithfulness）：生成答案中的每一条陈述是否都能从检索到的法规上下文中找到依据？
   3分=全部有据可查，2分=大部分有据可查，1分=大量编造
2. 答案相关性（Answer Relevance）：生成答案是否直接回应了用户的问题？
   3分=精准回应，2分=部分相关，1分=答非所问
3. 事实正确性（Factual Correctness）：与参考答案相比，生成答案的事实是否准确？
   3分=完全正确，2分=基本正确有小错，1分=关键事实错误

请以 JSON 格式返回评分结果，不要包含其他内容：
{{"faithfulness": int, "relevance": int, "correctness": int, "overall": float, "brief_reason": "string"}}"""

ANSWER_PROMPT = """你是一个金融合规知识助手。请根据以下法规上下文回答用户问题。

【法规上下文】
{context}

【用户问题】
{query}

请给出专业、准确的回答。如果法规上下文中没有相关信息，请明确说明。"""


def evaluate_generation(dataset_name: str) -> dict:
    """
    LLM-as-Judge 生成评测

    对数据集中所有包含 ground_truth 的 query：
    1. 检索法规上下文
    2. LLM 基于上下文生成答案
    3. LLM Judge 打分（忠实度/相关性/正确性）
    """
    data = _load_dataset(dataset_name)
    queries = [q for q in data["queries"] if q.get("ground_truth")]

    if not queries:
        return {"error": "数据集中没有包含 ground_truth 的 query"}

    llm = get_default_qwen_llm()
    scores = []

    for q in queries:
        query_id = q["query_id"]
        try:
            context = KnowledgeDocVdb.retrieve_context(q["query_text"], limit=3)
            if not context:
                context = "（暂无法规上下文）"

            # 生成答案
            answer_prompt = ANSWER_PROMPT.format(context=context, query=q["query_text"])
            generated = llm.invoke(answer_prompt)

            # Judge 打分
            judge_prompt = JUDGE_PROMPT.format(
                context=context,
                query=q["query_text"],
                ground_truth=q["ground_truth"],
                generated_answer=generated,
            )
            judge_resp = llm.invoke(judge_prompt)

            # 解析 JSON
            judge_resp = judge_resp.strip()
            if judge_resp.startswith("```json"):
                judge_resp = judge_resp[7:]
            if judge_resp.startswith("```"):
                judge_resp = judge_resp[3:]
            if judge_resp.endswith("```"):
                judge_resp = judge_resp[:-3]
            judge_data = json.loads(judge_resp.strip())

            scores.append({
                "query_id": query_id,
                "faithfulness": int(judge_data.get("faithfulness", 0)),
                "relevance": int(judge_data.get("relevance", 0)),
                "correctness": int(judge_data.get("correctness", 0)),
                "overall": float(judge_data.get("overall", 0)),
                "reason": judge_data.get("brief_reason", ""),
                "generated_answer": generated,
            })

        except Exception as e:
            logger.error(f"生成评测失败 query {query_id}：{e}")
            scores.append({"query_id": query_id, "error": str(e)})

    # 汇总
    valid = [s for s in scores if "error" not in s]
    if valid:
        aggregated = {
            "faithfulness": round(float(np.mean([s["faithfulness"] for s in valid])), 2),
            "relevance": round(float(np.mean([s["relevance"] for s in valid])), 2),
            "correctness": round(float(np.mean([s["correctness"] for s in valid])), 2),
            "overall": round(float(np.mean([s["overall"] for s in valid])), 2),
        }
    else:
        aggregated = {}

    return {
        "dataset": dataset_name,
        "total_with_ground_truth": len(queries),
        "evaluated": len(valid),
        "failed": len(scores) - len(valid),
        "aggregated_scores": aggregated,
        "per_query": scores,
    }


# ============================================================
# 服务单例
# ============================================================

class EvaluationService(BaseModel):
    """RAG 评测服务"""

    list_datasets = staticmethod(list_datasets)
    evaluate_retrieval = staticmethod(evaluate_retrieval)
    compare_snapshots = staticmethod(compare_snapshots)
    list_snapshots = staticmethod(list_snapshots)
    evaluate_generation = staticmethod(evaluate_generation)


evaluation_service = EvaluationService()


def get_evaluation_service():
    return evaluation_service
