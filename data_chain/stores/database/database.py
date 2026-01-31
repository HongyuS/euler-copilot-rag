# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import Index
from datetime import datetime
import uuid
from uuid import uuid4
import urllib.parse
from data_chain.logger.logger import logger as logging
from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Column, ForeignKey, BigInteger, Float, Text, func
from sqlalchemy.types import TIMESTAMP, UUID
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import declarative_base, DeclarativeBase, MappedAsDataclass, Mapped, mapped_column
from data_chain.config.config import config
from data_chain.entities.enum import (Tokenizer,
                                      ParseMethod,
                                      TeamStatus,
                                      TeamMessageStatus,
                                      TeamUserStaus,
                                      RoleStatus,
                                      RoleActionStatus,
                                      UserRoleStatus,
                                      UserStatus,
                                      UserMessageType,
                                      UserMessageStatus,
                                      KnowledgeBaseStatus,
                                      DocParseRelutTopology,
                                      DocumentStatus,
                                      ChunkType,
                                      ChunkStatus,
                                      ImageStatus,
                                      ChunkParseTopology,
                                      DataSetStatus,
                                      QAStatus,
                                      TestingStatus,
                                      TestCaseStatus,
                                      SearchMethod,
                                      TaskType,
                                      TaskStatus)

Base = declarative_base()


class TeamEntity(Base):
    __tablename__ = 'team'

    id = Column(UUID, default=uuid4, primary_key=True)
    author_id = Column(Text)
    author_name = Column(Text)
    name = Column(Text)
    description = Column(Text)
    member_cnt = Column(BigInteger, default=0)
    is_public = Column(Boolean, default=True)
    status = Column(Text, default=TeamStatus.EXISTED.value)
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    # 添加索引
    __table_args__ = (
        Index('team_name_index', name),
        Index('team_author_id_index', author_id)
    )


class TeamMessageEntity(Base):
    __tablename__ = 'team_message'

    id = Column(UUID, default=uuid4, primary_key=True)
    team_id = Column(UUID)
    author_id = Column(Text)
    author_name = Column(Text)
    message_level = Column(Text)
    zh_message = Column(Text, default='')
    en_message = Column(Text, default='')
    status = Column(Text, default=TeamMessageStatus.EXISTED.value)
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # 添加索引
    __table_args__ = (
        Index('team_message_team_id_index', team_id),
        Index('team_message_author_id_index', author_id)
    )


class RoleEntity(Base):
    __tablename__ = 'role'

    id = Column(UUID, default=uuid4, primary_key=True)
    team_id = Column(UUID)
    name = Column(Text)
    is_unique = Column(Boolean, default=False)
    editable = Column(Boolean, default=True)
    status = Column(Text, default=RoleStatus.EXISTED.value)  # 角色状态
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    # 添加索引
    __table_args__ = (
        Index('role_team_id_index', team_id),
        Index('role_name_index', name)
    )


class ActionEntity(Base):
    __tablename__ = 'action'

    action = Column(Text, primary_key=True)
    name = Column(Text)
    type = Column(Text)
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )


class RoleActionEntity(Base):
    __tablename__ = 'role_action'

    id = Column(UUID, default=uuid4, primary_key=True)
    role_id = Column(UUID)
    action = Column(Text)
    status = Column(Text, default=RoleActionStatus.EXISTED.value)
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # 添加索引
    __table_args__ = (
        Index('role_action_role_id_index', role_id),
        Index('role_action_action_index', action)
    )


class UserEntity(Base):
    __tablename__ = 'users'

    id = Column(Text, primary_key=True)
    name = Column(Text)
    status = Column(Text, default=UserStatus.ACTIVE.value)
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # 添加索引
    __table_args__ = (
        Index('user_name_index', name),
    )


class UserMessageEntity(Base):
    __tablename__ = 'user_message'

    id = Column(UUID, default=uuid4, primary_key=True)
    team_id = Column(UUID)
    team_name = Column(Text)
    role_id = Column(UUID)
    sender_id = Column(Text)
    sender_name = Column(Text)
    status_to_sender = Column(Text, default=UserMessageStatus.UNREAD.value)
    receiver_id = Column(Text)
    receiver_name = Column(Text)
    is_to_all = Column(Boolean, default=False)
    status_to_receiver = Column(Text, default=UserMessageStatus.UNREAD.value)
    message = Column(Text)
    type = Column(Text)
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )

    # 添加索引
    __table_args__ = (
        Index('user_message_sender_id_index', sender_id),
        Index('user_message_receiver_id_index', receiver_id)
    )


class TeamUserEntity(Base):
    __tablename__ = 'team_user'

    id = Column(UUID, default=uuid4, primary_key=True)
    team_id = Column(UUID)  # 团队id
    user_id = Column(Text)  # 用户id
    status = Column(Text, default=TeamUserStaus.EXISTED.value)  # 用户在团队中的状态
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # 添加索引
    __table_args__ = (
        Index('team_user_team_id_index', team_id),
        Index('team_user_user_id_index', user_id)
    )


class UserRoleEntity(Base):
    __tablename__ = 'user_role'
    id = Column(UUID, default=uuid4, primary_key=True)
    team_id = Column(UUID)  # 团队id
    user_id = Column(Text)  # 用户id
    role_id = Column(UUID)  # 角色id
    status = Column(Text, default=UserRoleStatus.EXISTED.value)  # 用户角色状态
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # 添加索引
    __table_args__ = (
        Index('user_role_team_id_index', team_id),
        Index('user_role_user_id_index', user_id)
    )


class KnowledgeBaseEntity(Base):
    __tablename__ = 'knowledge_base'

    id = Column(UUID, default=uuid4, primary_key=True)
    team_id = Column(UUID,  nullable=True)  # 团队id
    author_id = Column(Text)  # 作者id
    author_name = Column(Text)  # 作者名称
    name = Column(Text, default='')  # 知识库名资产名
    tokenizer = Column(Text, default=Tokenizer.ZH.value)  # 分词器
    description = Column(Text, default='')  # 资产描述
    embedding_model = Column(Text)  # 资产向量化模型
    rerank_method = Column(Text)
    rerank_name = Column(Text)
    separating_characters = Column(Text)  # 资产分块的分隔符
    doc_cnt = Column(BigInteger, default=0)  # 资产文档个数
    doc_size = Column(BigInteger, default=0)  # 资产下所有文档大小(TODO: 单位kb或者字节)
    upload_count_limit = Column(BigInteger, default=128)  # 更新次数限制
    upload_size_limit = Column(BigInteger, default=512)  # 更新大小限制
    default_parse_method = Column(
        Text, default=ParseMethod.GENERAL.value)  # 默认解析方法
    default_chunk_size = Column(BigInteger, default=1024)  # 默认分块大小
    status = Column(Text, default=KnowledgeBaseStatus.IDLE.value)
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # 添加索引
    __table_args__ = (
        Index('knowledge_base_team_id_index', team_id),
        Index('knowledge_base_name_index', name)
    )


class DocumentTypeEntity(Base):
    __tablename__ = 'document_type'

    id = Column(UUID, default=uuid4, primary_key=True)
    kb_id = Column(UUID,  nullable=True)
    name = Column(Text)
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # 添加索引
    __table_args__ = (
        Index('document_type_id_index', id),
        Index('document_type_kb_id_index', kb_id),
        Index('document_type_name_index', name)
    )


class DocumentEntity(Base):
    __tablename__ = 'document'

    id = Column(UUID, default=uuid4, primary_key=True)
    team_id = Column(UUID)  # 文档所属团队id
    kb_id = Column(UUID)  # 文档所属资产id
    author_id = Column(Text)  # 文档作者id
    author_name = Column(Text)  # 文档作者名称
    name = Column(Text)  # 文档名
    extension = Column(Text)  # 文件后缀
    size = Column(BigInteger)  # 文档大小
    parse_method = Column(Text, default=ParseMethod.GENERAL.value)  # 文档解析方法
    parse_relut_topology = Column(
        Text, default=DocParseRelutTopology.LIST.value)  # 文档解析结果拓扑结构
    chunk_size = Column(BigInteger)  # 文档分块大小
    type_id = Column(UUID)  # 文档类别
    enabled = Column(Boolean)  # 文档是否启用
    status = Column(Text, default=DocumentStatus.IDLE.value)  # 文档状态
    full_text = Column(Text)  # 文档全文
    abstract = Column(Text)  # 文档摘要
    abstract_ts_vector = Column(TSVECTOR)  # 文档摘要词向量
    abstract_vector = Column(Vector(1024))  # 文档摘要向量
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    if config['DATABASE_TYPE'].lower() == 'postgres':
        __table_args__ = (
            Index('doc_kb_id_index', kb_id),
            Index('abstract_ts_vector_index',
                  abstract_ts_vector, postgresql_using='gin'),
            Index(
                'abstract_vector_index',
                abstract_vector,
                postgresql_using='hnsw',
                postgresql_with={'m': 32, 'ef_construction': 200},
                postgresql_ops={'abstract_vector': 'vector_cosine_ops'}
            )
        )
    else:
        __table_args__ = (
            Index('doc_kb_id_index', kb_id),
            Index('abstract_ts_vector_index',
                  abstract_ts_vector, postgresql_using='gin'),
            Index(
                'abstract_vector_index',
                abstract_vector,
                postgresql_using='hnsw',
                postgresql_with={'m': 32, 'ef_construction': 200},
                postgresql_ops={'abstract_vector': 'vector_cosine_ops'}
            ),
            Index('abstract_bm25_index', abstract, postgresql_using='bm25')
        )


class ChunkEntity(Base):
    __tablename__ = 'chunk'

    id = Column(UUID, default=uuid4, primary_key=True)  # chunk id
    team_id = Column(UUID)  # 团队id
    kb_id = Column(UUID)  # 知识库id
    doc_id = Column(UUID)  # 片段所属文档id
    doc_name = Column(Text)  # 片段所属文档名称
    text = Column(Text)  # 片段文本内容
    text_ts_vector = Column(TSVECTOR)  # 片段文本词向量
    text_vector = Column(Vector(1024))  # 文本向量
    tokens = Column(BigInteger)  # 片段文本token数
    type = Column(Text, default=ChunkType.TEXT.value)  # 片段类型
    # 前一个chunk的id（假如解析结果为链表，那么这里是前一个节点的id，如果文档解析结果为树，那么这里是父节点的id）
    pre_id_in_parse_topology = Column(UUID)
    # chunk的在解析结果中的拓扑类型（假如解析结果为链表，那么这里为链表头、中间和尾；假如解析结果为树，那么这里为树根、树的中间节点和叶子节点）
    parse_topology_type = Column(
        Text, default=ChunkParseTopology.LISTHEAD.value)
    global_offset = Column(BigInteger)  # chunk在文档中的相对偏移
    local_offset = Column(BigInteger)  # chunk在块中的相对偏移
    enabled = Column(Boolean)  # chunk是否启用
    status = Column(Text, default=ChunkStatus.EXISTED.value)  # chunk状态
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp())
    if config['DATABASE_TYPE'].lower() == 'postgres':
        __table_args__ = (
            Index('text_ts_vector_index', text_ts_vector,
                  postgresql_using='gin'),
            Index(
                'text_vector_index',
                text_vector,
                postgresql_using='hnsw',
                postgresql_with={'m': 32, 'ef_construction': 200},
                postgresql_ops={'text_vector': 'vector_cosine_ops'}
            )
        )
    else:
        __table_args__ = (
            Index('chunk_doc_id_index', doc_id),
            Index('text_ts_vector_index', text_ts_vector,
                  postgresql_using='gin'),
            Index(
                'text_vector_index',
                text_vector,
                postgresql_using='hnsw',
                postgresql_with={'m': 32, 'ef_construction': 200},
                postgresql_ops={'text_vector': 'vector_cosine_ops'}
            ),
            Index('text_bm25_index', text, postgresql_using='bm25')
        )


class ImageEntity(Base):
    __tablename__ = 'image'
    id = Column(UUID, default=uuid4, primary_key=True)  # 图片id
    team_id = Column(UUID)  # 团队id
    doc_id = Column(UUID)  # 图片所属文档id
    chunk_id = Column(UUID)  # 图片所属chunk的id
    extension = Column(Text)  # 图片后缀
    status = Column(Text, default=ImageStatus.EXISTED.value)  # 图片状态
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # 添加索引
    __table_args__ = (
        Index('image_team_id_index', team_id),
        Index('image_doc_id_index', doc_id),
        Index('image_chunk_id_index', chunk_id)
    )


class DataSetEntity(Base):
    __tablename__ = 'dataset'

    id = Column(UUID, default=uuid4, primary_key=True)  # 数据集id
    team_id = Column(UUID)  # 数据集所属团队id
    kb_id = Column(UUID)  # 数据集所属资产id
    author_id = Column(Text)  # 数据的创建者id
    author_name = Column(Text)  # 数据的创建者名称
    llm_id = Column(Text)  # 数据的生成使用的大模型的id
    name = Column(Text, nullable=False)  # 数据集名称
    description = Column(Text)  # 数据集描述
    data_cnt = Column(BigInteger)  # 数据集数据量
    is_data_cleared = Column(Boolean, default=False)  # 数据集是否清洗
    is_chunk_related = Column(Boolean, default=False)  # 数据集是否关联上下文
    is_imported = Column(Boolean, default=False)  # 数据集是否导入
    status = Column(Text, default=DataSetStatus.IDLE)  # 数据集状态
    score = Column(Float, default=-1)  # 数据集得分
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # 添加索引
    __table_args__ = (
        Index('dataset_team_id_index', team_id),
        Index('dataset_kb_id_index', kb_id),
        Index('dataset_name_index', name)
    )


class DataSetDocEntity(Base):
    __tablename__ = 'dataset_doc'

    id = Column(UUID, default=uuid4, primary_key=True)  # 数据集文档id
    dataset_id = Column(UUID)  # 数据集id
    doc_id = Column(UUID)  # 文档id
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # 添加索引
    __table_args__ = (
        Index('dataset_doc_dataset_id_index', dataset_id),
        Index('dataset_doc_doc_id_index', doc_id)
    )


class QAEntity(Base):
    __tablename__ = 'qa'

    id = Column(UUID, default=uuid4, primary_key=True)  # 数据id
    dataset_id = Column(UUID)  # 数据所属数据集id
    doc_id = Column(UUID)  # 数据关联的文档id
    doc_name = Column(Text, default="未知文档")  # 数据关联的文档名称
    question = Column(Text)  # 数据的问题
    answer = Column(Text)  # 数据的答案
    chunk = Column(Text)  # 数据的片段
    chunk_type = Column(Text, default="未知片段类型")  # 数据的片段类型
    status = Column(Text, default=QAStatus.EXISTED.value)  # 数据的状态
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    # 添加索引
    __table_args__ = (
        Index('qa_dataset_id_index', dataset_id),
        Index('qa_doc_id_index', doc_id)
    )


class TestingEntity(Base):
    __tablename__ = 'testing'

    id = Column(UUID, default=uuid4, primary_key=True)  # 测试任务的id
    team_id = Column(UUID)  # 测试任务所属团队id
    kb_id = Column(UUID)  # 测试任务所属资产id
    dataset_id = Column(UUID)  # 测试任务使用数据集的id
    author_id = Column(Text)  # 测试任务的创建者id
    author_name = Column(Text)  # 测试任务的创建者名称
    name = Column(Text)  # 测试任务的名称
    description = Column(Text)  # 测试任务的描述
    llm_id = Column(Text)  # 测试任务的使用的大模型
    search_method = Column(
        Text, default=SearchMethod.KEYWORD_AND_VECTOR.value)  # 测试任务的使用的检索增强模式类型
    top_k = Column(BigInteger, default=5)  # 测试任务的检索增强模式的top_k
    status = Column(Text, default=TestingStatus.IDLE.value)  # 测试任务的状态
    ave_score = Column(Float, default=-1)  # 测试任务的综合得分
    ave_pre = Column(Float, default=-1)  # 测试任务的平均召回率
    ave_rec = Column(Float, default=-1)  # 测试任务的平均精确率
    ave_fai = Column(Float, default=-1)  # 测试任务的平均忠实值
    ave_rel = Column(Float, default=-1)  # 测试任务的平均可解释性
    ave_lcs = Column(Float, default=-1)  # 测试任务的平均最长公共子序列得分
    ave_leve = Column(Float, default=-1)  # 测试任务的平均编辑距离得分
    ave_jac = Column(Float, default=-1)  # 测试任务的平均杰卡德相似系数
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # 添加索引
    __table_args__ = (
        Index('testing_team_id_index', team_id),
        Index('testing_kb_id_index', kb_id),
        Index('testing_dataset_id_index', dataset_id)
    )


class TestCaseEntity(Base):
    __tablename__ = 'testcase'

    id = Column(UUID, default=uuid4, primary_key=True)  # 测试case的id
    testing_id = Column(UUID)  # 测试
    question = Column(Text)  # 数据的问题
    answer = Column(Text)  # 数据的答案
    chunk = Column(Text)  # 数据的片段
    llm_answer = Column(Text)  # 测试答案
    related_chunk = Column(Text)  # 测试关联到的chunk
    doc_name = Column(Text)  # 测试关联的文档名称
    score = Column(Float)  # 测试得分
    pre = Column(Float)  # 召回率
    rec = Column(Float)  # 精确率
    fai = Column(Float)  # 忠实值
    rel = Column(Float)  # 可解释性
    lcs = Column(Float)  # 最长公共子序列得分
    leve = Column(Float)  # 编辑距离得分
    jac = Column(Float)  # 杰卡德相似系数
    status = Column(Text, default=TestCaseStatus.EXISTED.value)  # 测试状态
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # 添加索引
    __table_args__ = (
        Index('testcase_testing_id_index', testing_id),
    )


class TaskEntity(Base):
    __tablename__ = 'task'

    id = Column(UUID, default=uuid4, primary_key=True)
    team_id = Column(UUID)  # 团队id
    user_id = Column(Text)  # 创建者id
    op_id = Column(UUID)  # 任务关联的实体id， 资产或者文档id
    op_name = Column(Text)  # 任务关联的实体名称
    type = Column(Text)  # 任务类型
    retry = Column(BigInteger)  # 重试次数
    status = Column(Text)  # 任务状态
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # 添加索引
    __table_args__ = (
        Index('task_team_id_index', team_id),
        Index('task_user_id_index', user_id),
        Index('task_op_id_index', op_id),
        Index('task_type_index', type),
        Index('task_status_index', status)
    )


class TaskReportEntity(Base):
    __tablename__ = 'task_report'

    id = Column(UUID, default=uuid4, primary_key=True)  # 任务报告的id
    task_id = Column(UUID)  # 任务id
    message = Column(Text)  # 任务报告信息
    current_stage = Column(BigInteger)  # 任务当前阶段
    stage_cnt = Column(BigInteger)  # 任务总的阶段
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # 添加索引
    __table_args__ = (
        Index('task_report_task_id_index', task_id),
    )


class TaskQueueEntity(Base):
    __tablename__ = 'task_queue'

    id = Column(UUID, default=uuid4, primary_key=True)  # 任务ID
    status = Column(Text)  # 任务状态
    created_time = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.current_timestamp()
    )
    # 添加索引以提高查询性能
    __table_args__ = (
        Index('idx_task_queue_created_time', 'created_time'),
    )


class DataBase:

    # 对密码进行 URL 编码
    password = config['DATABASE_PASSWORD']
    encoded_password = urllib.parse.quote_plus(password)

    if config['DATABASE_TYPE'].lower() == 'opengauss':
        database_url = f"opengauss+asyncpg://{config['DATABASE_USER']}:{encoded_password}@{config['DATABASE_HOST']}:{config['DATABASE_PORT']}/{config['DATABASE_DB']}"
    else:
        database_url = f"postgresql+asyncpg://{config['DATABASE_USER']}:{encoded_password}@{config['DATABASE_HOST']}:{config['DATABASE_PORT']}/{config['DATABASE_DB']}"
    import os
    pool_size = os.cpu_count()
    if pool_size is None:
        pool_size = 5
    logging.error(f"Database pool size set to: {pool_size}")
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_recycle=300,
        pool_pre_ping=True,
        pool_size=pool_size
    )
    init_all_table_flag = False

    @classmethod
    async def init_all_table(cls):
        if config['DATABASE_TYPE'] == 'opengauss':
            from sqlalchemy import event
            from opengauss_sqlalchemy.register_async import register_vector

            @event.listens_for(DataBase.engine.sync_engine, "connect")
            def connect(dbapi_connection, connection_record):
                dbapi_connection.run_async(register_vector)
        async with DataBase.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @classmethod
    async def get_session(cls):
        if DataBase.init_all_table_flag is False:
            await DataBase.init_all_table()
            DataBase.init_all_table_flag = True
        connection = async_sessionmaker(
            DataBase.engine, expire_on_commit=False)()
        return cls._ConnectionManager(connection)

    class _ConnectionManager:
        def __init__(self, connection):
            self.connection = connection

        async def __aenter__(self):
            return self.connection

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.connection.close()
