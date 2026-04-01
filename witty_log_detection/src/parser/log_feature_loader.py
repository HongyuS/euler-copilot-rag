import os
import yaml
from src.enum.log import LogTypeEnum
from src.config.config import Config


class BaseLogFeature:
    """基础日志特征类"""
    def __init__(self, config):
        self.keywords_regex_and_scores = config.get('keywords_regex_and_scores', {})
        self.mandatory = config.get('mandatory', {})
        self.capture_patterns = config.get('capture_patterns', {})


class LogFeatureLoader:
    """日志特征加载器"""
    
    @staticmethod
    def load_from_directory(directory: str):
        """
        从指定目录加载日志特征配置
        
        Args:
            directory: 配置文件目录路径
            
        Returns:
            日志类型到特征对象的映射
        """
        log_feature_mapping = {}
        
        # 获取配置
        config = Config().get_config()
        log_types_to_load = config.log_parse_config.log_types_to_load
        
        # 遍历目录中的所有YAML文件
        for filename in os.listdir(directory):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                # 提取日志类型名称（去掉后缀并转换为大写）
                log_type_name = os.path.splitext(filename)[0].replace('_log_feature', '').upper()
                log_type = getattr(LogTypeEnum, log_type_name, None)
                
                if log_type:
                    # 检查是否需要加载该类型的配置
                    if not log_types_to_load or log_type in log_types_to_load:
                        filepath = os.path.join(directory, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                file_config = yaml.safe_load(f)
                                if file_config:
                                    log_feature_mapping[log_type] = BaseLogFeature(file_config)
                        except Exception:
                            pass
        

        
        return log_feature_mapping
    
    @staticmethod
    def load_from_file(filepath: str):
        """
        从单个文件加载日志特征配置
        
        Args:
            filepath: 文件路径
            
        Returns:
            BaseLogFeature对象或None
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return BaseLogFeature(config) if config else None
        except Exception:
            return None


# 动态加载日志特征配置
config_directory = os.path.join(os.path.dirname(__file__), 'log_features')
log_feature_class_mapping = LogFeatureLoader.load_from_directory(config_directory)