from pydub import AudioSegment
import argparse
import os
import glob

def process_audio(folder_path, repeat=None, add=False):
    # 获取所有wav文件
    audio_files = sorted(glob.glob(os.path.join(folder_path, '*.wav')))
    
    if not audio_files:
        raise ValueError("未找到.wav音频文件")

    # 处理重复模式
    if repeat is not None:
        if repeat < 1:
            raise ValueError("重复次数必须大于0")
            
        combined = AudioSegment.empty()
        filename_parts = []
        
        for file in audio_files:
            audio = AudioSegment.from_wav(file)
            # 重复音频
            combined += audio * repeat
            # 处理文件名
            # 修改后的文件名处理逻辑（重复模式）
            base = os.path.basename(file).rsplit('.', 1)[0]
            filename_parts.append(base * repeat)  # 直接重复文件名
            

            filename_parts.append(os.path.basename(file).rsplit('.', 1)[0])
            
            # 最终输出文件名生成方式
            output_name = ''.join(filename_parts) + ".wav"

        output_name = "".join(filename_parts) + ".wav"
        combined.export(os.path.join(folder_path, output_name), format="wav")

    # 处理合并模式
    elif add:
        combined = AudioSegment.empty()
        filename_parts = []
        
        for file in audio_files:
            audio = AudioSegment.from_wav(file)
            combined += audio
            filename_parts.append(os.path.basename(file).rsplit('.', 1)[0])

        output_name = ''.join(filename_parts) + ".wav"
        combined.export(os.path.join(folder_path, output_name), format="wav")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='音频文件处理工具')
    parser.add_argument('--route', required=True, help='音频文件夹绝对路径')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--repeat', type=int, help='重复次数')
    group.add_argument('--add', action='store_true', help='合并全部文件')
    
    args = parser.parse_args()
    
    try:
        process_audio(
            folder_path=args.route,
            repeat=args.repeat,
            add=args.add
        )
        print(f"处理完成，输出文件保存在 {args.route}")
    except Exception as e:
        print(f"错误发生: {str(e)}")