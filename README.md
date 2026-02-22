# WF_Trader

一个基于 Tkinter 的 Warframe 交易消息快捷生成器，支持中文/英文消息实时预览与一键复制。

## 功能

- 模块化生成交易喊话（Prime 垃圾、核桃、Aya、自定义多物品）
- 自动生成中文与英文两套消息
- 遗物组队高频消息生成与历史记录
- 自定义后缀与致谢短语
- 配置自动保存到本地 `config.json`

## 运行环境

- Python 3.8+
- Tkinter（通常随 Python 自带）

## 快速开始

1. 进入项目目录
2. 运行：

```bash
python wf_trader.py
```

## 配置说明

- 程序会在项目目录下读写 `config.json`
- 首次运行会按代码默认值生成配置

## 项目结构

- `wf_trader.py`：主程序
- `config.json`：运行配置
