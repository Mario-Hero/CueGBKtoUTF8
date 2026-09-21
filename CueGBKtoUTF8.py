#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量把指定文件夹下（含所有子目录）的 .cue 文件从 GBK 转为 UTF-8。
- 已经是 UTF-8 的文件自动跳过。
- 删除文件末尾的解码错误行。

用法：
    python convert_cue.py <文件夹路径>
    或直接把文件放到指定目录，双击运行。
    # 不给出文件夹路径则默认为当前文件夹
"""

import sys
import os
from pathlib import Path

UTF8_BOM = b"\xef\xbb\xbf"

def main():
    if len(sys.argv) < 2:
        root_path = './'
    elif len(sys.argv) > 2:
        print("用法: python convert_cue.py <文件夹路径>", file=sys.stderr)
        return 1
    else:
        root_path = sys.argv[1]
    root = Path(root_path).expanduser()
    if not root.is_dir():
        print(f"错误: {root} 不是有效文件夹", file=sys.stderr)
        return 1

    files = sorted(
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() == ".cue"
    )
    if not files:
        print(f"在 {root} 下未找到 .cue 文件")
        return 0

    n_conv = n_skip = n_err = 0
    for f in files:
        try:
            raw = f.read_bytes()
        except OSError as e:
            n_err += 1
            print(f"[错误] {f}  读取失败: {e}")
            continue

        if not raw.strip():
            n_skip += 1
            print(f"[跳过] {f}  (空文件)")
            continue

        if raw.startswith(UTF8_BOM):
            n_skip += 1
            print(f"[跳过] {f}  (已是 UTF-8)")
            continue

        # 先判断是不是已经是 UTF-8
        try:
            raw.decode("utf-8")
            n_skip += 1
            print(f"[跳过] {f}  (已是 UTF-8)")
            continue
        except UnicodeDecodeError:
            pass

        # 用 GBK 解码（忽略末尾几行的解码错误）
        text = ''
        for line in raw.splitlines():
            try:
                text += line.decode("gbk", errors="strict") + '\n'
            except UnicodeDecodeError:
                break
        text = text.strip() # 去除末尾换行符
        try:
            f.write_bytes(text.encode("utf-8"))
        except OSError as e:
            n_err += 1
            print(f"[错误] {f}  写入失败: {e}")
            continue

        n_conv += 1
        print(f"[转换] {f}")

    print(f"\n完成: 共 {len(files)} 个 .cue，转换 {n_conv} 个，跳过 {n_skip} 个，出错 {n_err} 个")
    return 0 if n_err == 0 else 2


if __name__ == "__main__":
    main()
    os.system('pause')