# Lifecycle

## Knowledge lifecycle

```text
inbox → working → validated → canonical
                         └→ independent private repo → public
```

- **inbox**：仅保存待处理的问题、材料或线索，不作为知识引用。
- **working**：问题和竞争解释明确，正在搜集证据或实验。
- **validated**：关键判断已有支持，但仍可能受条件限制。
- **canonical**：已成为可长期引用的正式知识。

状态写在文档元数据中，不复制文件到多个状态目录。晋级必须更新 `updated`、`confidence` 和证据边界。

## Project lifecycle

想法和方案可在母库孵化；出现可运行代码且具备潜在公开价值时，立即建立独立私有仓库。公开前至少满足：独立权属、干净 Git 历史、可在干净环境运行、最小测试、合法数据、英文 README、不过度宣称结果，并发布至少一个语义化版本。

公共入口初期使用 GitHub Profile README。只有成熟公共项目达到 3 个及以上，且 Profile README 不足以清晰组织成果时，才建立 `vision-portfolio`；它不复制私有母库内容。
