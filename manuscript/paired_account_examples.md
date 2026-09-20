# Paired account examples / 対応する口座例

**代表的な口座例。** 表に、EU27か国全体の2026年8月失業率を対象とする対応口座を示す。二値版の比較値6.1%は、保存された2026年7月の値である。点予測版には同じ値を参考情報として添付する。6.1は実験対象の回答例や将来の正解ではない。

| 項目 | 二値確率予測版 | 点予測版 |
|---|---|---|
| 問本文の抜粋 | EU27か国全体の2026年8月の季節調整済み失業率の初回公表値は、固定比較値6.1%を厳密に上回るか。YESの確率を提出せよ。 | EU27か国全体の2026年8月の季節調整済み失業率の初回公表値について、提供情報に条件付けた平均を%単位の数値で予測せよ。 |
| 提出値 | $p_{fq}\in[0,1]$ | $\widehat{x}_{fq}$（%単位、この系列では0〜100） |
| 参照系列 | `une_rt_m`、M、SA、TOTAL、T、PC_ACT、EU27_2020 | 同左 |
| 提供履歴 | 2024年8月〜2026年7月の24値 | 同じCSV |
| 提示／提出締切 | 2026年9月17日09:00／11:00 UTC | 同左 |
| 公表予定 | 2026年10月1日11:00 Europe/Luxembourg（09:00 UTC、暫定） | 同左 |
| 結果 | 初回公表値が6.1を上回れば1、それ以外は0 | 初回公表値そのもの |
| 採点 | 二乗確率誤差、方式内で平均Brier score | 二乗誤差を用い、総合NMSEの尺度は $s_q\approx0.080645$パーセントポイント |

表では読みやすさのため問い本文を短縮し、尺度を丸めて表示した。機械可読口座には全文・系列キー・未丸めの尺度を保存した。結果・回答・得点欄は全件未取得である。


**Representative paired accounts.** The table illustrates the first release of the EU27 unemployment rate for August 2026. The binary threshold of 6.1% is the archived July 2026 value, retained as context in the point bank. It is neither a subject's example response nor a future outcome.

| Field | Binary-probabilistic account | Point-forecast account |
|---|---|---|
| Question excerpt | Will the first published seasonally adjusted EU27 unemployment rate for August 2026 strictly exceed the fixed threshold of 6.1%? Submit P(YES). | Predict the conditional mean, given the supplied information, of the first published seasonally adjusted EU27 unemployment rate for August 2026, in percent. |
| Submission | $p_{fq}\in[0,1]$ | $\widehat{x}_{fq}$ in percent, bounded by 0–100 for this series |
| Series | `une_rt_m`, M, SA, TOTAL, T, PC_ACT, EU27_2020 | Same |
| Supplied history | 24 observations, August 2024–July 2026 | Identical CSV |
| Presentation / deadline | 17 September 2026, 09:00 / 11:00 UTC | Same |
| Scheduled release | 1 October 2026, 11:00 Europe/Luxembourg (09:00 UTC; tentative) | Same |
| Outcome | 1 if the first published value exceeds 6.1; otherwise 0 | The first published numerical value |
| Scoring | Squared probability error, aggregated as mean Brier score within format | Squared error; composite NMSE uses $s_q\approx0.080645$ percentage points |

Question text is abbreviated and the scale rounded for display. Full text, series keys, and the unrounded scale are stored in the machine-readable accounts. All outcome, response, and score fields remain unobserved.

