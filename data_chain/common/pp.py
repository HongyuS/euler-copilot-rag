from data_chain.parser.tools.token_tool import TokenTool
import json
import asyncio
from data_chain.config.config import config
from data_chain.llm.llm import LLM
import yaml


def load_yaml_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # 使用yaml.safe_load()方法加载YAML文件内容
            data = yaml.safe_load(file)
            return data
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    except yaml.YAMLError as e:
        print(f"解析YAML文件时出错: {e}")


def save_yaml_file(yaml_data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(yaml_data, file, allow_unicode=True, default_flow_style=False)


# 示例：加载YAML文件
file_path = './data_chain/common/prompt.yaml'
yaml_data = load_yaml_file(file_path)
print(yaml_data)
# print(config.__dict__)
# llm = LLM(
#     model_name=config['MODEL_NAME'],
#     openai_api_base=config['OPENAI_API_BASE'],
#     openai_api_key=config['OPENAI_API_KEY'],
#     request_timeout=config['REQUEST_TIMEOUT'],
#     max_tokens=config['MAX_TOKENS'],
#     temperature=config['TEMPERATURE'],
# )
# print(prompt_dict)
# for key in prompt_dict:
#     prompt = prompt_dict[key]['zh']
#     systemcall = f"""
#     你是一个翻译专家, 你需要将用户输入的中文内容翻译成地道的英文, 只需要返回翻译后的英文内容, 不需要任何多余的解释和说明.
#     你需要严格遵守以下规则:
#     1. 你只能翻译用户输入的内容, 不能添加任何额外的信息.
#     2. 你需要确保翻译后的内容符合英文的语法和表达习惯.
#     3. 你需要确保翻译后的内容准确传达用户输入的中文内容的意思.

#     <content></content>标签中的内容是用户输入的中文内容, 你需要将这些内容翻译成英文.
#     <content>{prompt}</content>
#     """
#     user_call = f"请将上面的内容翻译为英文"
#     result = asyncio.run(llm.nostream([], systemcall, user_call))
#     print(result)
#     prompt_dict[key]['en'] = result
# print(prompt_dict)
