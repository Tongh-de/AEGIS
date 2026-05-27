import logging
from typing import Optional, List, ClassVar

from pydantic import Field

from Base.Ai.llms.qwenLlm import get_default_qwen_llm
from Base.Repository.base.baseVDB import BaseVDBModel

logger = logging.getLogger(__name__)


class KnowledgeDocVdb(BaseVDBModel):
    """合规知识文档向量数据库模型"""
    collection_alias: ClassVar[str] = "compliance_knowledge"
    description: ClassVar[str] = "合规知识库表"

    id: Optional[int] = Field(
        default=0,
        json_schema_extra={'is_primary': True, 'auto_id': True}
    )

    doc_id: Optional[str] = Field(
        default='',
        json_schema_extra={'max_length': 64}
    )

    doc_name: Optional[str] = Field(
        default='',
        json_schema_extra={'max_length': 256}
    )

    chunk_index: Optional[str] = Field(
        default='',
        json_schema_extra={'max_length': 10}
    )

    content: Optional[str] = Field(
        default='',
        json_schema_extra={
            'max_length': 65535,
            'enable_match': True,
            'enable_analyzer': True
        }
    )

    source_type: Optional[str] = Field(
        default='',
        json_schema_extra={'max_length': 32}
    )

    source_url: Optional[str] = Field(
        default='',
        json_schema_extra={'max_length': 1024}
    )

    tags: Optional[str] = Field(
        default='',
        json_schema_extra={'max_length': 1024}
    )

    effective_date: Optional[str] = Field(
        default='',
        json_schema_extra={'max_length': 32}
    )

    version: Optional[str] = Field(
        default='',
        json_schema_extra={'max_length': 32}
    )

    embedding: Optional[List[float]] = Field(
        default_factory=list,
        json_schema_extra={'dim': 1024}
    )

    content_sparse: Optional[List[float]] = Field(
        default_factory=list,
        json_schema_extra={
            'is_sparse_vector': True,
            'bm25_source_field': 'content'
        }
    )

    @classmethod
    def search_knowledge(cls, query: str, limit: int = 5,
                         source_type: Optional[str] = None,
                         tags: Optional[str] = None) -> List[dict]:
        """
        混合搜索知识库：dense (0.7) + BM25 (0.3)

        Args:
            query: 检索查询文本
            limit: 返回结果数量上限
            source_type: 按来源类型过滤
            tags: 按标签过滤

        Returns:
            List[dict]: 搜索结果列表，每项含 doc_name, content, score 等
        """
        try:
            cls._check_and_create_collection()
            llm = get_default_qwen_llm()
            query_embedding = llm.embedding(text=query, dimensions=1024)

            filter_expr = ''
            filters = []
            if source_type:
                filters.append(f'source_type == "{source_type}"')
            if tags:
                filters.append(f'tags like "%{tags}%"')
            if filters:
                filter_expr = ' && '.join(filters)

            results = cls.hybrid_search(
                query_vector=query_embedding[0] if isinstance(query_embedding, list) else query_embedding,
                query_text=query,
                output_fields=['doc_id', 'doc_name', 'chunk_index', 'content',
                               'source_type', 'source_url', 'tags',
                               'effective_date', 'version'],
                filter_expr=filter_expr,
                limit=limit,
                dense_weight=0.7
            )
            return results if results else []
        except Exception as e:
            logger.warning(f"知识库检索失败（Milvus 不可用），降级返回空列表：{e}")
            return []

    @classmethod
    def retrieve_context(cls, query: str, limit: int = 5,
                         source_type: Optional[str] = None,
                         tags: Optional[str] = None) -> str:
        """
        检索知识库并返回格式化的法规上下文文本，供 Prompt 注入使用。
        Milvus 不可用时返回空字符串，系统降级为无 RAG 模式。

        Args:
            query: 检索查询文本
            limit: 返回结果数量上限
            source_type: 按来源类型过滤
            tags: 按标签过滤

        Returns:
            str: 格式化的法规上下文文本，或空字符串
        """
        results = cls.search_knowledge(query, limit, source_type, tags)
        if not results:
            return ''

        lines = []
        for i, r in enumerate(results, 1):
            doc_name = r.get('doc_name', '未知文档')
            content = r.get('content', '')
            lines.append(f"[法规{i}] 《{doc_name}》\n{content}")

        return '\n\n'.join(lines)

    @classmethod
    def delete_by_doc_id(cls, doc_id: str) -> bool:
        """按 doc_id 删除该文档的所有分块"""
        try:
            cls._check_and_create_collection()
            cls.delete(filter_expr=f'doc_id == "{doc_id}"')
            return True
        except Exception as e:
            logger.error(f"删除文档分块失败 doc_id={doc_id}：{e}")
            return False

    @classmethod
    def batch_insert_chunks(cls, chunks: List['KnowledgeDocVdb'],
                            batch_size: int = 100) -> dict:
        """
        批量插入分块（含 embedding 生成）

        Args:
            chunks: 已填充字段（含 content）的分块列表
            batch_size: 批量插入大小

        Returns:
            dict: {'inserted': int, 'failed': int}
        """
        try:
            cls._check_and_create_collection()
            llm = get_default_qwen_llm()

            inserted = 0
            failed = 0
            batch = []

            for i, chunk in enumerate(chunks):
                try:
                    if chunk.content:
                        emb = llm.embedding(text=chunk.content, dimensions=1024)
                        chunk.embedding = emb[0] if isinstance(emb, list) else emb
                    batch.append(chunk)

                    if len(batch) >= batch_size:
                        result = cls.batch_insert(batch)
                        inserted += result.get('insert_count', len(batch))
                        batch = []

                except Exception as e:
                    failed += 1
                    logger.error(f"分块 {i} 嵌入/插入失败：{e}")

            if batch:
                result = cls.batch_insert(batch)
                inserted += result.get('insert_count', len(batch))

            logger.info(f"知识库批量插入完成：成功 {inserted}，失败 {failed}")
            return {'inserted': inserted, 'failed': failed}

        except Exception as e:
            logger.error(f"批量插入知识库失败：{e}")
            return {'inserted': 0, 'failed': len(chunks) if chunks else 0}

    @classmethod
    def list_documents(cls) -> List[dict]:
        """列出知识库中所有不重复的文档"""
        try:
            cls._check_and_create_collection()
            results = cls.query(
                output_fields=['doc_id', 'doc_name', 'source_type', 'tags',
                               'effective_date', 'version'],
                limit=10000
            )
            seen = set()
            docs = []
            for r in results:
                did = r.get('doc_id', '')
                if did and did not in seen:
                    seen.add(did)
                    docs.append({
                        'doc_id': did,
                        'doc_name': r.get('doc_name', ''),
                        'source_type': r.get('source_type', ''),
                        'tags': r.get('tags', ''),
                        'effective_date': r.get('effective_date', ''),
                        'version': r.get('version', ''),
                    })
            return docs
        except Exception as e:
            logger.error(f"列出知识库文档失败：{e}")
            return []
