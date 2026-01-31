import uuid
from data_chain.entities.enum import DeafaultRole
from data_chain.entities.enum import LanguageType
DEFAULT_DOC_TYPE_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")
DEFAULT_KNOWLEDGE_BASE_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")
DEFAULt_DOC_TYPE_NAME = "default"
actions = [
    {'type': {LanguageType.CHINESE: '团队', LanguageType.ENGLISH: 'team'},
     'name': {LanguageType.CHINESE: '获取团队用户列表', LanguageType.ENGLISH: 'Get team user list'},
     'action': 'POST /team/usr'},
    {'type': {LanguageType.CHINESE: '团队', LanguageType.ENGLISH: 'team'},
     'name': {LanguageType.CHINESE: '获取团队消息列表', LanguageType.ENGLISH: 'Get team message list'},
     'action': 'POST /team/msg'},
    {'type': {LanguageType.CHINESE: '团队', LanguageType.ENGLISH: 'team'},
     'name': {LanguageType.CHINESE: '发送团队邀请', LanguageType.ENGLISH: 'Send team invitation'},
     'action': 'POST /team/invitation'},
    {"type": {LanguageType.CHINESE: '团队', LanguageType.ENGLISH: 'team'},
     "name": {LanguageType.CHINESE: '获取用户消息列表', LanguageType.ENGLISH: 'Get user message list'},
     "action": "POST /usr_msg/list"},
    {'type': {LanguageType.CHINESE: '团队', LanguageType.ENGLISH: 'team'},
     'name': {LanguageType.CHINESE: '更新用户消息', LanguageType.ENGLISH: 'Update User message'},
     'action': 'PUT /usr_msg'},
    {'type': {LanguageType.CHINESE: '团队', LanguageType.ENGLISH: 'team'},
     'name': {LanguageType.CHINESE: '更新团队信息', LanguageType.ENGLISH: 'Update team information'},
     'action': 'PUT /team'},
    {'type': {LanguageType.CHINESE: '团队', LanguageType.ENGLISH: 'team'},
     'name': {LanguageType.CHINESE: '更新团队用户角色', LanguageType.ENGLISH: 'Update team user role'},
     'action': 'PUT /team/usr'},
    {'type': {LanguageType.CHINESE: '团队', LanguageType.ENGLISH: 'team'},
     'name': {LanguageType.CHINESE: '转让团队所有权', LanguageType.ENGLISH: 'Transfer team ownership'},
     'action': 'PUT /team/author'},
    {'type': {LanguageType.CHINESE: '团队', LanguageType.ENGLISH: 'team'},
     'name': {LanguageType.CHINESE: '解散团队', LanguageType.ENGLISH: 'Disband team'},
     'action': 'DELETE /team'},
    {'type': {LanguageType.CHINESE: '团队', LanguageType.ENGLISH: 'team'},
     'name': {LanguageType.CHINESE: '移除团队用户', LanguageType.ENGLISH: 'Remove team user'},
     'action': 'DELETE /team/usr'},
    {'type': {LanguageType.CHINESE: '角色', LanguageType.ENGLISH: 'role'},
     'name': {LanguageType.CHINESE: '获取角色操作列表', LanguageType.ENGLISH: 'Get role operation list'},
     'action': 'GET /role/action'},
    {'type': {LanguageType.CHINESE: '角色', LanguageType.ENGLISH: 'role'},
     'name': {LanguageType.CHINESE: '获取角色列表', LanguageType.ENGLISH: 'Get role list'},
     'action': 'POST /role/list'},
    {'type': {LanguageType.CHINESE: '角色', LanguageType.ENGLISH: 'role'},
     'name': {LanguageType.CHINESE: '创建角色', LanguageType.ENGLISH: 'Create role'},
     'action': 'POST /role'},
    {'type': {LanguageType.CHINESE: '角色', LanguageType.ENGLISH: 'role'},
     'name': {LanguageType.CHINESE: '更新角色信息', LanguageType.ENGLISH: 'Update role information'},
     'action': 'PUT /role'},
    {'type': {LanguageType.CHINESE: '角色', LanguageType.ENGLISH: 'role'},
     'name': {LanguageType.CHINESE: '删除角色', LanguageType.ENGLISH: 'Delete role'},
     'action': 'DELETE /role'},
    {'type': {LanguageType.CHINESE: '知识库', LanguageType.ENGLISH: 'knowledge_base'},
     'name': {LanguageType.CHINESE: '获取团队下的知识库列表', LanguageType.ENGLISH: 'Get knowledge base list under team'},
     'action': 'POST /kb/team'},
    {'type': {LanguageType.CHINESE: '知识库', LanguageType.ENGLISH: 'knowledge_base'},
     'name': {LanguageType.CHINESE: '获取知识库文档类型', LanguageType.ENGLISH: 'Get knowledge base document types'},
     'action': 'GET /kb/doc_type'},
    {'type': {LanguageType.CHINESE: '知识库', LanguageType.ENGLISH: 'knowledge_base'},
     'name': {LanguageType.CHINESE: '下载知识库文件', LanguageType.ENGLISH: 'Download knowledge base file'},
     'action': 'GET /kb/download'},
    {'type': {LanguageType.CHINESE: '知识库', LanguageType.ENGLISH: 'knowledge_base'},
     'name': {LanguageType.CHINESE: '创建知识库', LanguageType.ENGLISH: 'Create knowledge base'},
     'action': 'POST /kb'},
    {'type': {LanguageType.CHINESE: '知识库', LanguageType.ENGLISH: 'knowledge_base'},
     'name': {LanguageType.CHINESE: '导入知识库', LanguageType.ENGLISH: 'Import knowledge base'},
     'action': 'POST /kb/import'},
    {'type': {LanguageType.CHINESE: '知识库', LanguageType.ENGLISH: 'knowledge_base'},
     'name': {LanguageType.CHINESE: '导出知识库', LanguageType.ENGLISH: 'Export knowledge base'},
     'action': 'POST /kb/export'},
    {'type': {LanguageType.CHINESE: '知识库', LanguageType.ENGLISH: 'knowledge_base'},
     'name': {LanguageType.CHINESE: '更新知识库信息', LanguageType.ENGLISH: 'Update knowledge base information'},
     'action': 'PUT /kb'},
    {'type': {LanguageType.CHINESE: '知识库', LanguageType.ENGLISH: 'knowledge_base'},
     'name': {LanguageType.CHINESE: '删除知识库', LanguageType.ENGLISH: 'Delete knowledge base'},
     'action': 'DELETE /kb'},
    {'type': {LanguageType.CHINESE: '文档', LanguageType.ENGLISH: 'document'},
     'name': {LanguageType.CHINESE: '获取文档列表', LanguageType.ENGLISH: 'Get document list'},
     'action': 'POST /doc/list'},
    {'type': {LanguageType.CHINESE: '文档', LanguageType.ENGLISH: 'document'},
     'name': {LanguageType.CHINESE: '下载文档', LanguageType.ENGLISH: 'Download document'},
     'action': 'GET /doc/download'},
    {'type': {LanguageType.CHINESE: '文档', LanguageType.ENGLISH: 'document'},
     'name': {LanguageType.CHINESE: '获取文档报告', LanguageType.ENGLISH: 'Get document report'},
     'action': 'GET /doc/report'},
    {'type': {LanguageType.CHINESE: '文档', LanguageType.ENGLISH: 'document'},
     'name': {LanguageType.CHINESE: '下载文档报告', LanguageType.ENGLISH: 'Download document report'},
     'action': 'GET /doc/report/download'},
    {'type': {LanguageType.CHINESE: '文档', LanguageType.ENGLISH: 'document'},
     'name': {LanguageType.CHINESE: '创建文档', LanguageType.ENGLISH: 'Create document'},
     'action': 'POST /doc'},
    {'type': {LanguageType.CHINESE: '文档', LanguageType.ENGLISH: 'document'},
     'name': {LanguageType.CHINESE: '解析文档', LanguageType.ENGLISH: 'Parse document'},
     'action': 'POST /doc/parse'},
    {'type': {LanguageType.CHINESE: '文档', LanguageType.ENGLISH: 'document'},
     'name': {LanguageType.CHINESE: '更新文档信息', LanguageType.ENGLISH: 'Update document information'},
     'action': 'PUT /doc'},
    {'type': {LanguageType.CHINESE: '文档', LanguageType.ENGLISH: 'document'},
     'name': {LanguageType.CHINESE: '删除文档', LanguageType.ENGLISH: 'Delete document'},
     'action': 'DELETE /doc'},
    {'type': {LanguageType.CHINESE: '文档片段', LanguageType.ENGLISH: 'chunk'},
     'name': {LanguageType.CHINESE: '获取文档解析结果列表', LanguageType.ENGLISH: 'Get document parsing result list'},
     'action': 'POST /chunk/list'},
    {'type': {LanguageType.CHINESE: '文档片段', LanguageType.ENGLISH: 'chunk'},
     'name': {LanguageType.CHINESE: '检索文档解析结果', LanguageType.ENGLISH: 'Retrieve document parsing results'},
     'action': 'POST /chunk/search'},
    {'type': {LanguageType.CHINESE: '文档片段', LanguageType.ENGLISH: 'chunk'},
     'name': {LanguageType.CHINESE: '更新文档解析结果', LanguageType.ENGLISH: 'Update document parsing results'},
     'action': 'PUT /chunk'},
    {'type': {LanguageType.CHINESE: '文档片段', LanguageType.ENGLISH: 'chunk'},
     'name': {LanguageType.CHINESE: '启用/禁用文档片段', LanguageType.ENGLISH: 'Enable/Disable document chunk'},
     'action': 'PUT /chunk/switch'},
    {'type': {LanguageType.CHINESE: '数据集', LanguageType.ENGLISH: 'dataset'},
     'name': {LanguageType.CHINESE: '获取数据集列表', LanguageType.ENGLISH: 'Get dataset list'},
     'action': 'POST /dataset/list'},
    {'type': {LanguageType.CHINESE: '数据集', LanguageType.ENGLISH: 'dataset'},
     'name': {LanguageType.CHINESE: '获取测试数据列表', LanguageType.ENGLISH: 'Get test data list'},
     'action': 'POST /dataset/data'},
    {'type': {LanguageType.CHINESE: '数据集', LanguageType.ENGLISH: 'dataset'},
     'name': {LanguageType.CHINESE: '检查测试数据下是否有测试任务', LanguageType.ENGLISH: 'Check if there are test tasks under test data'},
     'action': 'GET /dataset/testing/exist'},
    {'type': {LanguageType.CHINESE: '数据集', LanguageType.ENGLISH: 'dataset'},
     'name': {LanguageType.CHINESE: '下载数据集', LanguageType.ENGLISH: 'Download dataset'},
     'action': 'GET /dataset/download'},
    {'type': {LanguageType.CHINESE: '数据集', LanguageType.ENGLISH: 'dataset'},
     'name': {LanguageType.CHINESE: '创建新数据集', LanguageType.ENGLISH: 'Create new dataset'},
     'action': 'POST /dataset'},
    {'type': {LanguageType.CHINESE: '数据集', LanguageType.ENGLISH: 'dataset'},
     'name': {LanguageType.CHINESE: '导入数据集', LanguageType.ENGLISH: 'Import dataset'},
     'action': 'POST /dataset/import'},
    {'type': {LanguageType.CHINESE: '数据集', LanguageType.ENGLISH: 'dataset'},
     'name': {LanguageType.CHINESE: '导出数据集', LanguageType.ENGLISH: 'Export dataset'},
     'action': 'POST /dataset/export'},
    {'type': {LanguageType.CHINESE: '数据集', LanguageType.ENGLISH: 'dataset'},
     'name': {LanguageType.CHINESE: '生成数据集', LanguageType.ENGLISH: 'Generate dataset'},
     'action': 'POST /dataset/generate'},
    {'type': {LanguageType.CHINESE: '数据集', LanguageType.ENGLISH: 'dataset'},
     'name': {LanguageType.CHINESE: '修改数据集信息', LanguageType.ENGLISH: 'Modify dataset information'},
     'action': 'PUT /dataset'},
    {'type': {LanguageType.CHINESE: '数据集', LanguageType.ENGLISH: 'dataset'},
     'name': {LanguageType.CHINESE: '修改测试用例', LanguageType.ENGLISH: 'Modify test case'},
     'action': 'PUT /dataset/data'},
    {'type': {LanguageType.CHINESE: '数据集', LanguageType.ENGLISH: 'dataset'},
     'name': {LanguageType.CHINESE: '删除数据集', LanguageType.ENGLISH: 'Delete dataset'},
     'action': 'DELETE /dataset'},
    {'type': {LanguageType.CHINESE: '数据集', LanguageType.ENGLISH: 'dataset'},
     'name': {LanguageType.CHINESE: '删除测试用例', LanguageType.ENGLISH: 'Delete test case'},
     'action': 'DELETE /dataset/data'},
    {'type': {LanguageType.CHINESE: '测试', LanguageType.ENGLISH: 'testing'},
     'name': {LanguageType.CHINESE: '获取测试列表', LanguageType.ENGLISH: 'Get test list'},
     'action': 'POST /testing/list'},
    {'type': {LanguageType.CHINESE: '测试', LanguageType.ENGLISH: 'testing'},
     'name': {LanguageType.CHINESE: '获取测试用例列表', LanguageType.ENGLISH: 'Get test case list'},
     'action': 'POST /testing/testcase'},
    {'type': {LanguageType.CHINESE: '测试', LanguageType.ENGLISH: 'testing'},
     'name': {LanguageType.CHINESE: '下载测试结果', LanguageType.ENGLISH: 'Download test results'},
     'action': 'GET /testing/download'},
    {'type': {LanguageType.CHINESE: '测试', LanguageType.ENGLISH: 'testing'},
     'name': {LanguageType.CHINESE: '创建测试', LanguageType.ENGLISH: 'Create test'},
     'action': 'POST /testing'},
    {'type': {LanguageType.CHINESE: '测试', LanguageType.ENGLISH: 'testing'},
     'name': {LanguageType.CHINESE: '运行测试', LanguageType.ENGLISH: 'Run test'},
     'action': 'POST /testing/run'},
    {'type': {LanguageType.CHINESE: '测试', LanguageType.ENGLISH: 'testing'},
     'name': {LanguageType.CHINESE: '更新测试信息', LanguageType.ENGLISH: 'Update test information'},
     'action': 'PUT /testing'},
    {'type': {LanguageType.CHINESE: '测试', LanguageType.ENGLISH: 'testing'},
     'name': {LanguageType.CHINESE: '删除测试', LanguageType.ENGLISH: 'Delete test'},
     'action': 'DELETE /testing'},
    {'type': {LanguageType.CHINESE: '任务', LanguageType.ENGLISH: 'task'},
     'name': {LanguageType.CHINESE: '获取任务列表', LanguageType.ENGLISH: 'Get task list'},
     'action': 'POST /task'},
    {'type': {LanguageType.CHINESE: '任务', LanguageType.ENGLISH: 'task'},
     'name': {LanguageType.CHINESE: '获取任务报告', LanguageType.ENGLISH: 'Get task report'},
     'action': 'GET /task/report'},
    {'type': {LanguageType.CHINESE: '任务', LanguageType.ENGLISH: 'task'},
     'name': {LanguageType.CHINESE: '删除单个任务', LanguageType.ENGLISH: 'Delete single task'},
     'action': 'DELETE /task/one'},
    {'type': {LanguageType.CHINESE: '任务', LanguageType.ENGLISH: 'task'},
     'name': {LanguageType.CHINESE: '删除所有任务', LanguageType.ENGLISH: 'Delete all tasks'},
     'action': 'DELETE /task/all'}
]
default_roles = [{
    'name': DeafaultRole.OWENER.value,
    'is_unique': True,
    'actions': [{
        'action': 'POST /team/usr'
    }, {
        'action': 'POST /team/msg'
    }, {
        'action': 'POST /team/invitation'
    }, {
        'action': 'POST /usr_msg/list'
    }, {
        'action': 'PUT /usr_msg'
    }, {
        'action': 'PUT /team'
    }, {
        'action': 'PUT /team/usr'
    }, {
        'action': 'PUT /team/author'
    }, {
        'action': 'DELETE /team'
    }, {
        'action': 'DELETE /team/usr'
    }, {
        'action': 'POST /kb/team'
    }, {
        'action': 'GET /kb/doc_type'
    }, {
        'action': 'GET /kb/download'
    }, {
        'action': 'POST /kb'
    }, {
        'action': 'POST /kb/import'
    }, {
        'action': 'POST /kb/export'
    }, {
        'action': 'PUT /kb'
    }, {
        'action': 'DELETE /kb'
    }, {
        'action': 'POST /chunk/list'
    }, {
        'action': 'POST /chunk/search'
    }, {
        'action': 'PUT /chunk'
    }, {
        'action': 'PUT /chunk/switch'
    }, {
        'action': 'POST /doc/list'
    }, {
        'action': 'GET /doc/download'
    }, {
        'action': 'GET /doc/report'
    }, {
        'action': 'GET /doc/report/download'
    }, {
        'action': 'POST /doc'
    }, {
        'action': 'POST /doc/parse'
    }, {
        'action': 'PUT /doc'
    }, {
        'action': 'DELETE /doc'
    }, {
        'action': 'POST /dataset/list'
    }, {
        'action': 'POST /dataset/data'
    }, {
        'action': 'GET /dataset/testing/exist'
    }, {
        'action': 'GET /dataset/download'
    }, {
        'action': 'POST /dataset'
    }, {
        'action': 'POST /dataset/import'
    }, {
        'action': 'POST /dataset/export'
    }, {
        'action': 'POST /dataset/generate'
    }, {
        'action': 'PUT /dataset'
    }, {
        'action': 'PUT /dataset/data'
    }, {
        'action': 'DELETE /dataset'
    }, {
        'action': 'DELETE /dataset/data'
    }, {
        'action': 'POST /testing/list'
    }, {
        'action': 'POST /testing/testcase'
    }, {
        'action': 'GET /testing/download'
    }, {
        'action': 'POST /testing'
    }, {
        'action': 'POST /testing/run'
    }, {
        'action': 'PUT /testing'
    }, {
        'action': 'DELETE /testing'
    }, {
        'action': 'GET /role/action'
    }, {
        'action': 'POST /role/list'
    }, {
        'action': 'POST /role'
    }, {
        'action': 'PUT /role'
    }, {
        'action': 'DELETE /role'
    }, {
        'action': 'POST /task'
    }, {
        'action': 'GET /task/report'
    }, {
        'action': 'DELETE /task/one'
    }, {
        'action': 'DELETE /task/all'
    }],
    'editable': False
}, {
    'name': DeafaultRole.ADMINISTRATOR.value,
    'is_unique': False,
    'actions': [{
        'action': 'POST /team/usr'
    }, {
        'action': 'POST /team/msg'
    }, {
        'action': 'POST /team/invitation'
    }, {
        'action': 'POST /usr_msg/list'
    }, {
        'action': 'PUT /usr_msg'
    }, {
        'action': 'PUT /team/usr'
    }, {
        'action': 'DELETE /team/usr'
    }, {
        'action': 'POST /kb/team'
    }, {
        'action': 'GET /kb/doc_type'
    }, {
        'action': 'GET /kb/download'
    }, {
        'action': 'POST /kb'
    }, {
        'action': 'POST /kb/import'
    }, {
        'action': 'POST /kb/export'
    }, {
        'action': 'PUT /kb'
    }, {
        'action': 'DELETE /kb'
    }, {
        'action': 'POST /chunk/list'
    }, {
        'action': 'POST /chunk/search'
    }, {
        'action': 'PUT /chunk'
    }, {
        'action': 'PUT /chunk/switch'
    }, {
        'action': 'POST /doc/list'
    }, {
        'action': 'GET /doc/download'
    }, {
        'action': 'GET /doc/report'
    }, {
        'action': 'GET /doc/report/download'
    }, {
        'action': 'POST /doc'
    }, {
        'action': 'POST /doc/parse'
    }, {
        'action': 'PUT /doc'
    }, {
        'action': 'DELETE /doc'
    }, {
        'action': 'POST /dataset/list'
    }, {
        'action': 'POST /dataset/data'
    }, {
        'action': 'GET /dataset/testing/exist'
    }, {
        'action': 'GET /dataset/download'
    }, {
        'action': 'POST /dataset'
    }, {
        'action': 'POST /dataset/import'
    }, {
        'action': 'POST /dataset/export'
    }, {
        'action': 'POST /dataset/generate'
    }, {
        'action': 'PUT /dataset'
    }, {
        'action': 'PUT /dataset/data'
    }, {
        'action': 'DELETE /dataset'
    }, {
        'action': 'DELETE /dataset/data'
    }, {
        'action': 'POST /testing/list'
    }, {
        'action': 'POST /testing/testcase'
    }, {
        'action': 'GET /testing/download'
    }, {
        'action': 'POST /testing'
    }, {
        'action': 'POST /testing/run'
    }, {
        'action': 'PUT /testing'
    }, {
        'action': 'DELETE /testing'
    }, {
        'action': 'GET /role/action'
    }, {
        'action': 'POST /role/list'
    }, {
        'action': 'POST /task'
    }, {
        'action': 'GET /task/report'
    }, {
        'action': 'DELETE /task/one'
    }, {
        'action': 'DELETE /task/all'
    }],
    'editable': False
}, {
    'name': DeafaultRole.MEMBER.value,
    'is_unique': False,
    'actions': [{
        'action': 'POST /team/usr'
    }, {
        'action': 'POST /team/msg'
    }, {
        'action': 'POST /kb/team'
    }, {
        'action': 'GET /kb/doc_type'
    }, {
        'action': 'POST /chunk/list'
    }, {
        'action': 'POST /chunk/search'
    }, {
        'action': 'POST /doc/list'
    }, {
        'action': 'GET /doc/download'
    }, {
        'action': 'POST /dataset/list'
    }, {
        'action': 'POST /dataset/data'
    }, {
        'action': 'POST /testing/list'
    }, {
        'action': 'POST /testing/testcase'
    }, {
        'action': 'GET /role/action'
    }, {
        'action': 'POST /role/list'
    }],
    'editable': False
}]

DOC_PATH_IN_MINIO = "witchaind-doc"
REPORT_PATH_IN_MINIO = "witchaind-report"
IMAGE_PATH_IN_MINIO = "witchaind-image"
EXPORT_KB_PATH_IN_MINIO = "witchaind-kb-export"
IMPORT_KB_PATH_IN_MINIO = "witchaind-kb-import"
EXPORT_DATASET_PATH_IN_MINIO = "witchaind-dataset-export"
IMPORT_DATASET_PATH_IN_MINIO = "witchaind-dataset-import"
TESTING_REPORT_PATH_IN_MINIO = "witchaind-testing-report"

DOC_PATH_IN_OS = "./witchaind-doc"
EXPORT_KB_PATH_IN_OS = "./witchaind-kb-export"
IMPORT_KB_PATH_IN_OS = "./witchaind-kb-import"
EXPORT_DATASET_PATH_IN_OS = "./witchaind-dataset-export"
IMPORT_DATASET_PATH_IN_OS = "./witchaind-dataset-import"
TESTING_REPORT_PATH_IN_OS = "./witchaind-testing-report"
