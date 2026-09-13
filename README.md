# RESERVOIR / 蓄水池 — 内容更新 04

数据来源：桌面《蓄水池梳理.xlsx》与「蓄水池」图片文件夹。
按一级分类的 1–6 标记和第三列序号匹配图片 a-b，显示编号 R-A-n 至 R-F-n。不依赖固定行区间。

本次 90 条表格案例、85 张图片；85 张均匹配文字。未提供图片的 R-B-4、R-B-6、R-B-8、R-B-13、R-B-14 不展示。

六类当前数量：A 功能原型 14、B 空间原型 15、C 机制原型 13、D 空间变型 15、E 介质变型 13、F 观念变型 15。B 类名称遵循新表。

保留蓝白风格、GRID 密度、FLOW 双语关键词频次与关联卡片、LAYER 时间蓄水池、MAP 坐标、DEPTH 球面和 DREDGE。三维动作仍仅作用于 A、B 两类。关键词频次与关系随新数据重算；新增英文关键词是界面译文，中文标签保留原表。

原表主次动作原样规范空格后保留；界面三维控制仍使用已有动作。MAP 沿用既有定位规则，25 条可定位、60 条待定位。日期有明确起始年时排序；不明或格式异常的年代放入未标注区，原文保留。

双击「启动网站.command」打开本地网站，保持服务终端运行。已构建的 dist 不需要网络或依赖安装。

## 后续更新

运行 scripts/import_archive.py，提供 --excel 表格路径、--images 图片目录。导入需要 openpyxl、Pillow，只读取源文件。表头验证后按分类标记分区，重复编号会报错。新增关键词需在 src/data/keywordTranslations.json 中补充英文。

开发使用 pnpm install、pnpm dev；pnpm build 更新 dist。

data-audit/image-mapping.csv 是逐图对应关系，report.json 列明来源、数量与缺图条目。validation-v4.json 记录本轮运行验证。
