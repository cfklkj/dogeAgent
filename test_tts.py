"""
TTS 功能测试脚本
测试文字转语音功能是否正常工作
"""
import os
import sys
import tempfile
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def test_tts_basic():
    """测试基本 TTS 功能"""
    print("=" * 50)
    print("TTS 功能测试")
    print("=" * 50)
    
    try:
        from tools.tts_tool import text_to_speech
        
        # 测试文本
        test_texts = [
            "你好，我是你的柴犬助手 Doge!",
            "今天天气真好!",
            "汪汪汪!"
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n[测试 {i}/3] 文本：{text}")
            
            # 生成临时文件
            temp_dir = tempfile.gettempdir()
            output_file = os.path.join(temp_dir, f"doge_test_{i}.mp3")
            
            try:
                # 调用 TTS
                print(f"  生成文件：{output_file}")
                result = text_to_speech(text, output_file)
                
                # 验证结果
                if os.path.exists(result):
                    file_size = os.path.getsize(result)
                    print(f"  [成功] 文件大小：{file_size} 字节")
                else:
                    print(f"  [失败] 文件不存在")
                    
            except Exception as e:
                print(f"  [错误] {e}")
        
        print("\n" + "=" * 50)
        print("测试完成!")
        print("=" * 50)
        
    except ImportError as e:
        print(f"导入失败：{e}")
        print("请确保已安装 edge-tts: pip install edge-tts")
    except Exception as e:
        print(f"测试失败：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tts_basic()
