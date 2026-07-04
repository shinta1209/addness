# 引き継ぎプロンプト: Addness 7/7ゴールへの登録作業(2026-07-04作成)

このファイルの内容を新スレッドに貼れば、Addnessゴール登録の続きができる。

---

## やってほしいこと

Addnessの「【7月7日まで】Fableで業務効率化させる はるきさんの記事」ゴールに、完成したAI資産を登録する。
**下のドラフトを私に見せて承認を取ってから書き込むこと。承認前にAddnessへの書き込み(DoD記入・成果物登録・完了化)は一切しない。**

## 背景

- 私(石山心太)は業務AI化プロジェクト中。リポジトリ **shinta1209/addness** / 作業ブランチ **claude/workflow-automation-strategy-3e1bib** に成果物がある(ローカル: /Users/shinta/Desktop/addnessタスク/addness)
- 完成済み: ①曲分析スキル(song-analysis+songs/6曲) ②SNS台本量産スキル(script-factory 3モード) ③docs/(業務マップ・自動化候補17案・引き継ぎ資料)
- 未完成: 受託ワークスキル(client-work)は叩き台のみ
- 詳しい経緯は `docs/04_引き継ぎプロンプト.md` を読むこと

## Addness側の現状(2026-07-04時点で確認済み)

- 親ゴール: 「【7月7日まで】Fableで業務効率化させる はるきさんの記事」
  ID: `3cc0713a-5192-42ae-9dc8-20648ab11a9a`(Status: NONE、**DoD未設定**、成果物ゼロ)
- 子ゴール:
  - 「コードとメロディ分析させて同じ技法が使われる曲を探してくるスキル作る」ID: `68a18370-f837-4ff4-81a1-76d3a3dfdf03` → **song-analysisで完成済み**
  - 「sns運用をfableで効率化する」ID: `2017215c-6310-449a-9729-8184591599b5` → **script-factoryで完成済み**(運用で育てるフェーズ)
  - 「受託案件をfableで効率化する」ID: `c8020db1-af5c-421f-829f-56b95c13cafb` → 未着手(叩き台のみ)。触らない

## 登録ドラフト(前スレッドで作成済み。まずこれを私に提示して承認を取る)

1. **親ゴールのDoD記入案**:
   > 音楽・SNS・受託の3業務それぞれについて、Fableで使えるAIスキル(リポジトリ shinta1209/addness の .claude/skills/ 配下)が完成し、実物でテストして本人が日常運用に使える状態になっていること。

2. **成果物リンク登録案(親ゴールに3件)**:
   - 「曲分析スキル+引き出し集6曲」→ https://github.com/shinta1209/addness/tree/claude/workflow-automation-strategy-3e1bib/.claude/skills/song-analysis と songs/
   - 「SNS台本量産スキル(3モード)」→ https://github.com/shinta1209/addness/tree/claude/workflow-automation-strategy-3e1bib/.claude/skills/script-factory
   - 「業務マップ・自動化候補17案・引き継ぎ資料」→ https://github.com/shinta1209/addness/tree/claude/workflow-automation-strategy-3e1bib/docs

3. **子ゴール2つの完了化**(それぞれDoDを書いてから完了):
   - 曲分析: DoD案「スキルに曲名を渡すとキー・コード進行(4段組)・技法を分析してsongs/に保存され、同じ技法の曲を逆引きできる」
   - SNS運用: DoD案「台本の翻訳(参考→自分用)、ストーリーの設計と整形、誘導施策のワークフローがスキル化され、運用開始できる状態」

## 注意

- 私が文面の修正を指示したら直してから実行。「完了化はまだ」と言ったらDoDと成果物だけ登録
- Addnessへのコメントを書く場合は末尾に署名(「Claude Codeより」等)
- マージするか(作業ブランチ→デフォルト)を聞かれたら、それは私の指示があった時のみ実行
