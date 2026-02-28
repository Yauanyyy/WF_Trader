# WF Trader 网页版需求规格（独立实现版）

## 1. 目标
- 实现一个单页 Web 工具，用于快速生成 Warframe 交易与组队频道文本。
- 用户应仅根据本文档即可完成实现，无需依赖任何其他源码。

## 2. 技术边界
- 前端单页：`HTML + CSS + JavaScript`。
- 无后端依赖。
- 状态持久化使用 `localStorage`。

## 3. 视觉与布局要求
### 3.1 界面要求
- 界面需美观、整洁、信息层级清晰。
- 统一间距、圆角、边框和按钮风格。
- 表单、预览、历史卡片要有清晰分组与留白。

### 3.2 页面结构
- 页面为“侧边栏 + 主内容区”布局。
- 侧边栏提供区域切换（单选）：
1. 交易区域
2. 组队区域
- 主内容区根据侧边栏切换显示对应区域内容。

## 4. 区域划分
- 交易区域包含模块：模块1、模块2、模块3、模块4、模块5。
- 组队区域包含模块：模块6、模块7（新增：自定义组队短语）。

## 5. 全局交互规则
- 任意输入变化时必须立即：
1. 刷新相关预览
2. 自动保存到本地存储
- 复制按钮统一行为：
1. 复制对应文本
2. 自动 `trim` 首尾空白
3. 失败时给出可见提示
- 文本框高度动态调整：最小 2 行，最大 10 行。

## 6. 交易区域

## 6.0 交易区域通用：白金显示格式选择（新增）
### 6.0.1 功能
- 模块1~5每个模块都必须提供“白金显示格式”选择器：
1. `:platinum:`
2. `p`
- 每个模块独立生效，互不影响。

### 6.0.2 字段
- `m1_plat_token` 默认 `:platinum:`
- `m2_plat_token` 默认 `:platinum:`
- `m3_plat_token` 默认 `:platinum:`
- `m4_plat_token` 默认 `:platinum:`
- `m5_plat_token` 默认 `:platinum:`

### 6.0.3 应用规则
- 模块1~4所有“价格单位”必须使用各自模块 `{plat}` 变量，禁止硬编码。
- 模块5当前没有内置价格字段，但仍保留该选择器并保存状态（用于统一交互与后续扩展）。

## 6.1 模块1：Prime Junk 收购
### 6.1.1 字段
- `m1_active`（boolean）
- `m1_mode`：`group` | `single`
- 按组价格（默认）：
1. `m1_g_bronze`=`6`
2. `m1_g_fsilver`=`7`
3. `m1_g_silver`=`18`
4. `m1_g_fgold`=`32`
5. `m1_g_gold`=`55`
- 按个价格（默认）：
1. `m1_s_bronze`=`1`
2. `m1_s_fsilver`=`2`
3. `m1_s_silver`=`3`
4. `m1_s_fgold`=`5`
5. `m1_s_gold`=`9`

### 6.1.2 比值计算
- 杜卡德固定：15/25/45/65/100。
- `group`：比值 = `ducats / (price / 6)`。
- `single`：比值 = `ducats / price`。
- 无效输入（非数字或 <=0）显示无效状态。

### 6.1.3 文案拼接
- 启用时参与交易总文案。
- 中文：
`收铜/假银/银/假金/金垃圾 {b}{plat}/{fs}{plat}/{s}{plat}/{fg}{plat}/{g}{plat}可混`
- 英文：
`WTB prime junk 15:ducats:={b}{plat} 25:ducats:={fs}{plat} 45:ducats:={s}{plat} 65:ducats:={fg}{plat} 100:ducats:={g}{plat} canmix`
- 其中 `{plat}` = `m1_plat_token`。

## 6.2 模块2：遗物收购（Relics）
### 6.2.1 字段
- `m2_active`（boolean）
- `m2_lith`=`4`
- `m2_meso`=`5`
- `m2_neo`=`5`
- `m2_axi`=`10`
- `m2_rad`（boolean，默认 false，表示光辉每个 +1p）

### 6.2.2 文案拼接
- 中文：`收Lith/Meso/Neo/Axi遗物 {l}/{m}/{n}/{a}{plat}{rad_cn}`
- 英文：`WTB Lith/Meso/Neo/Axi Relics {l}/{m}/{n}/{a}{plat}{rad_en}`
- `rad_cn`：开启时 ` 光辉+1p`，否则空。
- `rad_en`：开启时 ` Rad+1p ea`，否则空。
- 其中 `{plat}` = `m2_plat_token`。

## 6.3 模块3：Aya 收购
### 6.3.1 字段
- `m3_active`（boolean）
- `m3_aya`=`33`
- `m3_rad`（boolean，默认 false）

### 6.3.2 文案拼接
- 中文：`收Aya 6个{aya}{plat}{rad_cn}`
- 英文：`WTB[Aya] 6 for {aya}{plat}{rad_en}`
- 其中 `{plat}` = `m3_plat_token`。

## 6.4 模块4：自定义多物品（WTB/WTS）
### 6.4.1 字段与操作
- `m4_active`（boolean）
- `m4_items`（数组）
- 每个条目结构：
1. `active`（boolean，默认 true）
2. `type`（`WTB` | `WTS`，默认 `WTB`）
3. `item_cn`（中文物品名，默认空）
4. `item_en`（英文物品名，默认空）
5. `price`（字符串，默认空）
- 操作：
1. 新增条目
2. 删除条目
3. 编辑条目
4. 启用/禁用条目

### 6.4.2 拼接规则（中英文分离）
- 仅处理 `active=true` 的条目。
- 中文预览使用 `item_cn`，英文预览使用 `item_en`。
- 若对应语种名称为空，则该语种跳过该条目。
- 单条格式：
1. 中文：`[{item_cn}] {price}{plat}`
2. 英文：`[{item_en}] {price}{plat}`
- 分组：
1. WTB 归并为一个段
2. WTS 归并为一个段
- 前缀：
1. 中文 WTB=`收 `，中文 WTS=`出 `
2. 英文 WTB=`WTB `，英文 WTS=`WTS `
- 其中 `{plat}` = `m4_plat_token`。

## 6.5 模块5：自定义后缀
- `m5_cn` 默认 `私聊即可`
- `m5_en` 默认 `PM me`
- `m5_plat_token` 按 6.0 定义，当前仅保存状态，不直接参与模板拼接。
- 非空时分别追加到交易中文/英文总文案末尾。

## 6.6 交易区域预览
- 显示两块：
1. 交易中文喊话（只读 + 复制）
2. 交易英文喊话（只读 + 复制）
- 汇总算法：
1. 维护 `trade_cn_parts`、`trade_en_parts`
2. 按模块1 -> 2 -> 3 -> 4 -> 5 依次追加
3. 中文最终：`trade_cn_parts.join(",")`
4. 英文最终：`trade_en_parts.join("| ")`

## 7. 组队区域

## 7.1 模块6：遗物组队高频消息
### 7.1.1 字段
- `m6_epoch`：`Lith`/`Meso`/`Neo`/`Axi`，默认 `Lith`
- `m6_code`：默认 `A1`（使用时转大写）
- `m6_mode`：`求拉`/`人数`，默认 `求拉`
- `m6_count`：默认 `2`，范围 1~4
- `m6_note`：默认空
- `m6_history`：数组，默认空

### 7.1.2 映射与文案
- 中文纪元映射：Lith=古纪，Meso=前纪，Neo=中纪，Axi=后纪。
- 遗物名：
1. 中文：`[{中文纪元} {CODE} 遗物]`
2. 英文：`[{Epoch} {CODE} Relic]`
- `count` 非法时回退 `2`，并夹紧到 `1~4`。
- `wait = 4 - count`。
- `m6_mode=人数`：
1. 中文：`{relic_cn} 光辉 {count}/4，差{wait}`
2. 英文：`H {relic_en} Rad {count}/4`
- `m6_mode=求拉`：
1. 中文：`{relic_cn} 光辉求拉`
2. 英文：`H {relic_en} Rad`

### 7.1.3 历史功能
- “添加到历史”把当前配置插到列表头部。
- 每条历史支持：
1. 一键应用
2. 复制遗物名（中文）
3. 保存备注
4. 删除
- 空历史显示“暂无历史记录”。

## 7.2 模块7：自定义组队短语快捷模块
### 7.2.1 目的
- 支持用户保存常用组队短语，点击即可快速填充或复制，减少重复输入。

### 7.2.2 字段与数据结构
- `m7_items`（数组，默认空）
- 每条快捷短语结构：
1. `active`（boolean，默认 true）
2. `title`（可选）
3. `text_cn`（中文短语）
4. `text_en`（英文短语）

### 7.2.3 功能要求
- 支持新增、编辑、删除、启用/禁用。
- 每条支持：
1. 应用到快捷输出
2. 复制中文
3. 复制英文
- 仅 `active=true` 的条目显示在快捷按钮区。

### 7.2.4 展示
- 组队区域提供“快捷组队输出”双文本框：
1. 快捷中文（只读）
2. 快捷英文（只读）
- 点击某条“应用”后更新上述文本框。

## 7.3 组队区域预览
- 至少包含四块输出：
1. 模块6中文组队消息（只读 + 复制）
2. 模块6英文组队消息（只读 + 复制）
3. 快捷中文输出（只读 + 复制）
4. 快捷英文输出（只读 + 复制）

## 8. 致谢短语
- `thanks_msg` 默认 `Tyvm, have a good day!`
- 可编辑并可复制。
- 可放在交易区域或公共区域，但必须持久化保存。

## 9. 本地存储
### 9.1 Key
- `wf_trader_config_v1`

### 9.2 保存时机
- 任意状态变化即保存。

### 9.3 推荐结构
```json
{
  "active_region": "trade",
  "m1_active": false,
  "m1_plat_token": ":platinum:",
  "m1_mode": "group",
  "m1_g_bronze": "6",
  "m1_g_fsilver": "7",
  "m1_g_silver": "18",
  "m1_g_fgold": "32",
  "m1_g_gold": "55",
  "m1_s_bronze": "1",
  "m1_s_fsilver": "2",
  "m1_s_silver": "3",
  "m1_s_fgold": "5",
  "m1_s_gold": "9",
  "m2_active": false,
  "m2_plat_token": ":platinum:",
  "m2_lith": "4",
  "m2_meso": "5",
  "m2_neo": "5",
  "m2_axi": "10",
  "m2_rad": false,
  "m3_active": false,
  "m3_plat_token": ":platinum:",
  "m3_aya": "33",
  "m3_rad": false,
  "m4_active": false,
  "m4_plat_token": ":platinum:",
  "m4_items": [],
  "m5_plat_token": ":platinum:",
  "m5_cn": "私聊即可",
  "m5_en": "PM me",
  "m6_epoch": "Lith",
  "m6_code": "A1",
  "m6_mode": "求拉",
  "m6_count": "2",
  "m6_note": "",
  "m6_history": [],
  "m7_items": [],
  "m7_quick_cn": "",
  "m7_quick_en": "",
  "thanks_msg": "Tyvm, have a good day!"
}
```

### 9.4 初始化
- 无存储时使用默认值。
- 缺失字段回退默认值。

## 10. 非功能要求
- 视觉：整洁、统一、可读性高。
- 响应式：桌面与移动端可用。
- 稳定性：非法输入不导致崩溃。
- 性能：`m6_history<=100`、`m4_items<=50`、`m7_items<=100` 仍流畅。

## 11. 验收标准（全部必须通过）
1. 侧边栏可在“交易区域/组队区域”间切换。
2. 交易区域仅显示模块1-5；组队区域仅显示模块6-7。
3. 交易模块1-5均有白金显示格式选择器（`:platinum:`/`p`），并可持久化。
4. 模块1-4文案中的白金单位随各模块选择器实时切换。
5. 模块4支持中英文物品名分别输入并分别参与对应语种拼接。
6. 交易中文按 `,` 拼接，交易英文按 `| ` 拼接。
7. 模块6可生成中英文组队消息并管理历史。
8. 模块7可新增自定义组队短语并快速应用/复制。
9. 所有复制按钮可用，刷新后配置可恢复。
10. 页面视觉整洁，控制台无未处理异常。
