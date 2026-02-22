import tkinter as tk
from tkinter import ttk
import json
import os

CONFIG_FILE = "config.json"

class WarframeTraderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Warframe 交易消息快捷生成器 Pro")
        self.root.geometry("850x900")
        
        self.is_loading = True
        self.vars = {}
        self.m4_items_data = [] # 存储模块4的动态物品列表
        self.m6_history_data = [] # 存储模块6的历史记录
        
        self.init_vars()
        self.create_scrollable_ui()
        self.load_config()
        
        self.is_loading = False
        self.update_ui_mode() # 初始化模块1的显示状态
        self.update_preview()

    def init_vars(self):
        # M1: 垃圾 (按组收变量)
        self.vars['m1_active'] = tk.BooleanVar()
        self.vars['m1_mode'] = tk.StringVar(value="group")
        self.vars['m1_g_bronze'] = tk.StringVar(value="6")
        self.vars['m1_g_fsilver'] = tk.StringVar(value="7")
        self.vars['m1_g_silver'] = tk.StringVar(value="18")
        self.vars['m1_g_fgold'] = tk.StringVar(value="32")
        self.vars['m1_g_gold'] = tk.StringVar(value="55")
        
        # M1: 垃圾 (按个收变量)
        self.vars['m1_s_bronze'] = tk.StringVar(value="1")
        self.vars['m1_s_fsilver'] = tk.StringVar(value="2")
        self.vars['m1_s_silver'] = tk.StringVar(value="3")
        self.vars['m1_s_fgold'] = tk.StringVar(value="5")
        self.vars['m1_s_gold'] = tk.StringVar(value="9")
        
        # M2: 核桃
        self.vars['m2_active'] = tk.BooleanVar()
        self.vars['m2_lith'] = tk.StringVar(value="4")
        self.vars['m2_meso'] = tk.StringVar(value="5")
        self.vars['m2_neo'] = tk.StringVar(value="5")
        self.vars['m2_axi'] = tk.StringVar(value="10")
        self.vars['m2_rad'] = tk.BooleanVar()
        
        # M3: Aya
        self.vars['m3_active'] = tk.BooleanVar()
        self.vars['m3_aya'] = tk.StringVar(value="33")
        self.vars['m3_rad'] = tk.BooleanVar()
        
        # M4 控制变量 (是否启用整个模块)
        self.vars['m4_active'] = tk.BooleanVar()

        # M5: 后缀
        self.vars['m5_cn'] = tk.StringVar(value="私聊即可")
        self.vars['m5_en'] = tk.StringVar(value="PM me")

        # M6: 遗物组队消息
        self.vars['m6_epoch'] = tk.StringVar(value="古")
        self.vars['m6_code'] = tk.StringVar(value="A1")
        self.vars['m6_mode'] = tk.StringVar(value="求拉")
        self.vars['m6_count'] = tk.StringVar(value="2")
        self.vars['m6_note'] = tk.StringVar(value="")

        # 致谢
        self.vars['thanks_msg'] = tk.StringVar(value="Tyvm, have a good day!")

        for key, var in self.vars.items():
            var.trace_add("write", self.on_state_change)

    def on_state_change(self, *args):
        if not self.is_loading:
            self.update_preview()
            self.save_config()

    def create_scrollable_ui(self):
        # 创建滚动画布
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.canvas, padding="10")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # 绑定画布宽度随窗口变化
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_frame, width=e.width))
        # 绑定鼠标滚轮
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.build_ui_content(self.scrollable_frame)

    def _on_mousewheel(self, event):
        # 只有在内容超出可视区域时才允许滚动
        if self.canvas.bbox("all") and self.canvas.bbox("all")[3] > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def build_ui_content(self, parent):
        # ================= 模块 1：收 Prime 垃圾 =================
        lf1 = ttk.LabelFrame(parent, text=" 模块 1：收 Prime 垃圾 (Prime Junk) ")
        lf1.pack(fill=tk.X, pady=5, ipady=5)
        
        top_lf1 = ttk.Frame(lf1)
        top_lf1.pack(fill=tk.X, padx=5, pady=5)
        ttk.Checkbutton(top_lf1, text="启用此模块", variable=self.vars['m1_active']).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(top_lf1, text="按组(6个)收", variable=self.vars['m1_mode'], value="group", command=self.update_ui_mode).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(top_lf1, text="按个收", variable=self.vars['m1_mode'], value="single", command=self.update_ui_mode).pack(side=tk.LEFT)

        # 准备两套界面
        self.m1_g_frame = ttk.Frame(lf1)
        self.m1_s_frame = ttk.Frame(lf1)
        self.ratio_labels = [] # 清空重新收集

        junk_types = [
            ("铜 (15 Ducats)", 'bronze', 15), ("假银 (25 Ducats)", 'fsilver', 25),
            ("银 (45 Ducats)", 'silver', 45), ("假金 (65 Ducats)", 'fgold', 65),
            ("金 (100 Ducats)", 'gold', 100)
        ]

        # 构建按组界面
        for i, (label, base_name, ducats) in enumerate(junk_types):
            var_name = f'm1_g_{base_name}'
            ttk.Label(self.m1_g_frame, text=label).grid(row=i, column=0, padx=5, sticky=tk.W)
            ttk.Entry(self.m1_g_frame, textvariable=self.vars[var_name], width=8).grid(row=i, column=1, padx=5, pady=2)
            ttk.Label(self.m1_g_frame, text=":platinum:").grid(row=i, column=2, sticky=tk.W)
            r_lbl = ttk.Label(self.m1_g_frame, foreground="gray")
            r_lbl.grid(row=i, column=3, padx=10, sticky=tk.W)
            self.ratio_labels.append((r_lbl, var_name, ducats, True)) # True 代表是按组

        # 构建按个界面
        for i, (label, base_name, ducats) in enumerate(junk_types):
            var_name = f'm1_s_{base_name}'
            ttk.Label(self.m1_s_frame, text=label).grid(row=i, column=0, padx=5, sticky=tk.W)
            ttk.Entry(self.m1_s_frame, textvariable=self.vars[var_name], width=8).grid(row=i, column=1, padx=5, pady=2)
            ttk.Label(self.m1_s_frame, text=":platinum:").grid(row=i, column=2, sticky=tk.W)
            r_lbl = ttk.Label(self.m1_s_frame, foreground="gray")
            r_lbl.grid(row=i, column=3, padx=10, sticky=tk.W)
            self.ratio_labels.append((r_lbl, var_name, ducats, False)) # False 代表按个

        # ================= 模块 2：收遗物/核桃 =================
        lf2 = ttk.LabelFrame(parent, text=" 模块 2：收遗物/核桃 (Relics) ")
        lf2.pack(fill=tk.X, pady=5, ipady=5)
        ttk.Checkbutton(lf2, text="启用此模块", variable=self.vars['m2_active']).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        relic_types = [("古(Lith)", 'm2_lith'), ("前(Meso)", 'm2_meso'), ("中(Neo)", 'm2_neo'), ("后(Axi)", 'm2_axi')]
        for i, (label, var_name) in enumerate(relic_types):
            ttk.Label(lf2, text=label).grid(row=1, column=i*2, padx=5, sticky=tk.W)
            ttk.Entry(lf2, textvariable=self.vars[var_name], width=5).grid(row=1, column=i*2+1, padx=2)
        ttk.Label(lf2, text="白金/组").grid(row=1, column=8, padx=5)
        ttk.Checkbutton(lf2, text="光辉核桃每个额外+1白金", variable=self.vars['m2_rad']).grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky=tk.W)

        # ================= 模块 3：收阿耶精华 =================
        lf3 = ttk.LabelFrame(parent, text=" 模块 3：收阿耶精华 (Aya) ")
        lf3.pack(fill=tk.X, pady=5, ipady=5)
        ttk.Checkbutton(lf3, text="启用此模块", variable=self.vars['m3_active']).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(lf3, text="每组价格:").grid(row=1, column=0, padx=5, sticky=tk.W)
        ttk.Entry(lf3, textvariable=self.vars['m3_aya'], width=8).grid(row=1, column=1, padx=5)
        ttk.Label(lf3, text=":platinum:").grid(row=1, column=2, sticky=tk.W)
        ttk.Checkbutton(lf3, text="光辉核桃每个额外+1白金", variable=self.vars['m3_rad']).grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)

        # ================= 模块 4：自定义多物品 =================
        lf4 = ttk.LabelFrame(parent, text=" 模块 4：自定义多物品 (生成时自动分类收/出) ")
        lf4.pack(fill=tk.X, pady=5, ipady=5)
        
        top_lf4 = ttk.Frame(lf4)
        top_lf4.pack(fill=tk.X, padx=5, pady=5)
        ttk.Checkbutton(top_lf4, text="启用此模块", variable=self.vars['m4_active']).pack(side=tk.LEFT)
        ttk.Button(top_lf4, text="+ 添加一件物品", command=self.add_m4_item).pack(side=tk.LEFT, padx=15)
        
        self.m4_container = ttk.Frame(lf4)
        self.m4_container.pack(fill=tk.X, padx=5)

        # ================= 模块 5：自定义后缀短语 =================
        lf5 = ttk.LabelFrame(parent, text=" 模块 5：自定义后缀短语 ")
        lf5.pack(fill=tk.X, pady=5, ipady=5)
        ttk.Label(lf5, text="中文后缀:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(lf5, textvariable=self.vars['m5_cn'], width=40).grid(row=0, column=1, padx=5)
        ttk.Label(lf5, text="英文后缀:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(lf5, textvariable=self.vars['m5_en'], width=40).grid(row=1, column=1, padx=5)

        # ================= 模块 6：遗物组队高频消息 =================
        lf6 = ttk.LabelFrame(parent, text=" 模块 6：遗物组队高频消息 ")
        lf6.pack(fill=tk.X, pady=5, ipady=5)

        ttk.Label(lf6, text="纪元:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        cb_epoch = ttk.Combobox(lf6, textvariable=self.vars['m6_epoch'], values=["古", "前", "中", "后"], width=6, state='readonly')
        cb_epoch.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(lf6, text="代号:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(lf6, textvariable=self.vars['m6_code'], width=10).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        ttk.Label(lf6, text="模式:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        cb_mode = ttk.Combobox(lf6, textvariable=self.vars['m6_mode'], values=["求拉", "人数"], width=8, state='readonly')
        cb_mode.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        ttk.Label(lf6, text="人数(1-4):").grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(lf6, textvariable=self.vars['m6_count'], width=6).grid(row=0, column=7, padx=5, pady=5, sticky=tk.W)

        ttk.Label(lf6, text="备注:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(lf6, textvariable=self.vars['m6_note'], width=50).grid(row=1, column=1, columnspan=5, padx=5, pady=5, sticky=tk.W)
        ttk.Button(lf6, text="添加到历史", command=self.add_m6_history_item).grid(row=1, column=6, padx=5, pady=5, sticky=tk.W)

        ttk.Label(lf6, text="中文组队:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        self.text_m6_cn = tk.Text(lf6, height=2, width=70, state='disabled', wrap='word', font=('Microsoft YaHei', 9))
        self.text_m6_cn.grid(row=2, column=1, columnspan=6, padx=5, pady=5, sticky=tk.W)
        ttk.Button(lf6, text="复制中文", command=lambda: self.copy_to_clipboard(self.text_m6_cn.get(1.0, tk.END))).grid(row=2, column=7, padx=5, pady=5, sticky=tk.W)

        ttk.Label(lf6, text="英文组队:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.NW)
        self.text_m6_en = tk.Text(lf6, height=2, width=70, state='disabled', wrap='word', font=('Microsoft YaHei', 9))
        self.text_m6_en.grid(row=3, column=1, columnspan=6, padx=5, pady=5, sticky=tk.W)
        ttk.Button(lf6, text="复制英文", command=lambda: self.copy_to_clipboard(self.text_m6_en.get(1.0, tk.END))).grid(row=3, column=7, padx=5, pady=5, sticky=tk.W)

        ttk.Label(lf6, text="历史卡片:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.NW)
        self.m6_history_container = ttk.Frame(lf6)
        self.m6_history_container.grid(row=4, column=1, columnspan=7, padx=5, pady=5, sticky=tk.W+tk.E)
        lf6.columnconfigure(1, weight=1)

        # ================= 预览与操作区 =================
        preview_frame = ttk.LabelFrame(parent, text=" 实时预览")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10, ipady=5)

        ttk.Label(preview_frame, text="中文喊话:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.NW)
        self.text_cn = tk.Text(preview_frame, height=2, width=75, state='disabled', wrap='word', font=('Microsoft YaHei', 9))
        self.text_cn.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(preview_frame, text="复制中文", command=lambda: self.copy_to_clipboard(self.text_cn.get(1.0, tk.END))).grid(row=0, column=2, padx=5)

        ttk.Label(preview_frame, text="英文喊话:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.NW)
        self.text_en = tk.Text(preview_frame, height=2, width=75, state='disabled', wrap='word', font=('Microsoft YaHei', 9))
        self.text_en.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(preview_frame, text="复制英文", command=lambda: self.copy_to_clipboard(self.text_en.get(1.0, tk.END))).grid(row=1, column=2, padx=5)

        ttk.Label(preview_frame, text="致谢短语:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        self.text_thanks = tk.Text(preview_frame, height=2, width=75, wrap='word', font=('Microsoft YaHei', 9))
        self.text_thanks.grid(row=2, column=1, padx=5, pady=5)
        # 将 StringVar 同步到 Text
        self.text_thanks.insert(1.0, self.vars['thanks_msg'].get())
        self.text_thanks.bind("<<Modified>>", self.on_thanks_modified)
        ttk.Button(preview_frame, text="复制致谢", command=lambda: self.copy_to_clipboard(self.text_thanks.get(1.0, tk.END))).grid(row=2, column=2, padx=5)

    def on_thanks_modified(self, event):
        if self.text_thanks.edit_modified():
            self.vars['thanks_msg'].set(self.text_thanks.get(1.0, tk.END).strip())
            self.dynamic_resize_text(self.text_thanks, self.vars['thanks_msg'].get())
            self.text_thanks.edit_modified(False)
            self.on_state_change()

    def update_ui_mode(self):
        """切换模块1的显示帧"""
        if self.vars['m1_mode'].get() == "group":
            self.m1_s_frame.pack_forget()
            self.m1_g_frame.pack(fill=tk.X, padx=5, pady=5)
        else:
            self.m1_g_frame.pack_forget()
            self.m1_s_frame.pack(fill=tk.X, padx=5, pady=5)
        self.on_state_change()

    def add_m4_item(self, data=None):
        """动态添加模块4的一行"""
        item_vars = {
            'active': tk.BooleanVar(value=data.get('active', True) if data else True),
            'type': tk.StringVar(value=data.get('type', "WTB") if data else "WTB"),
            'item': tk.StringVar(value=data.get('item', "") if data else ""),
            'price': tk.StringVar(value=data.get('price', "") if data else "")
        }
        
        for v in item_vars.values():
            v.trace_add("write", self.on_state_change)
            
        row_frame = ttk.Frame(self.m4_container)
        row_frame.pack(fill=tk.X, pady=2)
        
        ttk.Checkbutton(row_frame, variable=item_vars['active']).pack(side=tk.LEFT, padx=2)
        cb = ttk.Combobox(row_frame, textvariable=item_vars['type'], values=["WTB", "WTS"], width=5, state='readonly')
        cb.pack(side=tk.LEFT, padx=5)
        ttk.Label(row_frame, text="名称:").pack(side=tk.LEFT)
        ttk.Entry(row_frame, textvariable=item_vars['item'], width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(row_frame, text="价格:").pack(side=tk.LEFT)
        ttk.Entry(row_frame, textvariable=item_vars['price'], width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(row_frame, text=":platinum:").pack(side=tk.LEFT)
        
        def remove_self():
            row_frame.destroy()
            self.m4_items_data.remove(item_vars)
            self.on_state_change()
            
        ttk.Button(row_frame, text="删除", width=6, command=remove_self).pack(side=tk.LEFT, padx=10)
        
        self.m4_items_data.append(item_vars)
        if not self.is_loading:
            self.on_state_change()

    def get_m6_relic_texts(self, epoch, code):
        epoch_map_cn = {
            '古': '古纪',
            '前': '前纪',
            '中': '中纪',
            '后': '后纪'
        }
        epoch_map_en = {
            '古': 'Lith',
            '前': 'Meso',
            '中': 'Neo',
            '后': 'Axi'
        }
        epoch_cn = epoch_map_cn.get(epoch, '古纪')
        epoch_en = epoch_map_en.get(epoch, 'Lith')
        relic_cn = f"[{epoch_cn} {code} 遗物]"
        relic_en = f"[{epoch_en} {code} Relic]"
        return relic_cn, relic_en

    def build_m6_messages(self, epoch, code, mode, count):
        relic_cn, relic_en = self.get_m6_relic_texts(epoch, code)
        try:
            count_num = int(str(count).strip())
        except:
            count_num = 2
        count_num = max(1, min(4, count_num))
        wait_num = 4 - count_num

        if mode == "人数":
            cn_msg = f"{relic_cn}光{count_num}====={wait_num}"
            en_msg = f"H {relic_en} Rad {count_num}/4"
        else:
            cn_msg = f"{relic_cn}光求拉"
            en_msg = f"H {relic_en} Rad"
        return relic_cn, cn_msg, en_msg

    def update_m6_preview(self):
        epoch = self.vars['m6_epoch'].get().strip() or '古'
        code = self.vars['m6_code'].get().strip().upper() or 'A1'
        mode = self.vars['m6_mode'].get().strip() or '求拉'
        count = self.vars['m6_count'].get().strip() or '2'

        _, cn_msg, en_msg = self.build_m6_messages(epoch, code, mode, count)

        self.text_m6_cn.config(state='normal')
        self.text_m6_cn.delete(1.0, tk.END)
        self.text_m6_cn.insert(tk.END, cn_msg)
        self.text_m6_cn.config(state='disabled')

        self.text_m6_en.config(state='normal')
        self.text_m6_en.delete(1.0, tk.END)
        self.text_m6_en.insert(tk.END, en_msg)
        self.text_m6_en.config(state='disabled')

        self.dynamic_resize_text(self.text_m6_cn, cn_msg)
        self.dynamic_resize_text(self.text_m6_en, en_msg)

    def add_m6_history_item(self):
        epoch = self.vars['m6_epoch'].get().strip() or '古'
        code = self.vars['m6_code'].get().strip().upper() or 'A1'
        mode = self.vars['m6_mode'].get().strip() or '求拉'
        count = self.vars['m6_count'].get().strip() or '2'
        note = self.vars['m6_note'].get().strip()

        item = {
            'epoch': epoch,
            'code': code,
            'mode': mode,
            'count': count,
            'note': note
        }
        self.m6_history_data.insert(0, item)
        self.render_m6_history()
        self.on_state_change()

    def apply_m6_history_item(self, idx):
        if idx < 0 or idx >= len(self.m6_history_data):
            return
        item = self.m6_history_data[idx]
        self.vars['m6_epoch'].set(item.get('epoch', '古'))
        self.vars['m6_code'].set(item.get('code', 'A1'))
        self.vars['m6_mode'].set(item.get('mode', '求拉'))
        self.vars['m6_count'].set(item.get('count', '2'))
        self.vars['m6_note'].set(item.get('note', ''))
        self.on_state_change()

    def save_m6_note(self, idx, note_var):
        if idx < 0 or idx >= len(self.m6_history_data):
            return
        self.m6_history_data[idx]['note'] = note_var.get().strip()
        self.on_state_change()

    def remove_m6_history_item(self, idx):
        if idx < 0 or idx >= len(self.m6_history_data):
            return
        self.m6_history_data.pop(idx)
        self.render_m6_history()
        self.on_state_change()

    def copy_m6_relic_name(self, idx):
        if idx < 0 or idx >= len(self.m6_history_data):
            return
        item = self.m6_history_data[idx]
        relic_cn, _ = self.get_m6_relic_texts(item.get('epoch', '古'), item.get('code', 'A1'))
        self.copy_to_clipboard(relic_cn)

    def render_m6_history(self):
        for child in self.m6_history_container.winfo_children():
            child.destroy()

        if not self.m6_history_data:
            ttk.Label(self.m6_history_container, text="暂无历史记录", foreground="gray").pack(anchor=tk.W, pady=2)
            return

        for idx, item in enumerate(self.m6_history_data):
            card = ttk.Frame(self.m6_history_container)
            card.pack(fill=tk.X, pady=3)

            relic_cn, cn_msg, en_msg = self.build_m6_messages(
                item.get('epoch', '古'),
                item.get('code', 'A1'),
                item.get('mode', '求拉'),
                item.get('count', '2')
            )

            ttk.Label(card, text=relic_cn, width=18).pack(side=tk.LEFT, padx=2)
            ttk.Label(card, text=cn_msg, width=28).pack(side=tk.LEFT, padx=2)
            ttk.Label(card, text=en_msg, width=26).pack(side=tk.LEFT, padx=2)

            ttk.Button(card, text="一键应用", width=8, command=lambda i=idx: self.apply_m6_history_item(i)).pack(side=tk.LEFT, padx=2)
            ttk.Button(card, text="复制遗物名", width=10, command=lambda i=idx: self.copy_m6_relic_name(i)).pack(side=tk.LEFT, padx=2)

            note_var = tk.StringVar(value=item.get('note', ''))
            ttk.Entry(card, textvariable=note_var, width=16).pack(side=tk.LEFT, padx=2)
            ttk.Button(card, text="保存备注", width=8, command=lambda i=idx, nv=note_var: self.save_m6_note(i, nv)).pack(side=tk.LEFT, padx=2)
            ttk.Button(card, text="删除", width=6, command=lambda i=idx: self.remove_m6_history_item(i)).pack(side=tk.LEFT, padx=2)

    def update_ratios(self):
        for lbl, var_name, ducats, is_group_calc in self.ratio_labels:
            try:
                plat_val = float(self.vars[var_name].get())
                if plat_val <= 0: raise ValueError
                plat_per_item = plat_val / 6.0 if is_group_calc else plat_val
                ratio = ducats / plat_per_item
                lbl.config(text=f"比例: {ratio:.1f} 杜卡德/白金", foreground="blue")
            except:
                lbl.config(text="比例: - 杜卡德/白金", foreground="red")

    def dynamic_resize_text(self, widget, content):
        """根据内容长度估算并动态调整文本框的高度"""
        # 粗略计算：每60个字符算一行，加上本身的换行符
        lines = 1
        for line in content.split('\n'):
            lines += (len(line) // 60) + 1
        widget.config(height=min(10, max(2, lines))) # 高度限制在 2 到 10 行之间

    def update_preview(self):
        self.update_ratios()
        cn_parts, en_parts = [], []

        # -- M1 --
        if self.vars['m1_active'].get():
            is_g = (self.vars['m1_mode'].get() == "group")
            pfx = "m1_g_" if is_g else "m1_s_"
            b, fs, s, fg, g = (self.vars[f'{pfx}bronze'].get(), self.vars[f'{pfx}fsilver'].get(), 
                               self.vars[f'{pfx}silver'].get(), self.vars[f'{pfx}fgold'].get(), self.vars[f'{pfx}gold'].get())
            mode_cn = "组" if is_g else "个"
            mode_en = "6" if is_g else "1"
            
            cn_parts.append(f"收铜/假银/银/假金/金垃圾 {b}:platinum:/{fs}:platinum:/{s}:platinum:/{fg}:platinum:/{g}:platinum:可混")
            en_parts.append(f"WTB prime junk 15:ducats:={b}:platinum: 25:ducats:={fs}:platinum: 45:ducats:={s}:platinum: 65:ducats:={fg}:platinum: 100:ducats:={g}:platinum: canmix")

        # -- M2 --
        if self.vars['m2_active'].get():
            l, m, n, a = (self.vars['m2_lith'].get(), self.vars['m2_meso'].get(), self.vars['m2_neo'].get(), self.vars['m2_axi'].get())
            rad_cn = " 光+1p" if self.vars['m2_rad'].get() else ""
            rad_en = " Rad+1p ea" if self.vars['m2_rad'].get() else ""
            cn_parts.append(f"收古/前/中/后核桃 {l}/{m}/{n}/{a}:platinum:{rad_cn}")
            en_parts.append(f"WTB Lith/Meso/Neo/Axi Relics {l}/{m}/{n}/{a}:platinum:{rad_en}")

        # -- M3 --
        if self.vars['m3_active'].get():
            aya_p = self.vars['m3_aya'].get()
            rad_cn = " 光+1p" if self.vars['m3_rad'].get() else ""
            rad_en = " Rad+1p ea" if self.vars['m3_rad'].get() else ""
            cn_parts.append(f"收阿耶{aya_p}p{rad_cn}")
            en_parts.append(f"WTB[Aya] 6 for {aya_p}p{rad_en}")

        # -- M4 (自动分组 WTB / WTS) --
        if self.vars['m4_active'].get():
            wtb_cn, wts_cn, wtb_en, wts_en = [], [], [], []
            for d in self.m4_items_data:
                if d['active'].get():
                    item = d['item'].get().strip()
                    if not item: continue
                    price = d['price'].get()
                    item_str = f"[{item}] {price}:platinum:"
                    
                    if d['type'].get() == "WTB":
                        wtb_cn.append(item_str); wtb_en.append(item_str)
                    else:
                        wts_cn.append(item_str); wts_en.append(item_str)
            
            if wtb_cn: cn_parts.append("收" + " ".join(wtb_cn))
            if wts_cn: cn_parts.append("出" + " ".join(wts_cn))
            if wtb_en: en_parts.append("WTB" + " ".join(wtb_en))
            if wts_en: en_parts.append("WTS" + " ".join(wts_en))
        
        # -- M5 --
        suffix_cn = self.vars['m5_cn'].get().strip()
        suffix_en = self.vars['m5_en'].get().strip()
        if suffix_cn: cn_parts.append(suffix_cn)
        if suffix_en: en_parts.append(suffix_en)

        final_cn = ",".join(cn_parts)
        final_en = "| ".join(en_parts)
        self.text_cn.config(state='normal')
        self.text_cn.delete(1.0, tk.END)
        self.text_cn.insert(tk.END, final_cn)
        self.text_cn.config(state='disabled')
        self.text_en.config(state='normal')
        self.text_en.delete(1.0, tk.END)
        self.text_en.insert(tk.END, final_en)
        self.text_en.config(state='disabled')
        self.dynamic_resize_text(self.text_cn, final_cn)
        self.dynamic_resize_text(self.text_en, final_en)
        self.update_m6_preview()

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text.strip())
        self.root.update() # 现在剪贴板内容已经更新

    def save_config(self):
        config = {key: var.get() for key, var in self.vars.items()}
        # 模块4的动态物品列表
        config['m4_items'] = []
        for item in self.m4_items_data:
            item_dict = {k: v.get() for k, v in item.items()}
            config['m4_items'].append(item_dict)
        config['m6_history'] = self.m6_history_data
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            for key, value in config.items():
                if key.startswith('m4_items'):
                    continue # 模块4单独处理
                if key in self.vars:
                    self.vars[key].set(value)
            # 加载模块4的动态物品列表
            for item_data in config.get('m4_items', []):
                self.add_m4_item(data=item_data)
            self.m6_history_data = config.get('m6_history', [])
            self.render_m6_history()
if __name__ == "__main__":
    root = tk.Tk()
    app = WarframeTraderApp(root)
    root.mainloop()