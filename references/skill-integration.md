# Skill and tool integration

The travel skill orchestrates research and planning. Call adjacent skills only for the requested artifact or a necessary quality check.

| Need | Skill or tool | Use |
|---|---|---|
| Full China trip | `$china-trip-planner` | Own requirements, evidence ledger, routing, meals, lodging, budget, risk, and updates |
| Existing Xiaohongshu, Dianping, or Amap tabs | Chrome CUA | Read the user's current session, search exact POIs, inspect routes, and capture current observations |
| Official or current public facts | Web research | Verify dates, notices, transport, weather, and rules with authoritative sources |
| PPT or PPTX | `presentations:Presentations` | Build, edit, render, and validate the deck after the plan is final |
| Illustrative cover or divider | `imagegen` | Generate decorative images; disclose that they are illustrative |
| POI or budget workbook | `spreadsheets:Spreadsheets` | Create editable tables, formulas, and charts |
| DOCX guide | `documents:documents` | Create and visually verify a document |
| PDF guide | `pdf:pdf` | Create or inspect the final PDF |

Do not let artifact creation become a second planning source. Update `trip-input.json`, `poi-ledger.json`, and `plan.json` first, then regenerate affected outputs.

For a revision such as “add Kashgar,” “cut the budget,” “it will rain,” or “change three days to four,” preserve verified evidence, update the affected inputs, and recalculate the complete route and budget. Never patch only the visible paragraph or slide.
  
