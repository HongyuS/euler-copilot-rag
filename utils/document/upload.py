import argparse
import os
import requests
import uuid
from pathlib import Path

def upload_documents(api_url, token, kb_id, doc_dir, batch_size=100):
    """
    批量上传文档到指定知识库
    
    Args:
        api_url: API接口地址
        token: 认证令牌
        kb_id: 知识库ID
        doc_dir: 文档所在目录
        batch_size: 每次上传的文档数量
    """
    # 检查文档目录是否存在
    if not os.path.isdir(doc_dir):
        print(f"错误：文档目录 {doc_dir} 不存在")
        return
    
    # 获取目录下的所有文件
    doc_files = [f for f in os.listdir(doc_dir) 
                if os.path.isfile(os.path.join(doc_dir, f))]
    
    if not doc_files:
        print(f"警告：文档目录 {doc_dir} 中没有文件")
        return
    
    print(f"发现 {len(doc_files)} 个文件，将以每次 {batch_size} 个的批次上传")
    
    # 按批次处理文件
    total_uploaded = 0
    headers = {"Authorization": f"Bearer {token}"}
    
    for i in range(0, len(doc_files), batch_size):
        batch = doc_files[i:i+batch_size]
        print(f"\n正在上传第 {i//batch_size + 1} 批，共 {len(batch)} 个文件...")
        
        # 准备文件数据
        files = []
        for filename in batch:
            file_path = os.path.join(doc_dir, filename)
            try:
                files.append(
                    ('docs', (filename, open(file_path, 'rb'), None))
                )
            except Exception as e:
                print(f"无法打开文件 {filename}：{str(e)}，已跳过")
        
        if not files:
            print("本批次没有可上传的文件，跳过")
            continue
        
        # 发送请求
        try:
            response = requests.post(
                f"{api_url}/doc",
                headers=headers,
                params={"kbId": kb_id},
                files=files
            )
            
            # 关闭所有文件
            for _, (_, file_obj, _) in files:
                file_obj.close()
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200 and "result" in result:
                    print(f"成功上传 {len(result['result'])} 个文件，文档ID：")
                    print(result["result"])
                    total_uploaded += len(result["result"])
                else:
                    print(f"上传失败：{result.get('message', '未知错误')}")
            else:
                print(f"请求失败，状态码：{response.status_code}")
                print(f"响应内容：{response.text}")
                
        except Exception as e:
            print(f"上传过程出错：{str(e)}")
    
    print(f"\n上传完成，共成功上传 {total_uploaded} 个文件")

def main():
    parser = argparse.ArgumentParser(description='批量上传文档到知识库')
    parser.add_argument('doc_dir', help='文档所在的目录')
    parser.add_argument('kb_id', help='知识库ID (kb_id)')
    parser.add_argument('--batch-size', type=int, default=100, 
                      help='每次上传的文档数量，默认100')
    parser.add_argument('--api-url', required=True, 
                      help='API接口基础地址 (例如: http://localhost:9988)')
    parser.add_argument('--token', required=True, 
                      help='认证令牌 (Bearer token)')
    
    args = parser.parse_args()
    
    # 验证kb_id格式
    try:
        uuid.UUID(args.kb_id)
    except ValueError:
        print(f"错误：{args.kb_id} 不是有效的UUID格式")
        return
    
    upload_documents(
        api_url=args.api_url,
        token=args.token,
        kb_id=args.kb_id,
        doc_dir=args.doc_dir,
        batch_size=args.batch_size
    )

if __name__ == '__main__':
    main()