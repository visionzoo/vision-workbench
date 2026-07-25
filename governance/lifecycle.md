# Lifecycle

## Knowledge lifecycle

```text
unclassified inbox → domain path / working → validated → canonical
                                             └→ independent private repo → public
```

- **inbox**：仅保存尚不能归类的原始输入、问题或线索，不作为知识引用。
- **working**：条目已能归入 foundations、engineering、research 或 productization，正在形成问题表征、证据和实验。
- **validated**：关键判断已有新鲜、可寻址的证据支持，并通过本人审查。
- **canonical**：边界、版本、失效条件和复用方式明确，已成为可长期引用的知识。

文件从可归类时起就放在所属主题目录；状态只写在元数据中，不设置 `workspace/working/`，也不通过复制或移动文件晋级。晋级必须更新 `updated`、`confidence`、`evidence_status`、`owner_review`、`ip_review` 与证据指针。证据失效、版本变化或反例出现时应降级，不把状态视为单向荣誉。

## Project lifecycle

想法和方案可在母库孵化；出现可运行代码、能脱离公司资产验证且具备潜在公开价值时，立即建立独立私有仓库。公开前至少满足：独立权属、干净 Git 历史、可在干净环境运行、最小测试、合法数据、英文 README、不过度宣称结果，并发布至少一个语义化版本。

“转为公开”属于 HIGH-RISK 承诺，必须由本人明确确认；Agent 不得仅凭内容成熟度自行公开。

公共入口初期使用 GitHub Profile README。只有成熟公共项目达到 3 个及以上，且 Profile README 不足以清晰组织成果时，才建立 `vision-portfolio`；它不复制私有母库内容。
